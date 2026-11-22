# boxkit-models

BoxKit 的可选离线模型包：翻译权重（OPUS-MT / Marian ONNX）与语音识别权重（SenseVoice）。
本仓库只放**权重与清单**，应用源码在主仓库。

**维护者**：BoxKit 项目（[@tourist723](https://github.com/tourist723)）。

> 本仓库与 University of Helsinki / Helsinki-NLP、阿里巴巴集团 / FunAudioLLM、sherpa-onnx
> 均**无隶属关系，也未获其背书**。模型权重的版权归各上游作者所有，本仓库只做格式转换与分发；
> 各模型名称是其各自所有者的商标或项目名，仅用于说明来源。

## 包含哪些包

| Release tag | 用途 | 上游模型 | 上游许可 | 体积 |
|---|---|---|---|---|
| `zh-pack-v1` | 离线翻译 中 → 英 | `Helsinki-NLP/opus-mt-zh-en` | CC-BY-4.0 | 约 227 MB |
| `en-pack-v1` | 离线翻译 英 → 中 | `Helsinki-NLP/opus-mt-en-zh` | Apache-2.0 | 约 227 MB |
| `ja-pack-v1` | 离线翻译 日 → 英（再经 `en_zh` 两跳转中文） | `Helsinki-NLP/opus-mt-ja-en` | Apache-2.0 | 约 217 MB |
| `sense-pack-v1` | 离线语音识别（视频「生成字幕」逐段识别） | `FunAudioLLM/SenseVoiceSmall` | FunASR 模型开源协议 v1.1 | 约 228 MB |

每个 Release 除权重外都带一个 `*.json` 清单，逐文件列出字节数与 sha256；
应用只认清单里的 sha256，先写 `.part`、校验通过才改名。

## 应用怎么用

BoxKit「翻译 → 引擎设置」里有两处入口：

- **离线翻译包**（一张卡，方向芯片可单独装）：`zh_en` / `en_zh` / `ja_en`；
- **识别模型**：`sense-voice`。

点「一键安装」会拉清单 → 逐文件下载 → 校验 sha256 → 落到模型目录，支持断点续传与取消。
国内直连 GitHub 常常不通，应用按 `gh-proxy.com` → `ghproxy.net` 的顺序自动换镜像。

清单地址可用环境变量覆盖（内网镜像 / 自建分发 / 测试）：

```
BOXKIT_PACK_MANIFEST_ZH_EN / _EN_ZH / _JA_EN / _SENSE_VOICE
BOXKIT_JA_PACK_MIRRORS        # 逗号分隔的镜像前缀，空字符串表示不用镜像
```

## 许可

| 内容 | 许可 |
|---|---|
| 本仓库的清单（`*.json`）与文档（`README.md` / `NOTICE.md`） | CC0-1.0（公有领域贡献），随意使用 |
| `zh-pack-v1` 权重 | CC-BY-4.0（需署名 + 注明改动） |
| `en-pack-v1` / `ja-pack-v1` 权重 | Apache-2.0（需保留版权与许可声明、注明改动） |
| `sense-pack-v1` 权重 | FunASR 模型开源协议 v1.1（需注明出处与作者、保留模型名称） |

**权重不是我们的版权**，本仓库不改变其许可，也不能替上游授权。逐包的上游链接、作者署名与
改动说明见 [NOTICE.md](NOTICE.md)；许可证全文见 [LICENSES/](LICENSES/)。

商用或再分发前，请自行核对上游条款与你所在法域的要求。若你是权利人并认为本仓库的分发方式
不当，请开 issue，我们会在核实后立即下架相关资产。
