#!/usr/bin/env bash
set -euo pipefail
ROOT="/root/.openclaw/workspace"
ENV_FILE="$ROOT/config/evomap.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

export A2A_NODE_ID="${A2A_NODE_ID:-${EVOMAP_SENDER_ID:-}}"

if [[ -z "${A2A_NODE_ID}" ]]; then
  echo "❌ missing A2A_NODE_ID / EVOMAP_SENDER_ID"
  exit 1
fi

echo "[evolver] using A2A_NODE_ID=$A2A_NODE_ID"
cd "$ROOT"
node skills/capability-evolver/index.js --review
