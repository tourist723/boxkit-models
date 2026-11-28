# 许可、署名与改动说明

本仓库分发的是**第三方模型的格式转换件**，不是我们训练的模型。版权归各上游作者；
本仓库只做「导出为 ONNX / int8 量化 / 按引擎约定改名」这类格式转换，并保留上游许可条款。
许可证全文在 [LICENSES/](LICENSES/)。

| Release tag | 方向 / 包类型 | 上游 | 许可 | 体积 |
|---|---|---|---|---|
| `zh-pack-v1` | 中 → 英（`zh_en`） | [Helsinki-NLP/opus-mt-zh-en](https://huggingface.co/Helsinki-NLP/opus-mt-zh-en) | CC-BY-4.0 | 226.8 MB |
| `en-pack-v1` | 英 → 中（`en_zh`） | [Helsinki-NLP/opus-mt-en-zh](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh) | Apache-2.0 | 226.8 MB |
| `ja-pack-v1` | 日 → 英（`ja_en`） | [Helsinki-NLP/opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en) | Apache-2.0 | 216.9 MB |
| `ko-pack-v1` | 韩 → 英（`ko_en`） | [Helsinki-NLP/opus-mt-ko-en](https://huggingface.co/Helsinki-NLP/opus-mt-ko-en) | Apache-2.0 | 238.6 MB |
| `sense-pack-v1` | 语音识别（`sense-voice`） | [FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall) | FunASR 模型开源协议 v1.1 | 228.4 MB |
| `asr-lid-v1` | 字幕语种检测（`whisper-lid`） | [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny) | MIT | 74.6 MiB |
| `asr-ja-v1` | 日语字幕识别（`whisper-ja`） | [litagin/anime-whisper](https://huggingface.co/litagin/anime-whisper) → [quantumcookie/anime-whisper-ct2-int8](https://huggingface.co/quantumcookie/anime-whisper-ct2-int8) | MIT | 约 736 MiB |
| `asr-multi-v1` | 英/韩/中字幕识别（`whisper-en`） | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) | MIT | 约 2.88 GiB（`model.bin` 分 3 卷） |

---

## 1. OPUS-MT 翻译权重（`zh-pack-v1` / `en-pack-v1` / `ja-pack-v1` / `ko-pack-v1`）

**上游作者署名**：Helsinki-NLP —— University of Helsinki, Language Technology Research Group
（赫尔辛基大学语言技术研究组）。模型卡与论文：*OPUS-MT — Building open translation services
for the World*（Tiedemann & Thottingal, EAMT 2020）。

**许可**：

- `opus-mt-zh-en`：**CC-BY-4.0**，全文见 [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt)，
  许可页 <https://creativecommons.org/licenses/by/4.0/>。
- `opus-mt-en-zh`、`opus-mt-ja-en`、`opus-mt-ko-en`：**Apache-2.0**，全文见
  [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)，
  许可页 <https://www.apache.org/licenses/LICENSE-2.0>。

**本仓库做的改动**（Apache-2.0 §4(b) / CC-BY-4.0 的「注明改动」要求）：

1. 用 `optimum-cli export onnx --task text2text-generation-with-past` 把上游 PyTorch 权重
   导出为 fp32 ONNX（Marian encoder / decoder / decoder_with_past 三件套）；
2. 用 onnxruntime `quantize_dynamic(..., weight_type=QuantType.QInt8)` 做动态 int8 量化，
   体积降到约 1/4，属于有损压缩（翻译质量有轻微下降），**不是重新训练**；
3. 按 BoxKit 引擎约定改名：`encoder_model.onnx` → `encoder.onnx`、
   `decoder_model.onnx` → `decoder.onnx`、`decoder_with_past_model.onnx` →
   `decoder_with_past.onnx`；
4. `vocab.json` 与 SentencePiece 分词器（`tokenizer.spm`，或 `ja_en` / `ko_en` 包的
   `source.spm` + `target.spm`）原样取自上游模型仓库，未改动内容。

**`ko-pack-v1` 特别说明**：上游只有韩→英（`ko_en`）方向，**不存在** OPUS-MT 韩→中
直译包；应用内韩→中走「`ko_en` → `en_zh`」两跳，`en_zh` 为既有英→中包。本包不包含
训练数据（OPUS 语料，由众多第三方语料库组成，各有各的条款）、训练脚本、以及
Helsinki-NLP 的商标或标识。

**没有包含**：其余 OPUS-MT 包同样不含上游训练数据、训练脚本与 Helsinki-NLP 商标标识。

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
> 该协议允许使用、复制、修改与分享，条件是第 2.2 条：**注明出处与作者信息，并保留相关
> 模型名称**。

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

## 3. Whisper CTranslate2 权重（`asr-lid-v1` / `asr-ja-v1` / `asr-multi-v1`）

这三个包用于 BoxKit「翻译 → 引擎设置 → 语音模型」，都是 **CTranslate2** 格式，直接由
BoxKit 内置的 faster-whisper worker 加载，不需要额外运行时。本仓库对这三个包**没有
重新训练、没有重新量化、没有修改权重内容**；下列转换、分卷与清单都属于**分发层改动**，
不是模型层改动。

### 3.1 `asr-lid-v1` 语种检测 Tiny

- **上游**：[Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny)。
- **原始模型**：OpenAI **Whisper Tiny**（OpenAI 官方仓库 LICENSE 为 MIT）。
- **转换**：Systran 用 CTranslate2 把 `openai/whisper-tiny` 转为 CT2 FP16 格式。
- **许可**：MIT。
- **本仓库改动**：无。四个文件（`model.bin` / `config.json` / `tokenizer.json` /
  `vocabulary.txt`）原样复制，仅增加清单与逐文件 sha256。
- **用途**：只做整轨语种检测（LID），不承担整轨识别；应用不会把它当作日语/英语/韩语
  识别模型。

### 3.2 `asr-ja-v1` 日语 Anime-Whisper

- **上游作者**：**litagin**，模型 [litagin/anime-whisper](https://huggingface.co/litagin/anime-whisper)。
- **模型谱系**：以 `kotoba-tech/kotoba-whisper-v2.0`（Apache-2.0，`openai/whisper-large-v3`
  的蒸馏模型）为基座，在约 5,300 小时、373 万文件的日式动画/游戏语音数据集上微调。
- **CT2 int8 转换**：**quantumcookie**，
  [quantumcookie/anime-whisper-ct2-int8](https://huggingface.co/quantumcookie/anime-whisper-ct2-int8)。
- **许可**：MIT（上游模型卡与转换件模型卡均标注 `license: mit`）。
- **本仓库做的处理**：
  1. 从 `quantumcookie/anime-whisper-ct2-int8` **原样复制** 10 个文件（`model.bin`、
     `config.json`、`preprocessor_config.json`、`tokenizer.json`、`vocabulary.json`、
     `added_tokens.json`、`generation_config.json`、`normalizer.json`、
     `special_tokens_map.json`、`tokenizer_config.json`）；
  2. **没有重新训练、没有重新量化、没有修改权重**；
  3. 仅增加 `asr-ja.json` 清单与逐文件 sha256。
- **没有包含**：训练数据集（`litagin/Galgame_Speech_ASR_16kHz`、
  `OOPPEENN/Galgame_Dataset`）、训练脚本、上游商标或标识。
- **内容提示**：上游模型在含成人向游戏语音的数据集中微调，识别结果可能包含成人向用语；
  该模型面向日语动画/游戏语音场景，不保证适用于其他领域。未成年人不应使用。

### 3.3 `asr-multi-v1` 英语 / 韩语 / 中文 Large-v3

- **上游**：[Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3)。
- **原始模型**：OpenAI **Whisper large-v3**（OpenAI 官方仓库 LICENSE 为 MIT，支持多语种，
  含英语、韩语、中文）。
- **转换**：Systran 用 `ct2-transformers-converter` 转为 CT2 FP16 格式。
- **许可**：MIT。
- **本仓库做的处理**：
  1. 五个文件（`model.bin` / `config.json` / `preprocessor_config.json` /
     `tokenizer.json` / `vocabulary.json`）取自上游；
  2. 由于 `model.bin` 为 3,087,284,237 字节，超过 GitHub Release 单资产 2 GiB 上限，
     按 **1 GiB** 切成 3 卷（`model.bin.part001` ~ `part003`）。这是**容器分卷，不是模型
     量化或重新训练**；应用下载后按卷序拼接回原文件，并校验整文件 sha256；
  3. 未修改权重内容；仅增加 `asr-multi.json` 清单、每卷与整文件的 `bytes` / `sha256`。
- **没有包含**：OpenAI 的训练数据、训练脚本、Systran 或 OpenAI 的商标或标识。

### 3.4 MIT 版权说明

上游仓库的模型卡均标注 `license: mit`，但这些仓库未单独附带版权文件。本仓库按 MIT
全文分发，版权归各自上游作者：

- Whisper 原始权重：**OpenAI**（OpenAI/whisper 仓库 LICENSE：Copyright (c) 2022 OpenAI）；
- faster-whisper 的 CTranslate2 转换件：**Systran**；
- Anime-Whisper 微调权重：**litagin**；
- Anime-Whisper 的 CT2 int8 转换件：**quantumcookie**。

如果上游后续提供更具体的版权声明，以对应上游仓库的 `LICENSE` / 模型卡为准。MIT 全文见
[LICENSES/MIT.txt](LICENSES/MIT.txt)。

---

## 4. 清单文件与安装校验

每个 Release 带一个 `*.json` 清单（`zh-pack.json` / `en-pack.json` / `ja-pack.json` /
`ko-pack.json` / `sense-pack.json` / `asr-lid.json` / `asr-ja.json` / `asr-multi.json`），
内容为版本、方向、每个文件的字节数与 sha256；分卷包还包含每卷的 `name` / `bytes` / `sha256`。
清单与文档由本仓库以 **CC0-1.0** 提供；根目录 `LICENSE`（CC0-1.0）不覆盖模型权重。

应用安装时：先读清单 → 下载到 `.part` → 校验 sha256 → 通过才改名落地。分卷包逐卷校验，
全部到齐后按顺序拼接，再对整文件校验 sha256；任何一卷损坏都会重下该卷，不会把半截文件
当成「装好」。

## 5. 免责与下架

- 本仓库的转换件与副本按「现状」提供，不附带任何明示或默示担保；使用风险由使用者承担。
- 与上游组织无隶属关系、未获背书；`OpenAI`、`Whisper`、`Systran`、`faster-whisper`、
  `Anime-Whisper`、`CTranslate2`、`OPUS-MT`、`SenseVoice`、`FunASR` 等名称归各自所有者。
- 本仓库不包含训练数据；不授予任何商标、专利或肖像权许可；不保证模型输出可用于法律、
  医疗、金融等专业场景。
- **下架条款与联系方式**：若你是权利人，认为某个包的分发方式不符合你的条款，请在
  [boxkit-models 仓库](https://github.com/tourist723/boxkit-models) 开 issue，说明**包名、
  具体文件与理由**；我们核实后会立即删除对应 Release 资产，并在 README / NOTICE 中记录
  下架情况。在核实完成前，相关资产保持现状；核实成立后不再保留副本。

---

## 6. Errata / 已知标注勘误

早期四个旧 Release 的**说明文字（Release notes）**存在许可标注笔误。该笔误只涉及说明文字，
**模型权重本身始终按下列正确许可分发**，清单与权重文件未因此改动。以下逐条勘误，许可归属
以本节、第 1 / 2 节及上游模型卡为准。

| Release | notes 原标注（有误） | 正确许可 | 出处 / 依据 |
|---|---|---|---|
| `en-pack-v1` | CC-BY-4.0 | **Apache-2.0** | [Helsinki-NLP/opus-mt-en-zh](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh)，HF 模型卡 `license: apache-2.0`；全文见 [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt) |
| `ja-pack-v1` | CC-BY-4.0 | **Apache-2.0** | [Helsinki-NLP/opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en)，HF 模型卡 `license: apache-2.0`；全文见 [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt) |
| `sense-pack-v1` | Apache-2.0 | **FunASR 模型开源协议 v1.1**（FunASR Model Open Source License Agreement v1.1） | [FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall)，HF 模型卡 `license: other / model-license`；全文见 [LICENSES/FunASR-Model-License-1.1.txt](LICENSES/FunASR-Model-License-1.1.txt) |

补充说明：

- `zh-pack-v1` 标注 CC-BY-4.0 与实际一致，不在勘误之列。
- 旧 Release 的 notes 受工具限制无法回填改写；如对许可归属有疑问，以本 NOTICE、上游模型卡与
  `LICENSES/` 许可证全文为准。
- 权重分发未受该笔误影响：en / ja 包权重按 Apache-2.0 条款保留版权与许可声明并注明改动；
  sense 包权重按 FunASR 协议第 2.2 条注明出处与作者、保留模型名称。
