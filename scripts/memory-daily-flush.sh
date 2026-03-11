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

# 提取今日记忆的关键内容（按字符截断，避免多字节字符被截断导致乱码）
SUMMARY=$(MEM_FILE="$MEM_FILE" python3 - <<'PY'
import os
from pathlib import Path
p = Path(os.environ["MEM_FILE"])
text = p.read_text(encoding="utf-8", errors="replace")
summary = text[:1000].replace("\n", " ")
while "  " in summary:
    summary = summary.replace("  ", " ")
print(summary.strip())
PY
)

if [ -z "$SUMMARY" ]; then
  echo "记忆文件为空，跳过"
  exit 0
fi

python3 scripts/memos-client.py add "【每日记忆归档 $TODAY】$SUMMARY" "dongcheng-laotao" "openclaw-main"
echo "记忆归档完成: $TODAY"
