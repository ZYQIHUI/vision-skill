# 使用示例 — Vision Skill

## 示例 1: 快速理解一张照片

```bash
python scripts/vision.py understand --image "photo.jpg"
```

输出 JSON 包含场景图、空间布局、文字提取、内容描述、上下文推断、情感分析、推理链。

## 示例 2: 深度分析(多维度)

```bash
python scripts/vision.py understand --image "photo.jpg" --mode deep
```

串行 6 次 API 调用,每个维度获得独立、更详细的分析。约 30-60 秒。

## 示例 3: 事实复核

```bash
python scripts/vision.py query --image "photo.jpg" --question "背景里有几个人?"
```

对 understand 结果中的关键论断做二次求证,而非仅在信息不足时追问。

## 示例 4: 使用 URL

```bash
python scripts/vision.py understand --image "https://example.com/photo.jpg"
```

支持 HTTP/HTTPS 图片 URL,无需下载。

## 示例 5: 查看配置

```bash
python scripts/vision.py config
```

检查 API key 是否设置、当前模型、限制参数等。

## 示例 6: 用 .env 配置 key 与模型

在项目根目录创建 `.env`(已被 `.gitignore` 忽略,可 `cp .env.example .env`):

```bash
VISION_PROVIDER=siliconflow
SILICONFLOW_API_KEY=your-key-here
VISION_MODEL=Qwen/Qwen3.5-4B   # 可选,默认即此(硅基流动,免费)
```

然后直接运行,无需 export:

```bash
python scripts/vision.py config        # 应显示 provider=siliconflow, model=Qwen/Qwen3.5-4B
python scripts/vision.py understand --image "photo.jpg"
```

显式设置的环境变量优先于 `.env`,两者都设时以环境变量为准。

## 示例 7: 切换备用供应商(智谱)

```bash
VISION_PROVIDER=zhipu
ZHIPU_API_KEY=your-key-here
# VISION_MODEL=glm-4.6v-flash   # 可选,默认即此(永久免费)
```
