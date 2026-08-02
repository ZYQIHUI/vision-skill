---
name: vision-skill
description: >
  国产大模型生态的视觉层 / Visual layer for Chinese LLM ecosystem.
  为纯文本 AI 模型提供深度图像理解能力 / Deep visual understanding for text-only models.
  通过硅基流动 Qwen/Qwen3.5-4B 视觉多模态模型桥接(可切换智谱 GLM-4.6V-Flash),支持场景图、空间推理、上下文分析、情感解读、因果推理链、追问查询 / Bridges text-only LLMs (GLM-5.2, DeepSeek, Qwen, GPT) with visual understanding via SiliconFlow Qwen/Qwen3.5-4B (or Zhipu GLM-4.6V-Flash): scene graphs, spatial reasoning, contextual analysis, emotional interpretation, causal reasoning chains, follow-up visual queries.
  当用户提供图片(路径或 URL)并要求理解、分析、描述、识别、推理、提取文字、回答关于图片的问题时触发 / Activate when the user provides an image (file path or URL) and asks to understand, analyze, describe, recognize, reason about, or extract text from it.
  兼容任何遵循 Agent Skills 开放标准的框架 / Works with any Agent framework following the Agent Skills open standard.
license: MIT
version: 2.0.0
---

# Vision Skill

为纯文本语言模型提供深度图像理解能力,默认通过硅基流动 Qwen/Qwen3.5-4B 桥接(可切智谱 GLM-4.6V-Flash)。
Provides deep image understanding for text-only language models via SiliconFlow Qwen/Qwen3.5-4B by default (Zhipu GLM-4.6V-Flash as backup).

## When to Use / 何时使用

当以下任一情况发生时激活本 skill / Activate when:
- 用户提供图片路径或 URL,询问其内容 / User provides an image path or URL and asks about its content
- 用户问"发生了什么"、"为什么"、"这是什么意思" / User asks "what's happening", "why", "what does it mean"
- 用户需要空间推理(左/右、上/下、近/远) / Spatial reasoning (left/right, above/below, near/far)
- 用户需要上下文、情感或因果分析 / Contextual, emotional, or causal analysis
- 用户对先前分析过的图片追问 / Follow-up questions about a previously analyzed image
- 当前模型无法直接处理图像 / The current model cannot process images directly

## Execution / 执行

### Phase 1: Deep Understanding / 深度理解

运行理解脚本,提取结构化表示 / Run the understanding script to extract a structured representation:

```bash
python scripts/vision.py understand --image "IMAGE_PATH_OR_URL" [--mode MODE]
```

Modes / 模式:
- `fast` (default / 默认): 单次综合调用。一次返回场景图 + 描述 + 文字 + 推理的 JSON。快速,约 5-10 秒。 / Single comprehensive call.  Returns scene graph + description + text + reasoning in one JSON.  ~5-10s.
- `deep`: 串行多次分析。分别提取场景图、空间布局、OCR、上下文、情感、推理链。更慢但更详细,约 30-60 秒。 / Sequential multi-call analysis.  More detailed but slower.  Extracts scene graph, spatial layout, OCR, context, emotion, reasoning chain separately.  ~30-60s.

读取 JSON 输出,将其作为你的视觉上下文内化 / Read the JSON output and internalize it as your visual context.

### Phase 2: 事实复核 — Follow-up Queries / 事实复核 — 追问查询

对 understand 结果中需核实的关键论断,用 query 做二次求证,而非仅在信息不足时补刀。
For key claims from the understanding that need verification, use query to cross-check rather than only when information is missing.

```bash
python scripts/vision.py query --image "IMAGE_PATH_OR_URL" --question "YOUR_QUESTION"
```

适用于此类定向问题 / Use for targeted questions like:
- "背景里有几个人?" / "How many people are in the background?"
- "狗的项圈是什么颜色?" / "What color is the dog's collar?"
- "这个人比门高吗?" / "Is the person taller than the door?"

### Phase 3: Synthesize / 综合

将结构化理解和复核结果综合,向用户展示你的推理过程。
Combine the structured understanding and verification results to form your answer.
Show your reasoning process to the user.

## Configuration / 配置

脚本从当前供应商的环境变量读取 API 密钥,支持两种配置方式(显式环境变量优先于 `.env`):
The script reads the API key from the selected provider's env var, via environment variable or a `.env` file (explicit env vars take precedence):

**供应商切换 / Provider switching** — `VISION_PROVIDER=siliconflow|zhipu`(默认 `siliconflow`, 以硅基流动为主):

1. **硅基流动 / SiliconFlow** (默认, key 获取: https://cloud.siliconflow.cn)
   ```bash
   export VISION_PROVIDER="siliconflow"
   export SILICONFLOW_API_KEY="your-key"
   # VISION_MODEL=Qwen/Qwen3.5-4B   (默认, 原生视觉多模态)
   ```
   注意: 硅基流动的 `Qwen/Qwen2.5-VL-*` 免费系列已于 2026-03/04 下线; 当前免费多模态仅 OCR/翻译类 (`PaddlePaddle/PaddleOCR-VL-1.5`、`tencent/Hunyuan-MT-7B`)。其他 VL 模型 ID 可在 https://cloud.siliconflow.cn 模型广场查询。

2. **智谱开放平台 / Zhipu BigModel** (备用, 免费获取 key: https://open.bigmodel.cn)
   ```bash
   export VISION_PROVIDER="zhipu"
   export ZHIPU_API_KEY="your-key"
   # VISION_MODEL=glm-4.6v-flash   (默认, 永久免费)
   ```

3. **自定义 OpenAI 兼容端点 / Custom endpoint**: 显式设置 `VISION_API_BASE` + `VISION_API_KEY`(或供应商专属 key)可接任意兼容服务。

Optional environment variables / 可选环境变量:
- `VISION_PROVIDER`: 供应商 (`siliconflow` 默认 / `zhipu`) / Provider selector
- `VISION_API_KEY`: 统一 key 覆盖, 优先于供应商专属 key / Unified API key override
- `VISION_MODEL`: 覆盖视觉模型(默认按供应商: 硅基流动 `Qwen/Qwen3.5-4B`, 智谱 `glm-4.6v-flash`) / Override vision model
- `VISION_API_BASE`: 覆盖 API 端点(默认按供应商预设) / Override API endpoint
- `VISION_MAX_TOKENS`: 覆盖最大输出 token(默认: 20000) / Override max output tokens (default: 20000)
- `VISION_REQUEST_INTERVAL`: 两次 API 调用最小间隔秒数(默认: 2.0), 降低 429 限流 / Min interval between API calls in seconds (default: 2.0), reduces 429 rate limits

## Notes / 注意

- 智谱 GLM-4.6V-Flash 免费但限 1 并发 / Zhipu GLM-4.6V-Flash is free but limited to 1 concurrent request
- 硅基流动按配额限流, 超限返回 429 (响应体含 `Request was rejected due to rate limiting`) / SiliconFlow is quota-limited; 429 responses indicate rate limiting
- 部分视觉模型(Qwen3.5 系列等)默认输出思维链, 脚本对硅基流动已默认关闭 (`enable_thinking=false`, 更快更省); understand JSON 解析失败自动重试 / Reasoning models are handled with enable_thinking=false on SiliconFlow for speed & stability; understand retries on JSON parse failure
- 脚本内置请求节流 + 429 智能重试(指数退避, 尊重 Retry-After); 仍建议连续手动调用间稍留间隔 / Built-in throttling + smart 429 retry (exponential backoff, honors Retry-After); still keep a small gap between manual calls
- 支持 JPG, PNG, WEBP, BMP, GIF, TIFF(按供应商: 硅基流动 10MB/3584px, 智谱 5MB/6000px)
- API 兼容 OpenAI 格式 / OpenAI-compatible API format
- 输出始终为 JSON 到 stdout,便于可靠解析 / Output is always JSON to stdout for reliable parsing
