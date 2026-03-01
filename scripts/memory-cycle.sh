#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/scripts/memory-session-hook.py"

if [ "$#" -lt 2 ]; then
  cat <<'EOF'
Usage:
  scripts/memory-cycle.sh pre  "<query>" [user_id] [conversation_id]
  scripts/memory-cycle.sh post "<summary>" [user_id] [conversation_id]
EOF
  exit 1
fi

STAGE="$1"
TEXT="$2"
USER_ID="${3:-dongcheng-laotao}"
CONV_ID="${4:-openclaw-main}"

python3 "$HOOK" "$STAGE" "$TEXT" "$USER_ID" "$CONV_ID"
