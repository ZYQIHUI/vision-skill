# 安装指南 — Vision Skill

## 前置要求

1. **Python 3.8+** — 检查: `python3 --version`
2. **硅基流动 API Key** — 免费注册: [cloud.siliconflow.cn](https://cloud.siliconflow.cn)(默认供应商)
   - 备用供应商(可选): 智谱 key — [open.bigmodel.cn](https://open.bigmodel.cn)

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
mkdir -p ~/.claude/skills/vision-skill/scripts
mkdir -p ~/.claude/skills/vision-skill/assets

cp SKILL.md ~/.claude/skills/vision-skill/
cp scripts/vision.py ~/.claude/skills/vision-skill/scripts/
cp scripts/config.py ~/.claude/skills/vision-skill/scripts/
cp assets/prompts.json ~/.claude/skills/vision-skill/assets/
cp .env.example ~/.claude/skills/vision-skill/
```

### For Codex / Kun

```bash
mkdir -p ~/.codex/skills/vision-skill/scripts
mkdir -p ~/.codex/skills/vision-skill/assets

cp SKILL.md ~/.codex/skills/vision-skill/
cp scripts/vision.py ~/.codex/skills/vision-skill/scripts/
cp scripts/config.py ~/.codex/skills/vision-skill/scripts/
cp assets/prompts.json ~/.codex/skills/vision-skill/assets/
cp .env.example ~/.codex/skills/vision-skill/
```

### For Cursor

```bash
mkdir -p ~/.agents/skills/vision-skill/scripts
mkdir -p ~/.agents/skills/vision-skill/assets

cp SKILL.md ~/.agents/skills/vision-skill/
cp scripts/vision.py ~/.agents/skills/vision-skill/scripts/
cp scripts/config.py ~/.agents/skills/vision-skill/scripts/
cp assets/prompts.json ~/.agents/skills/vision-skill/assets/
cp .env.example ~/.agents/skills/vision-skill/
```

### 项目级安装

将上述命令中的 `~/` 替换为你的项目目录,使用项目级 skill 目录(如 `.codex/skills/`)。

## 设置 API Key

默认供应商为**硅基流动**,主用模型 `Qwen/Qwen3.5-4B`(免费,输入/输出 ¥0.000000/K tokens)。

方式一:环境变量

```bash
# Linux / macOS
echo 'export SILICONFLOW_API_KEY="your-key-here"' >> ~/.bashrc
echo 'export VISION_PROVIDER="siliconflow"' >> ~/.bashrc   # 可选,默认即此
source ~/.bashrc

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable("SILICONFLOW_API_KEY", "your-key-here", "User")
```

方式二:项目根目录 `.env` 文件(推荐本地开发,已被 `.gitignore` 忽略)

```bash
# 在 vision-skill/ 根目录创建 .env(可 cp .env.example .env)
VISION_PROVIDER=siliconflow
SILICONFLOW_API_KEY=your-key-here
VISION_MODEL=Qwen/Qwen3.5-4B    # 可选,默认即此
```

`.env` 支持 `#` 注释与可选引号(`KEY="value"`)。显式环境变量优先于 `.env`;模型用 `VISION_MODEL` 配置,默认按供应商(`Qwen/Qwen3.5-4B` / 智谱 `glm-4.6v-flash`)。

**切备用供应商(智谱)**: 将 `VISION_PROVIDER` 改为 `zhipu` 并设置 `ZHIPU_API_KEY=your-key`,模型默认 `glm-4.6v-flash`(永久免费)。

## 验证安装

```bash
python ~/.codex/skills/vision-skill/scripts/vision.py config
```

如果看到 `"valid": true` 且 `"provider": "siliconflow"`,说明配置正确。

## 测试

```bash
python ~/.codex/skills/vision-skill/scripts/vision.py understand --image "test.jpg"
```

重启 Agent 框架后,尝试让它分析一张图片。
