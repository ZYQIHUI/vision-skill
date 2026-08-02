# Vision Skill 🖼️🧠

> 国产大模型生态的开源视觉层 —— 任意国产文本模型 + 视觉模型,一行命令接入。

一个即插即用 **Agent Skill**,把纯文本 LLM(GLM-5.2、DeepSeek、Qwen、GPT 等)与视觉模型桥接起来。默认供应商为**硅基流动(SiliconFlow)**,主用模型 **Qwen/Qwen3.5-4B**(原生视觉多模态,支持图像/视频/文本);亦可一键切回**智谱 GLM-4.6V-Flash**(永久免费)作为备用。遵循 Agent Skills 开放标准,兼容 Claude Code、Codex、Cursor、OpenCode 等所有支持 SKILL.md 的框架;框架不支持该标准时,脚本仍可作为普通 CLI 由调用方手动触发。

## 为什么需要它

很多强 LLM 是纯文本的——会推理但看不见图。本 skill 作为桥接:

```
用户图片 → [vision.py] → Qwen/Qwen3.5-4B (SiliconFlow)
                                ↓
                  结构化 JSON(场景图 + 推理链)
                                ↓
                  你的文本 LLM → 回答用户
```

文本 LLM 当"大脑"(推理、综合),视觉模型当"眼睛"(感知、描述)。

## 国产模型组合矩阵

本 skill 的核心价值:让国产文本模型生态拥有统一的视觉层。以下组合已验证可用:

| 文本 LLM(大脑)       | 视觉模型(眼睛)           | 成本      | 验证状态   |
| --------------------- | ------------------------ | --------- | ---------- |
| GLM-5.2               | Qwen/Qwen3.5-4B          | 免费      | ✅ verified |
| DeepSeek-V3           | Qwen/Qwen3.5-4B          | 免费      | ✅ verified |
| Qwen2.5-72B           | Qwen/Qwen3.5-4B          | 免费      | ⚠️ untested |
| GPT-4o (text)         | Qwen/Qwen3.5-4B          | 免费      | ⚠️ untested |
| Claude 3.5 (text)     | Qwen/Qwen3.5-4B          | 免费      | ⚠️ untested |

`verified` 表示已在真实环境跑通端到端链路(understand + query 全通过);`untested` 表示架构兼容但尚未在真实环境验证。如实标注,不给全绿假象——欢迎社区补测试报告。

## 特性

- **免费** —— 默认模型 Qwen/Qwen3.5-4B 在硅基流动**免费**(输入/输出 tokens 均免费)
- **多供应商** —— `VISION_PROVIDER` 一键切换:硅基流动(默认)/ 智谱(备用,GLM-4.6V-Flash 永久免费)
- **零依赖** —— 纯 Python 标准库,无需 pip install
- **跨框架** —— 任意 Agent Skills 兼容框架可用
- **深度理解** —— 场景图、空间推理、因果链、情感分析,不只是简单图说
- **事实复核** —— query 模式用于对关键论断二次求证,而非信息不足才追问
- **双模式** —— fast(单次调用 ~5-10s)、deep(串行多次 ~30-60s)

## 快速开始

### 1. 免费注册并获取 API key

注册 [cloud.siliconflow.cn](https://cloud.siliconflow.cn)(硅基流动),在"API 密钥"页创建 key。

### 2. 配置 API key 与模型(二选一)

**方式 A:环境变量(推荐 CI/服务端)**

```bash
export VISION_PROVIDER="siliconflow"        # 可选,默认即此
export SILICONFLOW_API_KEY="your-key-here"
export VISION_MODEL="Qwen/Qwen3.5-4B"        # 可选,默认即此
# 同步进 ~/.bashrc 或 ~/.zshrc 持久化
```

**方式 B:项目根目录 `.env` 文件(推荐本地开发)**

从模板复制并填入真实值(已被 `.gitignore` 忽略,不会误提交):

```bash
cp .env.example .env        # Windows: copy .env.example .env
# 然后编辑 .env:
#   VISION_PROVIDER=siliconflow        # 默认
#   SILICONFLOW_API_KEY=your-key-here  # 必填
#   VISION_MODEL=Qwen/Qwen3.5-4B       # 可选,默认即此
```

`.env` 支持 `#` 注释与可选引号(`KEY="value"`)。优先级:显式环境变量 > `.env` > 供应商默认值——两者都设时以环境变量为准。

### 3. 安装 skill

```bash
git clone https://github.com/ZYQIHUI/vision-skill.git
cd vision-skill
./install.sh
```

安装器自动检测已装 Agent 框架;检测到多个时让你确认,不悄悄挑第一个。

### 4. 使用

重启 Agent,然后:

> "帮我理解这张图片: /path/to/photo.jpg"

## 模型与费用

| 项                   | 默认值                                 |
| -------------------- | -------------------------------------- |
| 供应商               | 硅基流动 SiliconFlow                   |
| 模型                 | `Qwen/Qwen3.5-4B`(原生视觉多模态)      |
| 上下文               | 262,144 tokens                         |
| 图片输入             | 支持 URL 或 base64(≤10MB)              |

**费用**:Qwen/Qwen3.5-4B 在硅基流动**免费**——输入/输出 tokens 均不收费(控制台计费条目: `free-text-model.online.input-tokens` / `free-text-model.online.output-tokens`,即免费模型在线计费项)。仅受免费配额/限流约束。

同系列其他规模模型仍按量计费(元/百万 tokens),仅供参考:

| 模型               | 输入(元/M tokens) | 输出(元/M tokens) |
| ------------------ | ----------------- | ----------------- |
| Qwen3.5-397B-A17B  | 1.20              | 7.20              |
| Qwen3.5-122B-A10B  | 0.80              | 6.40              |
| Qwen3.5-35B-A3B    | 0.40              | 3.20              |
| Qwen3.5-27B        | 0.60              | 4.80              |
| **Qwen3.5-4B(默认)** | **免费**        | **免费**          |

> 免费额度与限流规则以 [cloud.siliconflow.cn](https://cloud.siliconflow.cn) 控制台实时展示为准。

**想用其他模型?** 可选:
- 切备用供应商: `.env` 中 `VISION_PROVIDER=zhipu` + `ZHIPU_API_KEY`,使用 **GLM-4.6V-Flash**(智谱永久免费,限 1 并发)
- 硅基流动其他多模态模型(OCR/翻译类): `VISION_MODEL=PaddlePaddle/PaddleOCR-VL-1.5` 或 `tencent/Hunyuan-MT-7B`

> 注意:硅基流动的 `Qwen/Qwen2.5-VL-*` 免费系列已于 2026-03/04 下线,勿再使用。

## 上游 LLM 接入要求

本 skill 在上游文本模型侧不引入任何 SDK 调用,LLM 是调用方而非被调用方。为避免 JSON 截断导致推理崩,上游 LLM 应满足:

| 要求              | 推荐           | 说明                                         |
| ----------------- | -------------- | -------------------------------------------- |
| 上下文长度        | ≥ 32K          | 容纳 understand 输出 JSON + 对话 + 工具结果   |
| tool 超时         | ≥ 90s          | deep 模式串行 6 次 VLM 调用约 30-60s,需留余量 |
| 工具结果解析       | 支持 JSON       | 脚本输出均为 JSON 到 stdout                  |

DeepSeek-V3 (128K)、GLM-5.2 (128K) 均无压力;8K 部署可能 JSON 截断后推理崩。

## 框架兼容性

| 框架                  | Skill 目录                   | 状态            |
| --------------------- | ---------------------------- | --------------- |
| Claude Code           | `~/.claude/skills/`          | ✅ verified      |
| Codex / Kun           | `~/.codex/skills/`           | ✅ verified      |
| Cursor                | `~/.agents/skills/`          | ⚠️ untested      |
| OpenCode              | `~/.config/opencode/skills/` | ⚠️ untested      |
| Any SKILL.md-compatible | varies                     | ✅ 标准格式      |

详见 [references/compatibility.md](references/compatibility.md)。

## 用法

```bash
# 深度理解(fast 模式,单次调用)
python scripts/vision.py understand --image "photo.jpg"

# 深度理解(deep 模式,串行多次)
python scripts/vision.py understand --image "photo.jpg" --mode deep

# 事实复核(query,针对关键论断求证)
python scripts/vision.py query --image "photo.jpg" --question "背景里有几个人?"

# 查看配置
python scripts/vision.py config
```

## 配置

方式一:**环境变量**;方式二:项目根目录 **`.env` 文件**(每行一个 `KEY=VALUE`,支持 `#` 注释)。显式环境变量优先于 `.env`,`.env` 优先于供应商默认值。

| 变量                  | 默认值                                 | 说明                   |
| --------------------- | -------------------------------------- | ---------------------- |
| `VISION_PROVIDER`     | `siliconflow`                          | 供应商: `siliconflow` / `zhipu` |
| `SILICONFLOW_API_KEY` | (必填,默认供应商)                      | cloud.siliconflow.cn 的 key |
| `ZHIPU_API_KEY`       | (切 zhipu 时必填)                      | open.bigmodel.cn 的 key |
| `VISION_MODEL`        | `Qwen/Qwen3.5-4B`(硅基流动) / `glm-4.6v-flash`(智谱) | 视觉模型,显式设置时覆盖供应商默认 |
| `VISION_API_BASE`     | `https://api.siliconflow.cn/v1`(硅基流动) / `https://open.bigmodel.cn/api/paas/v4`(智谱) | API 端点,显式设置时覆盖供应商默认 |
| `VISION_API_KEY`      | (空)                                   | 统一 key 覆盖,优先于供应商专属 key |
| `VISION_MAX_TOKENS`   | `20000`                                | 最大输出 token         |
| `VISION_TEMPERATURE`  | `0.2`                                  | 生成温度               |
| `VISION_TIMEOUT`      | `90`                                   | 请求超时(秒)          |
| `VISION_REQUEST_INTERVAL` | `2.0`                              | 两次 API 调用最小间隔(秒), 降低 429 限流触发 |

**换其他视觉后端(OpenAI 兼容)**: 设 `VISION_API_BASE` + `VISION_MODEL` + `VISION_API_KEY` 即可,零代码改动。示例:
> - 阿里百炼: `VISION_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1` + `VISION_MODEL=qwen-vl-max`
> - 自部署 Ollama: `VISION_API_BASE=http://<服务器IP>:11434/v1` + `VISION_MODEL=qwen2.5-vl:7b`

> **关于 429 限流**: 硅基流动按配额限流,智谱 GLM-4.6V-Flash 免费但限 1 并发。脚本已内置**请求节流**(两次调用间隔 ≥ `VISION_REQUEST_INTERVAL` 秒)与**智能重试**(尊重 `Retry-After` 头、指数退避 5s 起步封顶 60s)。连续手动测试时仍建议两次调用间稍留间隔。

> **关于思维链模型**: 部分视觉模型(Qwen3.5 系列等)默认输出超长思维链,可能吃光 `max_tokens` 预算导致 `answer` 为空。脚本对硅基流动已默认关闭思维链(`enable_thinking=false`,更快更省),understand 输出 JSON 解析失败会自动重试。

## 要求

- Python 3.8+
- 硅基流动 API key(默认)或智谱 API key(备用)
- 无需任何第三方 Python 包

## 边界声明

本 skill 是感知增强,不是视觉 ground truth。视觉模型对客观论断可能出现幻觉式描述——上游 LLM 应利用 query 模式对关键论断做事实复核,而非把 understand 结果直接当成可信观察。vision.py 只对接所选供应商的 VLM,不做多文本模型路由;文本模型是调用方,不引入文本推理分支。

## 贡献

欢迎贡献,尤其这些方向:
- **提示词工程** —— 优化 `assets/prompts.json`
- **多语言支持** —— 加英文 prompt 集合
- **新框架适配** —— 测试并补全 compatibility.md 的 verified 状态
- **边界场景** —— 改进错误处理

## License

MIT —— 见 [LICENSE](LICENSE)

## Acknowledgments

- [硅基流动](https://siliconflow.cn) 提供 Qwen/Qwen3.5-4B 等视觉模型
- [智谱 AI](https://open.bigmodel.cn) 提供 GLM-4.6V-Flash 免费模型
- [Anthropic](https://anthropic.com) 提出 Agent Skills 开放标准
