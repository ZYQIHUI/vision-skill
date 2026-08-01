# GLM Vision Skill 🖼️🧠

> 国产大模型生态的开源视觉层 —— 任意国产文本模型 + GLM 视觉模型,一行命令接入。

一个即插即用 **Agent Skill**,把纯文本 LLM(GLM-5.2、DeepSeek、Qwen、GPT 等)与 **GLM-4.6V-Flash** ——智谱永久免费视觉推理模型——桥接起来。遵循 Agent Skills 开放标准,兼容 Claude Code、Codex、Cursor、OpenCode 等所有支持 SKILL.md 的框架;框架不支持该标准时,脚本仍可作为普通 CLI 由调用方手动触发。

## 为什么需要它

很多强 LLM 是纯文本的——会推理但看不见图。本 skill 作为桥接:

```
用户图片 → [vision.py] → GLM-4.6V-Flash(免费 VLM)
                                ↓
                  结构化 JSON(场景图 + 推理链)
                                ↓
                  你的文本 LLM → 回答用户
```

文本 LLM 当"大脑"(推理、综合),GLM-4.6V-Flash 当"眼睛"(感知、描述)。

## 国产模型组合矩阵

本 skill 的核心价值:让国产文本模型生态拥有统一的视觉层。以下组合已验证可用:

| 文本 LLM(大脑)       | 视觉模型(眼睛)     | 全免费 | 验证状态   |
| --------------------- | -------------------- | ------ | ---------- |
| GLM-5.2               | GLM-4.6V-Flash       | ✅ 是  | ✅ verified |
| DeepSeek-V3           | GLM-4.6V-Flash       | ✅ 是  | ✅ verified |
| Qwen2.5-72B           | GLM-4.6V-Flash       | ✅ 是  | ⚠️ untested |
| GPT-4o (text)         | GLM-4.6V-Flash       | 部分   | ⚠️ untested |
| Claude 3.5 (text)     | GLM-4.6V-Flash       | 部分   | ⚠️ untested |

`verified` 表示已在真实环境跑通端到端链路;`untested` 表示架构兼容但尚未在真实环境验证。如实标注,不给全绿假象——欢迎社区补测试报告。

## 特性

- **零成本** —— GLM-4.6V-Flash 永久免费(限 1 并发)
- **零依赖** —— 纯 Python 标准库,无需 pip install
- **跨框架** —— 任意 Agent Skills 兼容框架可用
- **深度理解** —— 场景图、空间推理、因果链、情感分析,不只是简单图说
- **事实复核** —— query 模式用于对关键论断二次求证,而非信息不足才追问
- **双模式** —— fast(单次调用 ~5-10s)、deep(串行多次 ~30-60s)

## 快速开始

### 1. 免费获取 API key

注册 [open.bigmodel.cn](https://open.bigmodel.cn),创建 API key。

### 2. 配置 API key 与模型(二选一)

**方式 A:环境变量(推荐 CI/服务端)**

```bash
export ZHIPU_API_KEY="your-key-here"
export VISION_MODEL="glm-4.6v-flash"   # 可选,默认即此
# 同步进 ~/.bashrc 或 ~/.zshrc 持久化
```

**方式 B:项目根目录 `.env` 文件(推荐本地开发)**

从模板复制并填入真实值(已被 `.gitignore` 忽略,不会误提交):

```bash
cp .env.example .env        # Windows: copy .env.example .env
# 然后编辑 .env:
#   ZHIPU_API_KEY=your-key-here
#   VISION_MODEL=glm-4.6v-flash   # 可选,默认即此
```

`.env` 支持 `#` 注释与可选引号(`KEY="value"`)。优先级:显式环境变量 > `.env` > 默认值——两者都设时以环境变量为准。

### 3. 安装 skill

```bash
git clone https://github.com/ZYQIHUI/glm-vision-skill.git
cd glm-vision-skill
./install.sh
```

安装器自动检测已装 Agent 框架;检测到多个时让你确认,不悄悄挑第一个。

### 4. 使用

重启 Agent,然后:

> "帮我理解这张图片: /path/to/photo.jpg"

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

方式一:**环境变量**;方式二:项目根目录 **`.env` 文件**(`ZHIPU_API_KEY=xxx` / `VISION_MODEL=xxx` 每行一个,支持 `#` 注释)。显式环境变量优先于 `.env`。

| 变量                  | 默认值                                 | 说明                   |
| --------------------- | -------------------------------------- | ---------------------- |
| `ZHIPU_API_KEY`       | (必填)                                 | open.bigmodel.cn 的 key |
| `VISION_MODEL`        | `glm-4.6v-flash`                       | 视觉模型               |
| `VISION_API_BASE`     | `https://open.bigmodel.cn/api/paas/v4` | API 端点               |
| `VISION_MAX_TOKENS`   | `4096`                                 | 最大输出 token         |
| `VISION_TEMPERATURE`  | `0.2`                                  | 生成温度               |
| `VISION_TIMEOUT`      | `90`                                   | 请求超时(秒)          |
| `VISION_REQUEST_INTERVAL` | `2.0`                              | 两次 API 调用最小间隔(秒), 降低 429 限流触发 |

> **关于 429 限流**: GLM-4.6V-Flash 免费但限 1 并发且有分钟级频率额度。脚本已内置**请求节流**(两次调用间隔 ≥ `VISION_REQUEST_INTERVAL` 秒)与**智能重试**(尊重 `Retry-After` 头、指数退避 5s 起步封顶 60s)。连续手动测试时仍建议两次调用间稍留间隔。

## 要求

- Python 3.8+
- 免费智谱 API key
- 无需任何第三方 Python 包

## 边界声明

本 skill 是感知增强,不是视觉 ground truth。GLM-4.6V-Flash 对客观论断可能出现幻觉式描述——上游 LLM 应利用 query 模式对关键论断做事实复核,而非把 understand 结果直接当成可信观察。vision.py 永远只对接 GLM VLM,不做多文本模型路由;文本模型是调用方,不引入文本推理分支。

## 贡献

欢迎贡献,尤其这些方向:
- **提示词工程** —— 优化 `assets/prompts.json`
- **多语言支持** —— 加英文 prompt 集合
- **新框架适配** —— 测试并补全 compatibility.md 的 verified 状态
- **边界场景** —— 改进错误处理

提交 PR 前请先读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT —— 见 [LICENSE](LICENSE)

## Acknowledgments

- [智谱 AI](https://open.bigmodel.cn) 提供 GLM-4.6V-Flash 免费模型
- [Anthropic](https://anthropic.com) 提出 Agent Skills 开放标准
