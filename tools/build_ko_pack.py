#!/usr/bin/env python3
"""Build the ko-pack-v1 offline translate pack on a GitHub Actions runner.

Upstream: Helsinki-NLP/opus-mt-ko-en (Apache-2.0; Helsinki-NLP, University of
Helsinki Language Technology Research Group). BoxKit does not train or
re-quantize the model weights: the pack is the upstream PyTorch weights
converted to ONNX, dynamically quantized to int8, renamed to the engine's
filenames, plus a checksum manifest.

Pipeline mirrors the existing zh/en/ja translate packs:
  1. download upstream weights + tokenizer/config files (HF mirror fallback)
  2. optimum-cli export onnx --task text2text-generation-with-past (fp32)
  3. onnxruntime dynamic int8 quantization (QuantType.QInt8) of the three graphs
  4. rename to engine filenames, write manifest (bytes + sha256) and notes

Outputs land in dist/ko-pack-v1/; the workflow then creates the ko-pack-v1
Release and uploads every asset with gh release upload --clobber.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".ko-build"
DIST = ROOT / "dist" / "ko-pack-v1"

REPO = "Helsinki-NLP/opus-mt-ko-en"
UPSTREAM_URL = "https://huggingface.co/Helsinki-NLP/opus-mt-ko-en"
LICENSE = "Apache-2.0"

# Upstream files pulled for the local export.
UPSTREAM_FILES = [
    "pytorch_model.bin", "source.spm", "target.spm", "vocab.json",
    "config.json", "generation_config.json", "tokenizer_config.json",
]

# optimum export output -> engine filename.
EXPORT_TO_ENGINE = {
    "encoder_model.onnx": "encoder.onnx",
    "decoder_model.onnx": "decoder.onnx",
    "decoder_with_past_model.onnx": "decoder_with_past.onnx",
}

# Release order in the manifest (encoder/decoder/past, vocab, split spm).
PACK_FILES = [
    "encoder.onnx", "decoder.onnx", "decoder_with_past.onnx",
    "vocab.json", "source.spm", "target.spm",
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
            req = urllib.request.Request(
                url, headers={"User-Agent": "BoxKit-Pack-Builder/1.0"})
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


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("  $ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None)


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)

    model_dir = WORK / "model"
    onnx_dir = WORK / "onnx"
    model_dir.mkdir(parents=True, exist_ok=True)
    onnx_dir.mkdir(parents=True, exist_ok=True)

    # 1. Upstream weights + tokenizer/config.
    print(f"== fetch upstream {REPO}", flush=True)
    for filename in UPSTREAM_FILES:
        download(REPO, filename, model_dir / filename)

    # 2. Export ONNX (fp32) with optimum.
    print("== optimum ONNX export (fp32)", flush=True)
    run([
        "optimum-cli", "export", "onnx",
        "--model", str(model_dir),
        "--task", "text2text-generation-with-past",
        "--dtype", "fp32",
        str(onnx_dir),
    ])

    # 3. Dynamic int8 quantization of the three encoder/decoder graphs.
    print("== dynamic int8 quantization", flush=True)
    from onnxruntime.quantization import quantize_dynamic, QuantType

    for exported, engine_name in EXPORT_TO_ENGINE.items():
        src = None
        for candidate in (onnx_dir / exported, onnx_dir / "encoder" / exported):
            if candidate.is_file():
                src = candidate
                break
        if src is None:
            raise RuntimeError(f"exported ONNX not found: {exported} in {onnx_dir}")
        dst = DIST / engine_name
        quantize_dynamic(str(src), str(dst), weight_type=QuantType.QInt8)
        print(f"  {exported} -> {engine_name} ({dst.stat().st_size} B)", flush=True)

    # 4. Tokenizer / vocab copied unchanged from upstream.
    for name in ("source.spm", "target.spm", "vocab.json"):
        shutil.copy2(model_dir / name, DIST / name)

    # 5. Manifest with per-file bytes + sha256.
    entries = []
    total = 0
    for name in PACK_FILES:
        path = DIST / name
        if not path.is_file():
            raise RuntimeError(f"pack file missing after build: {name}")
        entries.append({
            "name": name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
        total += path.stat().st_size

    manifest = {
        "id": "ko-pack",
        "name": "BoxKit 离线翻译包 · 韩→英（两跳）",
        "version": "1.0.0",
        "direction": "ko_en",
        "kind": "translate",
        "engine": "opus-mt-ko-en",
        "license": LICENSE,
        "source": REPO,
        "tokenizer": "split",
        "totalBytes": total,
        "files": entries,
    }
    (DIST / "ko-pack.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    notes = (
        "BoxKit 离线翻译包 · 韩→英（经英语两跳转中文）\n\n"
        f"- Upstream: {UPSTREAM_URL}\n"
        f"- License: {LICENSE}\n\n"
        "BoxKit 仅做格式分发：PyTorch 权重导出为 ONNX、动态 int8 权重量化、按引擎约定"
        "改名；未重新训练、未修改权重内容。模型权重版权归上游 Helsinki-NLP"
        "（University of Helsinki, Language Technology Research Group）所有。\n\n"
        "本包与上游作者无隶属关系、未获其背书；OPUS-MT 名称归其各自所有者。"
        "若你是权利人并认为本次再分发不符合条款，请在 boxkit-models 仓库开 issue，"
        "说明包名、具体文件与理由；核实后对应资产将被下架。详见仓库 NOTICE.md。\n"
    )
    (DIST / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")

    print(f"  manifest bytes={total} ({total / 1048576:.1f} MiB)", flush=True)
    print("done; outputs in", DIST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
