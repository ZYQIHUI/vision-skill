# 安装指南 — GLM Vision Skill

## 前置要求

1. **Python 3.8+** — 检查: `python3 --version`
2. **智谱 API Key** — 免费获取: [open.bigmodel.cn](https://open.bigmodel.cn)

## 选项 A: 一键安装(推荐)

```bash
git clone https://github.com/ZYQIHUI/vision-skill.git
cd vision-skill
./install.sh
```

安装器会自动检测你已安装的 Agent 框架。如果检测到多个,会让你选择安装目标。

## 选项 B: 手动安装

### For Claude Code

```bash
mkdir -p ~/.claude/skills/glm-vision/scripts
mkdir -p ~/.claude/skills/glm-vision/assets

cp SKILL.md ~/.claude/skills/glm-vision/
cp scripts/vision.py ~/.claude/skills/glm-vision/scripts/
cp scripts/config.py ~/.claude/skills/glm-vision/scripts/
cp assets/prompts.json ~/.claude/skills/glm-vision/assets/
```

### For Codex / Kun

```bash
mkdir -p ~/.codex/skills/glm-vision/scripts
mkdir -p ~/.codex/skills/glm-vision/assets

cp SKILL.md ~/.codex/skills/glm-vision/
cp scripts/vision.py ~/.codex/skills/glm-vision/scripts/
cp scripts/config.py ~/.codex/skills/glm-vision/scripts/
cp assets/prompts.json ~/.codex/skills/glm-vision/assets/
```

### For Cursor

```bash
mkdir -p ~/.agents/skills/glm-vision/scripts
mkdir -p ~/.agents/skills/glm-vision/assets

cp SKILL.md ~/.agents/skills/glm-vision/
cp scripts/vision.py ~/.agents/skills/glm-vision/scripts/
cp scripts/config.py ~/.agents/skills/glm-vision/scripts/
cp assets/prompts.json ~/.agents/skills/glm-vision/assets/
```

### 项目级安装

将上述命令中的 `~/` 替换为你的项目目录,使用项目级 skill 目录(如 `.codex/skills/`)。

## 设置 API Key

方式一:环境变量

```bash
# Linux / macOS
echo 'export ZHIPU_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable("ZHIPU_API_KEY", "your-key-here", "User")
```

方式二:项目根目录 `.env` 文件(推荐本地开发,已被 `.gitignore` 忽略)

```bash
# 在 vision-skill/ 根目录创建 .env
ZHIPU_API_KEY=your-key-here
VISION_MODEL=glm-4.6v-flash    # 可选,默认即此
```

`.env` 支持 `#` 注释与可选引号(`KEY="value"`)。显式环境变量优先于 `.env`;模型用 `VISION_MODEL` 配置,默认为 `glm-4.6v-flash`。

## 验证安装

```bash
python ~/.codex/skills/glm-vision/scripts/vision.py config
```

如果看到 `"valid": true`,说明配置正确。

## 测试

```bash
python ~/.codex/skills/glm-vision/scripts/vision.py understand --image "test.jpg"
```

重启 Agent 框架后,尝试让它分析一张图片。
