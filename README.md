# boxkit-models

BoxKit 的可选离线模型包：翻译权重（OPUS-MT / Marian ONNX）、语音识别权重（SenseVoice）
与语音模型（Whisper / CTranslate2）。

本仓库只放**权重、清单与安装说明**，应用源码在主仓库
[tourist723/boxkit](https://github.com/tourist723/boxkit)。

**维护者**：BoxKit 项目（[@tourist723](https://github.com/tourist723)）。

> 本仓库与 OpenAI、Systran、litagin、quantumcookie、University of Helsinki / Helsinki-NLP、
> 阿里巴巴集团 / FunAudioLLM、sherpa-onnx 均**无隶属关系，也未获其背书**。
> 模型权重的版权归各上游作者所有，本仓库只做格式转换、分卷与分发；
> 各模型名称是其各自所有者的商标或项目名，仅用于说明来源。

## 包含哪些包

| Release tag | 用途 | 上游模型 | 上游许可 | 体积 |
|---|---|---|---|---|
| `zh-pack-v1` | 离线翻译 中 → 英 | `Helsinki-NLP/opus-mt-zh-en` | CC-BY-4.0 | 约 227 MB |
| `en-pack-v1` | 离线翻译 英 → 中 | `Helsinki-NLP/opus-mt-en-zh` | Apache-2.0 | 约 227 MB |
| `ja-pack-v1` | 离线翻译 日 → 英（再经 `en_zh` 两跳转中文） | `Helsinki-NLP/opus-mt-ja-en` | Apache-2.0 | 约 217 MB |
| `sense-pack-v1` | 旧版语音识别（SenseVoice，保留给旧安装） | `FunAudioLLM/SenseVoiceSmall` | FunASR 模型开源协议 v1.1 | 约 228 MB |
| `asr-lid-v1` | 字幕语种检测（Whisper Tiny） | `Systran/faster-whisper-tiny` | MIT | 4 个权重文件，约 72 MiB |
| `asr-ja-v1` | 字幕识别 日语（Anime-Whisper，CT2 int8） | `litagin/anime-whisper`（CT2 int8 转换件 `quantumcookie/anime-whisper-ct2-int8`） | MIT | 10 个权重文件，约 736 MiB |
| `asr-multi-v1` | 字幕识别 英语 / 韩语 / 中文（Large-v3） | `Systran/faster-whisper-large-v3` | MIT | 4 个配置/词表文件 + `model.bin` 分 3 卷，约 2.88 GiB |

每个 Release 除权重外都带一个 `*.json` 清单，逐文件列出字节数与 sha256；
应用只认清单里的 sha256，先写 `.part`、校验通过才改名。
`asr-multi-v1` 的 `model.bin` 为 3,087,284,237 字节，超过 GitHub Release 单资产 2 GiB
上限，因此按 1 GiB 分卷（`model.bin.part001` ~ `part003`）；清单里每一卷也有独立的
`bytes` 与 `sha256`，并保留整文件的 `bytes` / `sha256`，应用下载后按卷序拼接回原文件，
再校验整文件 sha256，通过后才上线。

## 应用怎么用

BoxKit「翻译 → 引擎设置」里有两处入口：

- **离线翻译包**（一张卡，方向芯片可单独装）：`zh_en` / `en_zh` / `ja_en`；
- **识别模型**：`sense-voice`。

「翻译 → 引擎设置 → **语音模型**」里另有三张 Whisper 模型卡，按语言选择，不再把
Tiny / large-v3 / Kotoba 混在一起：

- **日语 Anime-Whisper**（`asr-ja-v1`）：日语视频优先使用；
- **英语 / 韩语 / 中文 Large-v3**（`asr-multi-v1`）：三种语言共用一套多语种权重；
- **自动判语种 Whisper Tiny**（`asr-lid-v1`）：只做语种检测，不单独承担整轨识别。

点「一键安装」会拉清单 → 逐文件（或逐卷）下载 → 校验 sha256 → 落到模型目录，
支持断点续传与取消；分卷全部到齐后按顺序拼成整文件，再校验整文件 sha256，
通过后才改名上线。国内直连 GitHub 常常不通，应用按 `gh-proxy.com` → `ghproxy.net`
的顺序自动换镜像。

清单地址可用环境变量覆盖（内网镜像 / 自建分发 / 测试）：

```text
BOXKIT_PACK_MANIFEST_ZH_EN / _EN_ZH / _JA_EN / _SENSE_VOICE
BOXKIT_ASR_MANIFEST_JA / _MULTI / _LID
BOXKIT_JA_PACK_MIRRORS        # 逗号分隔的镜像前缀，空字符串表示不用镜像
```

旧版 `whisper-ja`（Kotoba）与 `whisper-en`（large-v3）目录会被新版按文件字节数和
sha256 重新识别；Anime-Whisper 与旧 Kotoba 的文件集不同，安装时会覆盖同名文件，
不会把旧目录误判为已就绪。

## 许可

| 内容 | 许可 |
|---|---|
| 本仓库的清单（`*.json`）、构建脚本与文档（`README.md` / `NOTICE.md`） | CC0-1.0（公有领域贡献），随意使用 |
| `zh-pack-v1` 权重 | CC-BY-4.0（需署名 + 注明改动） |
| `en-pack-v1` / `ja-pack-v1` 权重 | Apache-2.0（需保留版权与许可声明、注明改动） |
| `sense-pack-v1` 权重 | FunASR 模型开源协议 v1.1（需注明出处与作者、保留模型名称） |
| `asr-lid-v1` / `asr-ja-v1` / `asr-multi-v1` 权重 | MIT（保留版权与许可声明） |

**关于根目录 `LICENSE`**：仓库根的 `LICENSE`（CC0-1.0）只覆盖 BoxKit 自有的脚本、
文档与清单（`*.json`）；**不覆盖任何模型权重**。模型权重按其上游许可分发，本仓库
不改变其许可，也不能替上游授权。逐包的上游链接、作者署名与改动说明见
[NOTICE.md](NOTICE.md)；许可证全文见 [LICENSES/](LICENSES/)，其中 MIT 全文见
[LICENSES/MIT.txt](LICENSES/MIT.txt)。

商用或再分发前，请自行核对上游条款与你所在法域的要求。若你是权利人并认为本仓库的
distribution 方式不当，请在本仓库开 issue，说明包名、具体文件与理由；我们核实后会立即下架
相关资产，并在 README / NOTICE 中记录下架情况。
