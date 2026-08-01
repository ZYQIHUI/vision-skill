#!/usr/bin/env python3
"""
基础测试 — GLM Vision Skill
运行: python tests/test_vision.py
需要设置 ZHIPU_API_KEY 才能跑 API 相关测试。
"""

import json
import os
import sys
import subprocess

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
VISION_PY = os.path.join(SCRIPT_DIR, "vision.py")
PYTHON = sys.executable


def test_config_command():
    """测试 config 子命令输出合法 JSON"""
    result = subprocess.run(
        [PYTHON, VISION_PY, "config"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"config exited {result.returncode}"
    data = json.loads(result.stdout)
    assert "config" in data
    assert "valid" in data
    print("✅ test_config_command passed")


def test_missing_image():
    """测试不存在的图片路径返回错误"""
    result = subprocess.run(
        [PYTHON, VISION_PY, "understand", "--image", "nonexistent.jpg"],
        capture_output=True, text=True, timeout=10,
    )
    data = json.loads(result.stdout)
    assert data["success"] is False
    assert "not found" in data["error"].lower()
    print("✅ test_missing_image passed")


def test_parse_json_response():
    """测试 JSON 解析容错"""
    sys.path.insert(0, SCRIPT_DIR)
    from vision import parse_json_response

    # 正常 JSON
    r = parse_json_response('{"a": 1}')
    assert r["parsed"] is True
    assert r["data"]["a"] == 1

    # 带 markdown 代码块
    r = parse_json_response('```json\n{"a": 1}\n```')
    assert r["parsed"] is True

    # 带中文前缀
    r = parse_json_response('好的,这是分析结果:\n{"a": 1}')
    assert r["parsed"] is True

    # 无法解析
    r = parse_json_response("这不是 JSON")
    assert r["parsed"] is False
    assert r["parse_failed"] is True
    assert "raw_response" in r

    print("✅ test_parse_json_response passed")


def _clean_env():
    """清除 ZHIPU_*/VISION_* 环境变量, 避免干扰 .env 测试"""
    return {k: v for k, v in os.environ.items()
            if not k.startswith(("ZHIPU_", "VISION_"))}


def _run_config_with_dotenv(dotenv_content, extra_env=None):
    """在隔离的临时项目结构中运行 vision.py config。
    临时目录内建 scripts/ + .env, 避免读到真实项目根的 .env(用户配置)。"""
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        scripts_dir = os.path.join(tmp, "scripts")
        os.makedirs(scripts_dir)
        shutil.copy(os.path.join(SCRIPT_DIR, "vision.py"), os.path.join(scripts_dir, "vision.py"))
        shutil.copy(os.path.join(SCRIPT_DIR, "config.py"), os.path.join(scripts_dir, "config.py"))
        with open(os.path.join(tmp, ".env"), "w", encoding="utf-8") as f:
            f.write(dotenv_content)
        env = _clean_env()
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [PYTHON, os.path.join(scripts_dir, "vision.py"), "config"],
            capture_output=True, text=True, timeout=10,
            cwd=tmp, env=env,
        )


def test_dotenv_config():
    """测试 .env 文件配置 key/model 生效"""
    result = _run_config_with_dotenv(
        "# comment line\n"
        'ZHIPU_API_KEY="dotenv-key-123"\n'
        "VISION_MODEL=glm-dotenv-model\n"
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    cfg = data["config"]
    assert cfg["model"] == "glm-dotenv-model", cfg
    assert cfg["api_key_preview"] == "dotenv-k...", cfg
    assert data["valid"] is True, data
    print("✅ test_dotenv_config passed")


def test_dotenv_env_priority():
    """测试显式环境变量优先于 .env"""
    result = _run_config_with_dotenv(
        "VISION_MODEL=glm-dotenv-model\n",
        extra_env={"VISION_MODEL": "glm-explicit-model", "ZHIPU_API_KEY": "explicit-key"},
    )
    assert result.returncode == 0, result.stderr
    cfg = json.loads(result.stdout)["config"]
    assert cfg["model"] == "glm-explicit-model", cfg
    assert cfg["api_key_preview"] == "explicit...", cfg
    print("✅ test_dotenv_env_priority passed")


def test_throttle_interval():
    """测试进程内节流: 两次 _throttle 调用间隔 >= REQUEST_INTERVAL"""
    import time
    sys.path.insert(0, SCRIPT_DIR)
    import vision

    vision.REQUEST_INTERVAL = 0.3  # monkeypatch 缩短间隔加速测试
    vision._last_request_time[0] = 0.0
    t0 = time.monotonic()
    vision._throttle()  # 首次不 sleep
    vision._throttle()  # 第二次应补齐间隔
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.28, f"节流未生效: {elapsed:.3f}s"
    print("✅ test_throttle_interval passed")


def test_retry_wait():
    """测试 429 重试等待: 指数退避 + Retry-After 优先 + 封顶"""
    sys.path.insert(0, SCRIPT_DIR)
    from vision import _retry_wait

    # 指数退避: 5s * 2^attempt, 封顶 60
    assert _retry_wait(0, "Rate limit hit (429). GLM...") == 5
    assert _retry_wait(1, "Rate limit hit (429). GLM...") == 10
    assert _retry_wait(5, "Rate limit hit (429). GLM...") == 60
    # Retry-After 优先
    assert _retry_wait(0, "Rate limit hit (429). Retry-After: 3s.") == 3
    # 服务器建议超长时仍封顶 60
    assert _retry_wait(9, "Rate limit hit (429). Retry-After: 120s.") == 60
    print("✅ test_retry_wait passed")


def test_mime_data_url():
    """测试本地图片生成带真实 MIME 的 data URL (换 OpenAI 兼容后端必需)"""
    import base64
    import tempfile
    sys.path.insert(0, SCRIPT_DIR)
    from vision import prepare_image_input, mime_for

    assert mime_for("a.jpg") == "image/jpeg"
    assert mime_for("a.JPG") == "image/jpeg"
    assert mime_for("a.png") == "image/png"
    assert mime_for("a.webp") == "image/webp"
    assert mime_for("a.unknown") == "image/jpeg"  # 未知回退

    # 最小 1x1 png
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "t.png")
        with open(p, "wb") as f:
            f.write(base64.b64decode(png_b64))
        r = prepare_image_input(p)
        assert r.startswith("data:image/png;base64,"), r[:40]
        # URL 原样返回
        assert prepare_image_input("https://x.com/a.png") == "https://x.com/a.png"
    print("✅ test_mime_data_url passed")


if __name__ == "__main__":
    test_config_command()
    test_missing_image()
    test_parse_json_response()
    test_dotenv_config()
    test_dotenv_env_priority()
    test_throttle_interval()
    test_retry_wait()
    test_mime_data_url()
    print("\n所有测试通过! ✅")
