#!/usr/bin/env python3
"""Build the three BoxKit speech-model releases from upstream Hugging Face repos.

This script is run by .github/workflows/asr-packs.yml on a GitHub-hosted runner.
It does not train or re-quantize anything:
  - asr-lid   = Systran/faster-whisper-tiny (MIT), files copied as-is
  - asr-ja    = quantumcookie/anime-whisper-ct2-int8 (MIT, conversion of
                litagin/anime-whisper), files copied as-is
  - asr-multi = Systran/faster-whisper-large-v3 (MIT), files copied as-is;
                model.bin is split into <=1 GiB chunks because GitHub Releases
                cap a single asset at 2 GiB.

Every file/part gets a byte count and SHA-256. The app verifies each part,
concatenates them, then verifies the whole file before it is moved into place.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".asr-build"
DIST = ROOT / "dist" / "asr-packs"
CHUNK = 1024 * 1024 * 1024  # 1 GiB, safely below GitHub's 2 GiB asset cap

PACKS = [
    {
        "tag": "asr-lid-v1",
        "id": "asr-lid-pack",
        "name": "BoxKit 语音模型 · 语种检测 Whisper Tiny",
        "direction": "whisper-lid",
        "version": "1.0",
        "repo": "Systran/faster-whisper-tiny",
        "files": ["model.bin", "config.json", "tokenizer.json", "vocabulary.txt"],
        "license": "MIT",
        "upstream": "https://huggingface.co/Systran/faster-whisper-tiny",
        "notes": "Whisper Tiny (OpenAI, MIT). Copied as-is; no training, no re-quantization.",
    },
    {
        "tag": "asr-ja-v1",
        "id": "asr-ja-pack",
        "name": "BoxKit 语音模型 · 日语 Anime-Whisper",
        "direction": "whisper-ja",
        "version": "1.0",
        "repo": "quantumcookie/anime-whisper-ct2-int8",
        "files": [
            "model.bin", "config.json", "preprocessor_config.json", "tokenizer.json",
            "vocabulary.json", "added_tokens.json", "generation_config.json",
            "normalizer.json", "special_tokens_map.json", "tokenizer_config.json",
        ],
        "license": "MIT",
        "upstream": "https://huggingface.co/litagin/anime-whisper",
        "conversion": "https://huggingface.co/quantumcookie/anime-whisper-ct2-int8",
        "notes": (
            "Anime-Whisper by litagin (MIT), fine-tuned from kotoba-whisper-v2.0. "
            "The CTranslate2 int8 conversion is by quantumcookie. Files are copied "
            "as-is from that conversion; BoxKit does not train or re-quantize the model."
        ),
    },
    {
        "tag": "asr-multi-v1",
        "id": "asr-multi-pack",
        "name": "BoxKit 语音模型 · 英语/韩语/中文 Large-v3",
        "direction": "whisper-en",
        "version": "3.1",
        "repo": "Systran/faster-whisper-large-v3",
        "files": ["model.bin", "config.json", "preprocessor_config.json", "tokenizer.json", "vocabulary.json"],
        "split": "model.bin",
        "license": "MIT",
        "upstream": "https://huggingface.co/Systran/faster-whisper-large-v3",
        "notes": (
            "faster-whisper large-v3 (Systran conversion of OpenAI Whisper large-v3, MIT). "
            "Copied as-is. model.bin is split into <=1 GiB parts only to fit GitHub "
            "Release asset limits; the app concatenates and verifies the whole file."
        ),
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(repo: str, filename: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  cached {filename} ({dest.stat().st_size} B)", flush=True)
        return
    errors = []
    for base in ("https://huggingface.co", "https://hf-mirror.com"):
        url = f"{base}/{repo}/resolve/main/{filename}?download=true"
        part = dest.with_suffix(dest.suffix + ".part")
        part.unlink(missing_ok=True)
        try:
            print(f"  GET {url}", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "BoxKit-ASR-Pack-Builder/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                total = int(response.headers.get("content-length") or 0)
                done = 0
                last = 0.0
                with part.open("wb") as out:
                    while True:
                        block = response.read(8 * 1024 * 1024)
                        if not block:
                            break
                        out.write(block)
                        done += len(block)
                        now = time.time()
                        if now - last > 10:
                            last = now
                            pct = f"{done / total * 100:.1f}%" if total else "?"
                            print(f"    {pct} {done / 1048576:.0f} MiB", flush=True)
            if total and part.stat().st_size != total:
                raise RuntimeError(f"size mismatch: got {part.stat().st_size}, expected {total}")
            part.replace(dest)
            print(f"  done {filename} ({dest.stat().st_size} B)", flush=True)
            return
        except (urllib.error.URLError, RuntimeError, OSError) as exc:
            errors.append(f"{base}: {exc}")
            print(f"  failed: {errors[-1]}", flush=True)
            part.unlink(missing_ok=True)
    raise RuntimeError(f"cannot download {repo}/{filename}: {'; '.join(errors)}")


def split_file(src: Path, tag_dir: Path, part_prefix: str) -> list[dict]:
    parts = []
    with src.open("rb") as handle:
        index = 1
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            name = f"{part_prefix}.part{index:03d}"
            out_path = tag_dir / name
            with out_path.open("wb") as out:
                out.write(block)
            parts.append({
                "name": name,
                "bytes": out_path.stat().st_size,
                "sha256": sha256_file(out_path),
            })
            index += 1
    if not parts:
        raise RuntimeError(f"empty file: {src}")
    return parts


def build_pack(pack: dict) -> None:
    tag = pack["tag"]
    tag_dir = DIST / tag
    if tag_dir.exists():
        shutil.rmtree(tag_dir)
    tag_dir.mkdir(parents=True, exist_ok=True)
    src_dir = WORK / tag
    entries = []
    total = 0
    print(f"== {tag} ({pack['repo']})", flush=True)
    for filename in pack["files"]:
        src = src_dir / filename
        download(pack["repo"], filename, src)
        whole_bytes = src.stat().st_size
        whole_sha = sha256_file(src)
        entry = {"name": filename, "bytes": whole_bytes, "sha256": whole_sha}
        if pack.get("split") == filename:
            entry["parts"] = split_file(src, tag_dir, filename)
            print(f"  split {filename} -> {len(entry['parts'])} parts", flush=True)
        else:
            shutil.copy2(src, tag_dir / filename)
        entries.append(entry)
        total += whole_bytes

    manifest = {
        "id": pack["id"],
        "version": pack["version"],
        "name": pack["name"],
        "direction": pack["direction"],
        "license": pack["license"],
        "upstream": pack["upstream"],
        "conversion": pack.get("conversion", ""),
        "files": entries,
    }
    (tag_dir / f"{tag.replace('-v1', '')}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    notes = (
        f"{pack['name']}\n\n"
        f"- Upstream: {pack['upstream']}\n"
        + (f"- Conversion: {pack['conversion']}\n" if pack.get("conversion") else "")
        + f"- License: {pack['license']}\n\n"
        f"{pack['notes']}\n\n"
        "BoxKit only redistributes the converted weights and a checksum manifest. "
        "It is not affiliated with or endorsed by the upstream authors. "
        "See NOTICE.md in this repository for full attribution and modification notes. "
        "If you are a rights holder and believe this redistribution violates your terms, "
        "please open an issue and the asset will be removed after verification.\n"
    )
    (tag_dir / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    print(f"  manifest bytes={total} ({total / 1073741824:.2f} GiB)", flush=True)


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    for pack in PACKS:
        build_pack(pack)
    print("done; outputs in", DIST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
