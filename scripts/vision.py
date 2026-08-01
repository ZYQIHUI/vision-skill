#!/usr/bin/env python3
"""
GLM Vision Skill — Bridge text-only LLMs with visual understanding.

Usage:
    python vision.py understand --image "photo.jpg" [--mode fast|deep]
    python vision.py query --image "photo.jpg" --question "What color is the car?"
    python vision.py config

Requires:
    - Python 3.8+
    - ZHIPU_API_KEY environment variable (free: https://open.bigmodel.cn)
    - No third-party packages required (uses only stdlib)
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    API_BASE, API_KEY, VISION_MODEL,
    MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT, REQUEST_INTERVAL,
    MAX_IMAGE_SIZE_MB, MAX_IMAGE_DIMENSION, SUPPORTED_FORMATS,
    validate_config, get_config_summary,
)

# ============================================================
# Prompt Loading
# ============================================================

def load_prompts() -> dict:
    """从 assets/prompts.json 加载提示词模板"""
    possible_paths = [
        Path(__file__).parent.parent / "assets" / "prompts.json",
        Path(__file__).parent / "assets" / "prompts.json",
        Path.cwd() / "assets" / "prompts.json",
    ]
    for p in possible_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {
        "fast_comprehensive": {
            "prompt": "请全面分析这张图片,返回JSON格式:包含场景图(对象、属性、关系)、空间布局、文字提取、内容描述、上下文推断、情感分析、推理链。只返回有效 JSON。"
        },
        "query": {
            "template": "精确回答关于图片的问题:{question}。只基于可见内容,明确区分观察与推断,无法确定时直说不要编造。"
        },
    }

# ============================================================
# Image Utilities
# ============================================================

def is_url(path: str) -> bool:
    return path.startswith(("http://", "https://"))

def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 扩展名 → MIME 类型 (data URL 前缀用, 不同 VLM 后端对 MIME 校验严格度不同)
MIME_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp",
    ".bmp": "image/bmp", ".gif": "image/gif",
    ".tiff": "image/tiff",
}

def mime_for(image_path: str) -> str:
    return MIME_MAP.get(Path(image_path).suffix.lower(), "image/jpeg")

def validate_image(image_path: str) -> None:
    if is_url(image_path):
        return
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(f"Image size {size_mb:.1f}MB exceeds {MAX_IMAGE_SIZE_MB}MB limit.")
    ext = Path(image_path).suffix.lower()
    if ext and ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}")

def prepare_image_input(image_path: str) -> str:
    """返回可直接放进 OpenAI 兼容请求的 image_url 值:
    URL 原样返回; 本地图片返回带真实 MIME 的 data URL。
    """
    validate_image(image_path)
    if is_url(image_path):
        return image_path
    return f"data:{mime_for(image_path)};base64,{image_to_base64(image_path)}"

# ============================================================
# Request Throttling — 降低免费模型 429 触发频率
# ============================================================

_last_request_time = [0.0]  # 进程内节流状态 (list 以便闭包修改)


def _throttle() -> None:
    """保证两次 API 调用间隔 >= REQUEST_INTERVAL 秒。
    GLM-4.6V-Flash 限 1 并发且有分钟级频率额度, 无间隔连发(尤其 deep 模式
    6 次串行调用)极易触发 429; 在真正发请求前补齐间隔, 从源头降频。
    """
    now = time.monotonic()
    need = REQUEST_INTERVAL - (now - _last_request_time[0])
    if need > 0:
        time.sleep(need)
    _last_request_time[0] = time.monotonic()


def _retry_wait(attempt: int, error_message: str) -> int:
    """计算 429 重试等待秒数: 尊重服务器 Retry-After 头, 否则指数退避。
    退避: 5s * 2^attempt, 封顶 60s (5/10/20/40/60)。
    """
    m = re.search(r"Retry-After[:=]?\s*(\d+)", error_message)
    if m:
        return min(int(m.group(1)), 60)
    return min(5 * (2 ** attempt), 60)


# ============================================================
# API Client
# ============================================================

def call_vision_api(image_input, prompt, max_tokens=None, temperature=None) -> str:
    errors = validate_config()
    if errors:
        raise RuntimeError("; ".join(errors))
    _throttle()  # 发请求前节流

    if is_url(image_input):
        image_url = image_input
    else:
        # 已是带真实 MIME 的 data URL (prepare_image_input 组装)
        image_url = image_input

    payload = {
        "model": VISION_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
        "max_tokens": max_tokens or MAX_TOKENS,
        "temperature": temperature if temperature is not None else TEMPERATURE,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions", data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        if e.code == 429:
            retry_after = e.headers.get("Retry-After") if e.headers else None
            hint = f" Retry-After: {retry_after}s." if retry_after else ""
            raise RuntimeError(
                f"Rate limit hit (429).{hint} GLM-4.6V-Flash allows 1 concurrent request. Wait and retry."
            )
        elif e.code == 401:
            raise RuntimeError("Authentication failed (401). Check your ZHIPU_API_KEY.")
        else:
            raise RuntimeError(f"API error {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse API response: {e}")

def call_vision_with_retry(image_input, prompt, max_retries=3, **kwargs) -> str:
    last_error = None
    for attempt in range(max_retries):
        try:
            return call_vision_api(image_input, prompt, **kwargs)
        except RuntimeError as e:
            last_error = e
            if "429" in str(e) or "Rate limit" in str(e):
                wait = _retry_wait(attempt, str(e))
                print(f"[Retry {attempt+1}/{max_retries}] Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
    raise last_error

# ============================================================
# JSON Parsing Utility — 加 parse_failed 降级
# ============================================================

def parse_json_response(raw: str) -> dict:
    """
    尝试从模型响应中解析 JSON。
    解析成功 → {"parsed": True, "data": {...}}
    解析失败 → {"parsed": False, "parse_failed": True, "raw_response": raw}

    国产模型常在 JSON 外加"好的,这是分析结果:"这类中文前缀,
    或不严格遵守 schema。兜底返回 raw_response + parse_failed=True,
    让上游中文 LLM 自己消化原始文本——它读自然语言比读残缺 JSON 更稳,
    且 parse_failed 字段让调用方能区分"结构化可用"和"需重新理解"。
    """
    text = raw.strip()
    # 去除 markdown 代码块标记
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines)
        if lines[-1].strip() == "```":
            end = -1
        text = "\n".join(lines[start:end])
    # 截取首个 { 到末尾 }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace + 1]
    try:
        return {"parsed": True, "data": json.loads(text)}
    except json.JSONDecodeError:
        return {"parsed": False, "parse_failed": True, "raw_response": raw}

# ============================================================
# Understand Command
# ============================================================

def cmd_understand(args):
    prompts = load_prompts()
    image_input = prepare_image_input(args.image)

    if args.mode == "fast":
        fc = prompts.get("fast_comprehensive", {})
        prompt = fc.get("prompt", "")
        few_shot = fc.get("few_shot")
        if few_shot and few_shot.get("example_output"):
            prompt = (
                "参考以下例答格式(仅作格式参考,内容据实际图片填写):\n"
                + json.dumps(few_shot["example_output"], ensure_ascii=False, indent=2)
                + "\n\n" + prompt
            )
        raw = call_vision_with_retry(image_input, prompt, max_tokens=4096, temperature=0.2)
        result = {
            "success": True,
            "mode": "fast",
            "image": args.image,
            "model": VISION_MODEL,
            "understanding": parse_json_response(raw),
            "hint": "如 understanding.parsed 为 False,建议改用 --mode deep 单维度分析",
        }

    elif args.mode == "deep":
        tasks = [
            ("scene_graph", "scene_graph", 1024, 0.1),
            ("spatial_layout", "spatial", 768, 0.2),
            ("extracted_text", "text_ocr", 512, 0.1),
            ("contextual_analysis", "context", 1024, 0.3),
            ("emotional_atmosphere", "emotion", 768, 0.3),
            ("reasoning_chain", "reasoning", 1024, 0.3),
        ]
        layers = {}
        for field_name, prompt_key, tokens, temp in tasks:
            print(f"[Deep] Extracting {field_name}...", file=sys.stderr)
            prompt = prompts[prompt_key]["prompt"]
            raw = call_vision_with_retry(image_input, prompt, max_tokens=tokens, temperature=temp)
            if field_name == "scene_graph":
                layers[field_name] = parse_json_response(raw)
            else:
                layers[field_name] = raw.strip()

        result = {
            "success": True,
            "mode": "deep",
            "image": args.image,
            "model": VISION_MODEL,
            "layer1_visual_extraction": {
                "scene_graph": layers.get("scene_graph", {}),
                "spatial_layout": layers.get("spatial_layout", ""),
                "extracted_text": layers.get("extracted_text", ""),
            },
            "layer2_semantic_understanding": {
                "contextual_analysis": layers.get("contextual_analysis", ""),
                "emotional_atmosphere": layers.get("emotional_atmosphere", ""),
                "reasoning_chain": layers.get("reasoning_chain", ""),
            },
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))

# ============================================================
# Query Command — 事实复核通道,而非补刀
# ============================================================

def cmd_query(args):
    prompts = load_prompts()
    image_input = prepare_image_input(args.image)
    template = prompts["query"]["template"]
    prompt = template.replace("{question}", args.question)
    raw = call_vision_with_retry(image_input, prompt, max_tokens=512, temperature=0.1)
    result = {
        "success": True,
        "image": args.image,
        "question": args.question,
        "answer": raw.strip(),
        "model": VISION_MODEL,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

# ============================================================
# Config Command
# ============================================================

def cmd_config(args):
    summary = get_config_summary()
    errors = validate_config()
    output = {
        "config": summary,
        "valid": len(errors) == 0,
        "errors": errors if errors else None,
        "supported_formats": sorted(SUPPORTED_FORMATS),
        "limits": {"max_image_size_mb": MAX_IMAGE_SIZE_MB, "max_image_dimension": MAX_IMAGE_DIMENSION, "concurrent_requests": 1},
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

# ============================================================
# CLI Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        prog="vision.py",
        description="GLM Vision Skill — Visual understanding for text-only LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vision.py understand --image "photo.jpg"
  python vision.py understand --image "photo.jpg" --mode deep
  python vision.py query --image "photo.jpg" --question "How many people?"
  python vision.py config
        """,
    )
    sub = parser.add_subparsers(dest="command")
    pu = sub.add_parser("understand", help="Deep image understanding")
    pu.add_argument("--image", required=True, help="Image path or URL")
    pu.add_argument("--mode", default="fast", choices=["fast", "deep"])
    pq = sub.add_parser("query", help="Cross-check a key claim about an image")
    pq.add_argument("--image", required=True, help="Image path or URL")
    pq.add_argument("--question", required=True, help="Question to cross-check")
    sub.add_parser("config", help="Show current configuration")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    try:
        {"understand": cmd_understand, "query": cmd_query, "config": cmd_config}[args.command](args)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
    except KeyboardInterrupt:
        print(json.dumps({"success": False, "error": "Interrupted by user"}))
        sys.exit(130)

if __name__ == "__main__":
    main()
