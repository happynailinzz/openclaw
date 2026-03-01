#!/usr/bin/env bash
set -euo pipefail

# 一键流程：微信公众号链接 -> markdown 抓取 -> Notion 入库
# 依赖：
# 1) /root/.openclaw/workspace/scripts/wechat-capture.sh
# 2) /root/.openclaw/workspace/scripts/wechat_md_to_notion.py
# 3) 环境变量 MATON_API_KEY

if [[ $# -lt 1 ]]; then
  echo "用法: $0 <wechat_url> [--wait] [--page-id <id>]"
  exit 1
fi

URL="$1"
shift || true

WAIT_MODE=""
PAGE_ID=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wait)
      WAIT_MODE="--wait"
      shift
      ;;
    --page-id)
      PAGE_ID="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 2
      ;;
  esac
done

if [[ -z "${MATON_API_KEY:-}" ]]; then
  echo "ERROR: MATON_API_KEY 未设置"
  exit 3
fi

OUT_MD="/root/.openclaw/workspace/tmp/wechat-$(date +%Y%m%d-%H%M%S).md"

echo "[wechat_to_notion] step1 抓取 markdown..."
if [[ -n "$WAIT_MODE" ]]; then
  /root/.openclaw/workspace/scripts/wechat-capture.sh "$URL" "$OUT_MD" --wait
else
  /root/.openclaw/workspace/scripts/wechat-capture.sh "$URL" "$OUT_MD"
fi

echo "[wechat_to_notion] step2 写入 Notion..."
if [[ -n "$PAGE_ID" ]]; then
  python3 /root/.openclaw/workspace/scripts/wechat_md_to_notion.py --url "$URL" --md "$OUT_MD" --page-id "$PAGE_ID"
else
  python3 /root/.openclaw/workspace/scripts/wechat_md_to_notion.py --url "$URL" --md "$OUT_MD"
fi
