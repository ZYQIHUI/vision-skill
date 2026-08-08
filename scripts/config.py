#!/usr/bin/env python3
"""
Configuration manager for Vision Skill.
All settings are controlled via environment variables with sensible defaults.
Supports multiple vision API providers (Agnes / SiliconFlow / Zhipu / custom via overrides).
"""

import os
from pathlib import Path

# ============================================================
# Version
# ============================================================

__version__ = "2.1.0"

# ============================================================
# .env File Loading — stdlib only (no python-dotenv)
# ============================================================
# 用户可在项目根目录放 .env 文件配置 API key 与模型:
#   AGNES_API_KEY=your-key          # Agnes AI (默认供应商, 免费全模态)
#   SILICONFLOW_API_KEY=your-key    # 硅基流动 (备用)
#   ZHIPU_API_KEY=your-key          # 智谱 (备用)
#   VISION_PROVIDER=agnes           # 供应商切换 (agnes | siliconflow | zhipu)
#   VISION_MODEL=agnes-2.5-flash    # 模型覆盖
# 优先级: 显式环境变量 > .env 文件 > 供应商预设默认值。
# 零第三方依赖, 解析规则: KEY=VALUE 每行, 支持 # 注释与可选引号。

def _find_dotenv() -> str:
    """定位 .env 文件: 项目根 → scripts 目录 → 当前工作目录"""
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / ".env",   # 项目根 (vision-skill/.env)
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
# Provider Registry — 供应商预设
# ============================================================
# 每个供应商: API 端点、API key 环境变量名、默认模型、图片限制。
# 视觉请求统一走 OpenAI 兼容 /chat/completions 格式, 换供应商只换端点+key+模型。

PROVIDERS = {
    "agnes": {
        "label": "Agnes AI (AgnesAI-Labs)",
        "home": "https://agnes-ai.com",
        "api_base": "https://apihub.agnes-ai.com/v1",
        "key_env": "AGNES_API_KEY",
        # 主用视觉模型: agnes-2.5-flash 为文本+视觉语言模型 (image_url 输入),
        # 512K 上下文 / 65.5K 输出, 当前输入输出均 $0/1M tokens (限时免费)。
        # key 获取: https://platform.agnes-ai.com 注册后创建。
        # 免费档 20 RPM (实际), 20 次/分钟 ≈ 3 秒/请求, 脚本内置 2s 节流已基本覆盖。
        # 用 VISION_MODEL 覆盖为其他模型 ID: agnes-2.0-flash / agnes-1.5-flash 等。
        "default_model": "agnes-2.5-flash",
        "max_image_size_mb": 10,
        "max_image_dimension": 4096,  # 文档未公布明确上限, 保守取 4096
        "concurrent_requests": 1,
    },
    "siliconflow": {
        "label": "硅基流动 (SiliconFlow)",
        "home": "https://cloud.siliconflow.cn",
        "api_base": "https://api.siliconflow.cn/v1",
        "key_env": "SILICONFLOW_API_KEY",
        # 主用视觉模型: Qwen/Qwen3.5-4B 为原生视觉多模态 (image-text-to-text),
        # 小尺寸低成本; 注意 Qwen/Qwen2.5-VL-* 免费系列已于 2026-03/04 下线。
        # 用 VISION_MODEL 覆盖为任意模型 ID:
        #   Qwen/Qwen3.5-35B-A3B  (¥0.4/M 输入, 通用 VL)
        #   Qwen/Qwen3-VL-32B-Instruct / zai-org/GLM-4.5V 等
        "default_model": "Qwen/Qwen3.5-4B",
        "max_image_size_mb": 10,
        "max_image_dimension": 3584,  # Qwen 系 VL 最大支持 3584x3584
        "concurrent_requests": None,  # 硅基流动无固定 1 并发限制
    },
    "zhipu": {
        "label": "智谱开放平台 (Zhipu BigModel)",
        "home": "https://open.bigmodel.cn",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "key_env": "ZHIPU_API_KEY",
        "default_model": "glm-4.6v-flash",  # 永久免费, 128K 上下文, 限 1 并发
        "max_image_size_mb": 5,
        "max_image_dimension": 6000,
        "concurrent_requests": 1,
    },
}

# ============================================================
# Active Configuration — 显式环境变量 > 供应商预设
# ============================================================

# 供应商选择: VISION_PROVIDER=agnes|siliconflow|zhipu (默认 agnes, 以 Agnes AI 为主)
VISION_PROVIDER = os.environ.get("VISION_PROVIDER", "agnes").strip().lower()
CONFIG_ERRORS: list = []  # 模块加载期的非致命配置错误, validate_config() 会合并上报
if VISION_PROVIDER not in PROVIDERS:
    CONFIG_ERRORS.append(
        f"Unknown VISION_PROVIDER={VISION_PROVIDER!r}. "
        f"Supported: {', '.join(sorted(PROVIDERS))}. "
        "Or set VISION_API_BASE + VISION_API_KEY for a custom OpenAI-compatible endpoint."
    )
    VISION_PROVIDER = "agnes"  # 回退到默认供应商, 保证其余配置可加载
_PROVIDER = PROVIDERS[VISION_PROVIDER]

# API 端点 — 显式 VISION_API_BASE 优先, 否则用供应商预设
API_BASE = os.environ.get("VISION_API_BASE", _PROVIDER["api_base"])

# API Key — 读取优先级: VISION_API_KEY > 供应商专属 key 环境变量
API_KEY = (
    os.environ.get("VISION_API_KEY")
    or os.environ.get(_PROVIDER["key_env"])
    or ""
)
API_KEY_ENV = "VISION_API_KEY" if os.environ.get("VISION_API_KEY") else _PROVIDER["key_env"]

# 视觉模型 — 显式 VISION_MODEL 优先, 否则用供应商默认
VISION_MODEL = os.environ.get("VISION_MODEL", _PROVIDER["default_model"])

# 生成参数
MAX_TOKENS = int(os.environ.get("VISION_MAX_TOKENS", "20000"))
TEMPERATURE = float(os.environ.get("VISION_TEMPERATURE", "0.2"))
REQUEST_TIMEOUT = int(os.environ.get("VISION_TIMEOUT", "90"))

# 请求最小间隔(秒) — 进程内节流, 降低免费模型 429 限流触发频率
# 脚本保证两次 API 调用间隔 >= 此值; deep 模式 6 次串行调用自动受益。
REQUEST_INTERVAL = float(os.environ.get("VISION_REQUEST_INTERVAL", "2.0"))

# 图片限制(按供应商)
MAX_IMAGE_SIZE_MB = _PROVIDER["max_image_size_mb"]
MAX_IMAGE_DIMENSION = _PROVIDER["max_image_dimension"]

# 并发限制(按供应商; None 表示无固定限制)
CONCURRENT_REQUESTS = _PROVIDER.get("concurrent_requests")

# 支持的图片格式
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}


def validate_config() -> list:
    """验证配置是否完整, 返回错误信息列表"""
    errors = list(CONFIG_ERRORS)
    if not API_KEY:
        errors.append(
            f"{API_KEY_ENV} is not set for provider {VISION_PROVIDER} "
            f"({_PROVIDER['label']}). Get a key at {_PROVIDER['home']} "
            f"and set it in .env or as an environment variable."
        )
    if not API_BASE:
        errors.append("VISION_API_BASE is not set.")
    return errors


def get_config_summary() -> dict:
    """返回当前配置摘要(用于调试)"""
    return {
        "version": __version__,
        "provider": VISION_PROVIDER,
        "provider_label": _PROVIDER["label"],
        "api_base": API_BASE,
        "model": VISION_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "api_key_env": API_KEY_ENV,
        "api_key_set": bool(API_KEY),
        "api_key_preview": f"{API_KEY[:8]}..." if API_KEY else "NOT SET",
    }

if __name__ == "__main__":
    print(get_config_summary())
