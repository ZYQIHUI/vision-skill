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


def test_dotenv_config():
    """测试 .env 文件配置 key/model 生效"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, ".env"), "w", encoding="utf-8") as f:
            f.write("# comment line\n")
            f.write('ZHIPU_API_KEY="dotenv-key-123"\n')
            f.write("VISION_MODEL=glm-dotenv-model\n")
        result = subprocess.run(
            [PYTHON, VISION_PY, "config"],
            capture_output=True, text=True, timeout=10,
            cwd=tmp, env=_clean_env(),
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
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, ".env"), "w", encoding="utf-8") as f:
            f.write("VISION_MODEL=glm-dotenv-model\n")
        env = _clean_env()
        env["VISION_MODEL"] = "glm-explicit-model"
        env["ZHIPU_API_KEY"] = "explicit-key"
        result = subprocess.run(
            [PYTHON, VISION_PY, "config"],
            capture_output=True, text=True, timeout=10,
            cwd=tmp, env=env,
        )
        assert result.returncode == 0, result.stderr
        cfg = json.loads(result.stdout)["config"]
        assert cfg["model"] == "glm-explicit-model", cfg
        assert cfg["api_key_preview"] == "explicit...", cfg
    print("✅ test_dotenv_env_priority passed")


if __name__ == "__main__":
    test_config_command()
    test_missing_image()
    test_parse_json_response()
    test_dotenv_config()
    test_dotenv_env_priority()
    print("\n所有测试通过! ✅")
