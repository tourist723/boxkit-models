# 许可、署名与改动说明

本仓库分发的是**第三方模型的格式转换件**，不是我们训练的模型。版权归各上游作者；
本仓库只做「导出为 ONNX / int8 量化 / 按引擎约定改名」这类格式转换，并保留上游许可条款。
许可证全文在 [LICENSES/](LICENSES/)。

| Release tag | 方向 / 包类型 | 上游 | 许可 | 体积 |
|---|---|---|---|---|
| `zh-pack-v1` | 中 → 英（`zh_en`） | [Helsinki-NLP/opus-mt-zh-en](https://huggingface.co/Helsinki-NLP/opus-mt-zh-en) | CC-BY-4.0 | 226.8 MB |
| `en-pack-v1` | 英 → 中（`en_zh`） | [Helsinki-NLP/opus-mt-en-zh](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh) | Apache-2.0 | 226.8 MB |
| `ja-pack-v1` | 日 → 英（`ja_en`） | [Helsinki-NLP/opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en) | Apache-2.0 | 216.9 MB |
| `sense-pack-v1` | 语音识别（`sense-voice`） | [FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall) | FunASR 模型开源协议 v1.1 | 228.4 MB |

---

## 1. OPUS-MT 翻译权重（`zh-pack-v1` / `en-pack-v1` / `ja-pack-v1`）

**上游作者署名**：Helsinki-NLP —— University of Helsinki, Language Technology Research Group
（赫尔辛基大学语言技术研究组）。模型卡与论文：*OPUS-MT — Building open translation services
for the World*（Tiedemann & Thottingal, EAMT 2020）。

**许可**：

- `opus-mt-zh-en`：**CC-BY-4.0**，全文见 [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt)，
  许可页 <https://creativecommons.org/licenses/by/4.0/>。
- `opus-mt-en-zh`、`opus-mt-ja-en`：**Apache-2.0**，全文见
  [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)，
  许可页 <https://www.apache.org/licenses/LICENSE-2.0>。

**本仓库做的改动**（Apache-2.0 §4(b) / CC-BY-4.0 的「注明改动」要求）：

1. 用 `optimum-cli export onnx --task text2text-generation-with-past` 把上游 PyTorch 权重
   导出为 fp32 ONNX（Marian encoder / decoder / decoder_with_past 三件套）；
2. 用 onnxruntime `quantize_dynamic(..., weight_type=QuantType.QInt8)` 做动态 int8 量化，
   体积降到约 1/4，属于有损压缩（翻译质量有轻微下降），**不是重新训练**；
3. 按 BoxKit 引擎约定改名：`encoder_model.onnx` → `encoder.onnx`、
   `decoder_model.onnx` → `decoder.onnx`、`decoder_with_past_model.onnx` → `decoder_with_past.onnx`；
4. `vocab.json` 与 SentencePiece 分词器（`tokenizer.spm`，或日→英包的 `source.spm` + `target.spm`）
   原样取自上游模型仓库，未改动内容。

**没有包含**：上游的训练数据（OPUS 语料，由众多第三方语料库组成，各有各的条款）、
训练脚本、以及 Helsinki-NLP 的商标或标识。

**Apache-2.0 声明**：本仓库对这些包的再分发不附带任何额外保证；上游模型按「现状」提供，
不附带明示或默示担保。若你修改后再分发，请同样注明改动。

---

## 2. SenseVoice 语音识别权重（`sense-pack-v1`）

**上游作者署名**：阿里巴巴集团（Alibaba Group）通义实验室 / FunAudioLLM 团队的
**SenseVoice / SenseVoiceSmall**。项目地址 <https://github.com/FunAudioLLM/SenseVoice>。

**许可**：**FunASR 模型开源协议 v1.1**（FunASR Model Open Source License Agreement v1.1），
版权归 Alibaba Group，全文见
[LICENSES/FunASR-Model-License-1.1.txt](LICENSES/FunASR-Model-License-1.1.txt)，
原始地址 <https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE>。

> 注意：SenseVoice 的**仓库源码**是 MIT，但**模型权重**不是 MIT、也不是 Apache-2.0，
> 而是上述 FunASR 模型协议（HF 模型卡上标为 `other / model-license`）。
> 该协议允许使用、复制、修改与分享，条件是第 2.2 条：**注明出处与作者信息，并保留相关模型名称**。

**本仓库做的处理**：

1. 使用 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 项目（作者 csukuangfj）已导出的
   int8 ONNX 版本 `model.int8.onnx`，本仓库**原样分发，未再量化、未再训练**；
2. 附带上游同源的 `tokens.txt`（模型词表，供解码用）；
3. 保留模型名称：清单 `sense-pack.json` 的 `name` 为「SenseVoice 离线识别模型」、
   `engine` 为 `sense-voice-int8`，应用界面里该模型显示为「SenseVoice（字幕精解）」，
   文件与目录命名中亦保留 `sense-voice`。

**协议第 2.2 条落实方式**：出处（本仓库 + 上游链接）、作者（Alibaba Group / FunAudioLLM）、
模型名称（SenseVoice / SenseVoiceSmall）三者在清单、本文件与应用界面中均可见。

**没有包含**：训练数据、微调权重、SenseVoice 的商标或标识。

---

## 3. 清单文件与安装校验

每个 Release 带一个 `*.json` 清单（`zh-pack.json` / `en-pack.json` / `ja-pack.json` / `sense-pack.json`），
内容为版本、方向、每个文件的字节数与 sha256。清单与文档由本仓库以 **CC0-1.0** 提供。

应用安装时：先读清单 → 下载到 `.part` → 校验 sha256 → 通过才改名落地。
清单里的 sha256 是唯一依据，所以半截或被篡改的文件不会被当成「装好」。

## 4. 免责与下架

- 本仓库的转换件按「现状」提供，不附带任何担保；使用风险由使用者承担。
- 与上游组织无隶属关系、未获背书；`OPUS-MT`、`SenseVoice`、`FunASR` 等名称归各自所有者。
- 若你是权利人，认为某个包的分发方式不符合你的条款，请在本仓库开 issue 说明包名与理由，
  我们核实后会立即删除对应 Release 资产。
