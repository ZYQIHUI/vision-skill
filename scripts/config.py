#!/usr/bin/env python3
"""
Configuration manager for GLM Vision Skill.
All settings are controlled via environment variables with sensible defaults.
"""

import os
from pathlib import Path

# ============================================================
# .env File Loading — stdlib only (no python-dotenv)
# ============================================================
# 用户可在项目根目录放 .env 文件配置 API key 与模型:
#   ZHIPU_API_KEY=your-key
#   VISION_MODEL=glm-4.1v-thinking-flash
# 优先级: 显式环境变量 > .env 文件 > 硬编码默认值。
# 零第三方依赖, 解析规则: KEY=VALUE 每行, 支持 # 注释与可选引号。

def _find_dotenv() -> str:
    """定位 .env 文件: 项目根 → scripts 目录 → 当前工作目录"""
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / ".env",   # 项目根 (glm-vision-skill/.env)
        here / ".env",          # scripts 目录
        Path.cwd() / ".env",    # 当前工作目录
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return ""

def load_dotenv_file() -> None:
    """解析 .env 并写入环境变量; 已显式设置的环境变量不被覆盖"""
    path = _find_dotenv()
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # 去掉可选引号: KEY="value" 或 KEY='value'
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                os.environ.setdefault(key, value)

load_dotenv_file()

# ============================================================
# API Configuration
# ============================================================

# 智谱开放平台 API(免费注册: https://open.bigmodel.cn)
API_BASE = os.environ.get(
    "VISION_API_BASE",
    "https://open.bigmodel.cn/api/paas/v4"
)

# API Key — 从智谱开放平台获取
API_KEY = os.environ.get("ZHIPU_API_KEY", "")

# 视觉模型 — GLM-4.6V-Flash 永久免费, 128K上下文, 限1并发
# 可选替代:
#   glm-4.1v-thinking-flash  — 带思维链推理的视觉模型(也免费)
#   glm-4v-plus              — 付费增强版
VISION_MODEL = os.environ.get("VISION_MODEL", "glm-4.6v-flash")

# 生成参数
MAX_TOKENS = int(os.environ.get("VISION_MAX_TOKENS", "4096"))
TEMPERATURE = float(os.environ.get("VISION_TEMPERATURE", "0.2"))
REQUEST_TIMEOUT = int(os.environ.get("VISION_TIMEOUT", "90"))

# 请求最小间隔(秒) — 进程内节流, 降低免费模型 429 限流触发频率
# GLM-4.6V-Flash 限 1 并发且有分钟级频率额度, 连续快速请求易触发 429。
# 脚本保证两次 API 调用间隔 >= 此值; deep 模式 6 次串行调用自动受益。
REQUEST_INTERVAL = float(os.environ.get("VISION_REQUEST_INTERVAL", "2.0"))

# 图片限制(智谱 API 约束)
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_DIMENSION = 6000

# 支持的图片格式
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}


def validate_config() -> list:
    """验证配置是否完整, 返回错误信息列表"""
    errors = []
    if not API_KEY:
        errors.append(
            "ZHIPU_API_KEY is not set. "
            "Get a free key at https://open.bigmodel.cn"
        )
    if not API_BASE:
        errors.append("VISION_API_BASE is not set.")
    return errors


def get_config_summary() -> dict:
    """返回当前配置摘要(用于调试)"""
    return {
        "api_base": API_BASE,
        "model": VISION_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "api_key_set": bool(API_KEY),
        "api_key_preview": f"{API_KEY[:8]}..." if API_KEY else "NOT SET",
    }
