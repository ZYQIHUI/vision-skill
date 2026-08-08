#!/usr/bin/env bash
# Vision Skill — One-click installer (multi-framework aware)
# Usage:
#   ./install.sh [--global] [--local] [--to DIR]
#
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect all installed frameworks — return multiple candidates, not just first
detect_candidates_global() {
  local home="$HOME"; local out=""
  [ -d "$home/.claude" ] && out="$out $home/.claude/skills"
  [ -d "$home/.codex"  ] && out="$out $home/.codex/skills"
  [ -d "$home/.agents" ] && out="$out $home/.agents/skills"
  [ -d "$HOME/.config/opencode" ] && out="$out $HOME/.config/opencode/skills"
  echo $out | tr ' ' '\n' | sed '/^$/d'
}

INSTALL_SCOPE="auto"; TO_DIR=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --global) INSTALL_SCOPE="global"; shift ;;
    --local)  INSTALL_SCOPE="local";  shift ;;
    --to)     TO_DIR="$2"; shift 2 ;;
    --help|-h) echo "Usage: ./install.sh [--global|--local] [--to DIR]"; exit 0 ;;
    *) err "Unknown: $1"; exit 1 ;;
  esac
done

PYTHON="$(command -v python3 || command -v python)"
[ -z "$PYTHON" ] && { err "Python 3 required."; exit 1; }
ok "Python: $($PYTHON --version 2>&1)"

# Determine target dir — ask user if multiple candidates found
if [ -n "$TO_DIR" ]; then
  SKILL_DIR="$TO_DIR"
elif [ "$INSTALL_SCOPE" = "local" ]; then
  for d in .claude/skills .codex/skills .agents/skills; do
    [ -d "$(dirname $d)" ] && SKILL_DIR="$d" && break
  done
  [ -z "$SKILL_DIR" ] && SKILL_DIR=".codex/skills"
else
  CANDIDATES=$(detect_candidates_global)
  COUNT=$(echo "$CANDIDATES" | grep -c .)
  if [ "$COUNT" -eq 0 ]; then
    err "No supported Agent framework found. Use --to DIR to specify."
    exit 1
  elif [ "$COUNT" -eq 1 ]; then
    SKILL_DIR="$CANDIDATES"
  else
    echo "检测到多个 Agent 框架,请选择安装目标:"
    select d in $CANDIDATES; do
      [ -n "$d" ] && SKILL_DIR="$d" && break
      err "无效选择"
    done
  fi
fi

SKILL_NAME="vision-skill"
INSTALL_DIR="$SKILL_DIR/$SKILL_NAME"
ok "安装到: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR/scripts" "$INSTALL_DIR/assets" "$INSTALL_DIR/references"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/SKILL.md" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/vision.py" "$INSTALL_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/config.py" "$INSTALL_DIR/scripts/"
cp "$SCRIPT_DIR/assets/prompts.json" "$INSTALL_DIR/assets/"
cp "$SCRIPT_DIR/scripts/requirements.txt" "$INSTALL_DIR/scripts/" 2>/dev/null || true
[ -d "$SCRIPT_DIR/references" ] && cp -r "$SCRIPT_DIR/references/"* "$INSTALL_DIR/references/" 2>/dev/null || true
ok "文件复制完成"

if [ -z "$AGNES_API_KEY" ]; then
  warn "AGNES_API_KEY 未设置(默认供应商: Agnes AI)!"
  echo "  免费注册: https://platform.agnes-ai.com"
  echo "  export AGNES_API_KEY=\"your-key\""
  echo "  或参考安装目录中的 .env.example 配置"
elif [ -z "$SILICONFLOW_API_KEY" ]; then
  warn "备用供应商 SILICONFLOW_API_KEY 未设置(仅切 VISION_PROVIDER=siliconflow 时需要)"
elif [ -z "$ZHIPU_API_KEY" ]; then
  warn "备用供应商 ZHIPU_API_KEY 未设置(仅切 VISION_PROVIDER=zhipu 时需要)"
else
  ok "AGNES_API_KEY 已设置"
fi

( cd "$INSTALL_DIR" && $PYTHON scripts/vision.py config 2>/dev/null && ok "skill 就绪" ) || warn "请检查上方配置"

echo ""
ok "安装完成。重启 Agent 框架即可加载 skill。"
