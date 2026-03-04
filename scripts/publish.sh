#!/bin/bash
# =============================================================
# publish.sh — 公众号文章一键发布流水线（第二阶段）
# 用法：bash scripts/publish.sh <markdown文件路径>
#
# 前置条件：
#   - 文章已定稿，frontmatter 含 title / author / description
#   - .baoyu-skills/.env 已配置所有 key
#   - 如需配图，在 articles/imgs/ 提前放好；或由本脚本自动生成封面
#
# 流程：
#   Step 1 — 生成封面图（已存在则跳过）
#   Step 2 — 上传微信草稿箱（wechat-api 自动处理内容图片上传）
#   Step 3 — Notion 入库（文章选题草稿箱）
# =============================================================

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
ENV_FILE="$WORKSPACE/.baoyu-skills/.env"
IMGS_DIR="$WORKSPACE/articles/imgs"
IMAGE_GEN="$HOME/.agents/skills/baoyu-image-gen/scripts/main.ts"
WECHAT_API="$HOME/.agents/skills/baoyu-post-to-wechat/scripts/wechat-api.ts"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# ── 入参与环境 ────────────────────────────────────────────────
MD_FILE="${1:-}"
[ -z "$MD_FILE" ] && fail "用法：bash scripts/publish.sh articles/your-article.md"
[ -f "$MD_FILE" ] || fail "文件不存在：$MD_FILE"
MD_FILE="$(cd "$(dirname "$MD_FILE")" && pwd)/$(basename "$MD_FILE")"

set -a; source "$ENV_FILE" 2>/dev/null || warn ".env 加载失败，尝试继续"; set +a

# ── 读取 frontmatter ──────────────────────────────────────────
TITLE=$(grep '^title:' "$MD_FILE" | head -1 | sed 's/^title: *//;s/^"//;s/"$//')
AUTHOR=$(grep '^author:' "$MD_FILE" | head -1 | sed 's/^author: *//;s/^"//;s/"$//')
SUMMARY=$(grep '^description:' "$MD_FILE" | head -1 | sed 's/^description: *//;s/^"//;s/"$//')
SLUG=$(basename "$MD_FILE" .md)
AUTHOR="${AUTHOR:-余炜勋}"
[ -z "$TITLE" ] && fail "frontmatter 缺少 title 字段"

echo ""
echo -e "${BOLD}📰 发布流水线启动${NC}"
echo -e "   文章：$TITLE"
echo -e "   作者：$AUTHOR"
echo ""

# ── Step 1：生成封面图 ────────────────────────────────────────
log "Step 1/3  生成封面图..."
COVER_IMG="$IMGS_DIR/cover-${SLUG}.png"
mkdir -p "$IMGS_DIR"

if [ -f "$COVER_IMG" ]; then
  warn "封面图已存在，跳过：$(basename "$COVER_IMG")"
else
  PROMPT="为微信公众号文章《${TITLE}》生成封面图。专业商务风，中国科技感，蓝色调，简洁大气，横版16:9，无文字。"
  RETRY=0
  GEN_OK=0

  # 主路：SmartAPI（chat completions 接口）
  log "尝试主路图片代理（SmartAPI）..."
  until IMAGE_GEN_BACKUP_BASE_URL= \
        IMAGE_GEN_BACKUP_API_KEY= \
        IMAGE_GEN_BACKUP_MODEL= \
        IMAGE_GEN_BASE_URL="$IMAGE_GEN_BASE_URL" \
        IMAGE_GEN_API_KEY="$IMAGE_GEN_API_KEY" \
        IMAGE_GEN_MODEL="$IMAGE_GEN_MODEL" \
        python3 "$WORKSPACE/scripts/smartapi-image-gen.py" "$PROMPT" "$COVER_IMG" 2>&1; do
    RETRY=$((RETRY+1))
    [ $RETRY -ge 3 ] && break
    warn "主路失败（$RETRY/3），60s 后重试..."
    sleep 60
  done

  # 检查是否生成成功
  if [ -f "$COVER_IMG" ]; then
    GEN_OK=1
  else
    # 备用路：本地代理 8317
    warn "主路失败，切换备用 API（本地代理）..."
    RETRY=0
    until OPENAI_BASE_URL="$IMAGE_GEN_BACKUP_BASE_URL" \
          OPENAI_API_KEY="$IMAGE_GEN_BACKUP_API_KEY" \
          OPENAI_IMAGE_MODEL="$IMAGE_GEN_BACKUP_MODEL" \
          npx -y bun "$IMAGE_GEN" --prompt "$PROMPT" --image "$COVER_IMG" --ar 16:9 2>&1; do
      RETRY=$((RETRY+1))
      [ $RETRY -ge 3 ] && fail "封面图生成失败，主路+备用均已重试 3 次"
      warn "备用路失败（$RETRY/3），60s 后重试..."
      sleep 60
    done
    [ -f "$COVER_IMG" ] && GEN_OK=1
  fi

  [ $GEN_OK -eq 0 ] && fail "封面图生成失败"
  ok "封面图：$(basename "$COVER_IMG")"
fi

# ── Step 2：上传微信草稿箱 ────────────────────────────────────
log "Step 2/3  上传微信草稿箱..."
cd "$WORKSPACE"

WECHAT_OUT=$(npx -y bun "$WECHAT_API" "$MD_FILE" --author "$AUTHOR" --cover "$COVER_IMG" 2>&1)
echo "$WECHAT_OUT"

MEDIA_ID=$(echo "$WECHAT_OUT" | grep -oP '(?i)media_id["\s:=]+\K[A-Za-z0-9_\-]+' | head -1)
[ -n "${MEDIA_ID:-}" ] && ok "微信草稿：$MEDIA_ID" || warn "未提取到 media_id，请检查上方输出"

# ── Step 3：Notion 入库 ───────────────────────────────────────
log "Step 3/3  Notion 入库..."

NOTION_OUT=$(NOTION_API_KEY="$NOTION_API_KEY" \
  NOTION_ARTICLE_DB_ID="${NOTION_ARTICLE_DB_ID:-a8a41765-aec8-417e-8764-7506465bb42f}" \
  NOTION_GATEWAY_URL="${NOTION_GATEWAY_URL:-https://gateway.maton.ai/notion/v1/}" \
  python3 - <<PYEOF
import urllib.request, json, os

api_key = os.environ['NOTION_API_KEY']
db_id   = os.environ['NOTION_ARTICLE_DB_ID']
gateway = os.environ['NOTION_GATEWAY_URL']
title   = """$TITLE"""
summary = """$SUMMARY"""
media_id = """${MEDIA_ID:-}"""
md_path  = """$MD_FILE"""

with open(md_path) as f:
    raw = f.read()
parts = raw.split('---', 2)
body = (parts[2].strip() if len(parts) >= 3 else raw)[:2000]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Notion-Version': '2025-09-03'
}

# 创建页面
page = urllib.request.Request(
    f'{gateway}pages',
    data=json.dumps({
        "parent": {"database_id": db_id},
        "properties": {
            "文章标题": {"title": [{"text": {"content": title}}]},
            "摘要":    {"rich_text": [{"text": {"content": summary[:500]}}]},
            "状态":    {"select": {"name": "草稿"}},
            "是否采纳": {"checkbox": True}
        }
    }).encode(), headers=headers, method='POST')
with urllib.request.urlopen(page) as r:
    page_id = json.load(r).get('id', '')
print(f'page_id={page_id}')

# 写正文 block
if page_id:
    children = [{"object":"block","type":"paragraph",
                 "paragraph":{"rich_text":[{"text":{"content": body}}]}}]
    if media_id:
        children.append({"object":"block","type":"paragraph",
            "paragraph":{"rich_text":[{"text":{"content":f"微信 media_id: {media_id}"}}]}})
    urllib.request.urlopen(urllib.request.Request(
        f'{gateway}blocks/{page_id}/children',
        data=json.dumps({"children": children}).encode(),
        headers=headers, method='PATCH'))
    print('blocks_written=ok')
PYEOF
)

echo "$NOTION_OUT"
NOTION_PAGE_ID=$(echo "$NOTION_OUT" | grep -oP 'page_id=\K\S+' | head -1)
[ -n "${NOTION_PAGE_ID:-}" ] && ok "Notion：$NOTION_PAGE_ID" || warn "Notion 入库可能失败"

# ── 汇总 ─────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}🎉 完成${NC}"
echo -e "   📄 $TITLE"
echo -e "   🖼️  封面：$(basename "$COVER_IMG")"
[ -n "${MEDIA_ID:-}" ]       && echo -e "   📱 微信：$MEDIA_ID"
[ -n "${NOTION_PAGE_ID:-}" ] && echo -e "   📋 Notion：$NOTION_PAGE_ID"
echo ""
