#!/usr/bin/env bash
# 每日记忆冷存储：把当天日志摘要写入 Memos
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .baoyu-skills/.env 2>/dev/null || true

TODAY=$(date -u +%Y-%m-%d)
MEM_FILE="memory/${TODAY}.md"

if [ ! -f "$MEM_FILE" ]; then
  echo "今日无记忆文件，跳过"
  exit 0
fi

# 提取今日记忆的关键内容（取前 1000 字）
SUMMARY=$(head -c 1000 "$MEM_FILE" | tr '\n' ' ' | sed 's/  */ /g')

if [ -z "$SUMMARY" ]; then
  echo "记忆文件为空，跳过"
  exit 0
fi

python3 scripts/memos-client.py add "【每日记忆归档 $TODAY】$SUMMARY" "dongcheng-laotao" "openclaw-main"
echo "记忆归档完成: $TODAY"
