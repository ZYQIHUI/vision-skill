---
name: glm-vision
description: >
  国产大模型生态的视觉层 / Visual layer for Chinese LLM ecosystem.
  为纯文本 AI 模型提供深度图像理解能力 / Deep visual understanding for text-only models.
  通过 GLM-4.6V-Flash 视觉推理模型桥接,支持场景图、空间推理、上下文分析、情感解读、因果推理链、追问查询 / Bridges text-only LLMs (GLM-5.2, DeepSeek, Qwen, GPT) with visual understanding via GLM-4.6V-Flash: scene graphs, spatial reasoning, contextual analysis, emotional interpretation, causal reasoning chains, follow-up visual queries.
  当用户提供图片(路径或 URL)并要求理解、分析、描述、识别、推理、提取文字、回答关于图片的问题时触发 / Activate when the user provides an image (file path or URL) and asks to understand, analyze, describe, recognize, reason about, or extract text from it.
  兼容任何遵循 Agent Skills 开放标准的框架 / Works with any Agent framework following the Agent Skills open standard.
license: MIT
---

# GLM Vision Skill

为纯文本语言模型提供深度图像理解能力,通过 GLM-4.6V-Flash 桥接。
Provides deep image understanding for text-only language models via GLM-4.6V-Flash.

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

脚本从 `ZHIPU_API_KEY` 读取 API 密钥,支持两种配置方式(显式环境变量优先于 `.env`):
The script reads the API key from `ZHIPU_API_KEY`, via environment variable or a `.env` file (explicit env vars take precedence):

1. **环境变量** / **Environment variable**: `export ZHIPU_API_KEY="your-key"`
2. **`.env` 文件** / **`.env` file**: 在项目根目录创建 `.env`,写 `ZHIPU_API_KEY=your-key`(每行一个,支持 `#` 注释)

在 https://open.bigmodel.cn 免费获取。
Get a free key at https://open.bigmodel.cn

Optional environment variables / 可选环境变量:
- `VISION_MODEL`: 覆盖视觉模型(默认: glm-4.6v-flash) / Override vision model (default: glm-4.6v-flash)
- `VISION_API_BASE`: 覆盖 API 端点 / Override API endpoint
- `VISION_MAX_TOKENS`: 覆盖最大输出 token(默认: 4096) / Override max output tokens (default: 4096)
- `VISION_REQUEST_INTERVAL`: 两次 API 调用最小间隔秒数(默认: 2.0), 降低 429 限流 / Min interval between API calls in seconds (default: 2.0), reduces 429 rate limits

## Notes / 注意

- GLM-4.6V-Flash 免费但限 1 并发 / Free with 1 concurrent request limit
- 脚本内置请求节流 + 429 智能重试(指数退避, 尊重 Retry-After); 仍建议连续手动调用间稍留间隔 / Built-in throttling + smart 429 retry (exponential backoff, honors Retry-After); still keep a small gap between manual calls
- 支持 JPG, PNG, WEBP, BMP, GIF, TIFF(最大 5MB, 6000x6000px)
- API 兼容 OpenAI 格式(https://open.bigmodel.cn/api/paas/v4)
- 输出始终为 JSON 到 stdout,便于可靠解析 / Output is always JSON to stdout for reliable parsing
