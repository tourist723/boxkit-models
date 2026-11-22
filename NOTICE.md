# BoxKit 离线语言包

这个仓库只放 BoxKit 用到的可选离线翻译模型权重（ONNX），源码在主仓库。

权重通过 [GitHub Releases](../../releases) 分发，每个 tag 是一个方向的包：

| tag | 方向 | 内容 |
|---|---|---|
| `ja-pack-v1` | 日 → 英 | OPUS-MT `opus-mt-ja-en`，int8 动态量化，约 217MB |

## 为什么单独一个仓库

主仓库是私有的，而私有仓库的 Release 资产下载需要带令牌。应用里匿名下载、
国内镜像代理转发都要求包放在公开仓库，所以权重单独放这里。

## 许可与署名（重要）

- 原始模型：[Helsinki-NLP/opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en)
- 许可证：**CC-BY-4.0**（允许再分发，需署名并注明改动）
- 本仓库的改动：用 `optimum-cli export onnx --task text2text-generation-with-past`
  导出为 fp32 ONNX，再用 onnxruntime 动态量化为 int8 权重（`QuantType.QInt8`），
  文件名按 BoxKit 引擎约定重命名（`encoder_model.onnx` → `encoder.onnx` 等）。
- 量化会带来轻微质量损失，属于格式转换，不是重新训练。

再分发时请保留本说明与 CC-BY-4.0 许可链接。

## 包内文件

| 文件 | 说明 |
|---|---|
| `ja-pack.json` | 清单：版本、方向、每个文件的字节数与 sha256 |
| `encoder.onnx` / `decoder.onnx` / `decoder_with_past.onnx` | Marian 三件套 |
| `source.spm` / `target.spm` | 源语言（日语）与目标语言（英语）分词器，两份不能合并 |
| `vocab.json` | piece → token id 映射，`<pad>`/`</s>` 也从这里取 |

`ja-pack.json` 里的 sha256 是安装时的唯一依据：应用会把文件先写成 `.part`，
校验通过才改名，所以半截文件不会被当成装好。
