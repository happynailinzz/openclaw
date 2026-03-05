#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/.openclaw/workspace"
ENV_FILE="$ROOT/config/evomap.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ missing: $ENV_FILE"
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

A2A_NODE_ID_VALUE="${A2A_NODE_ID:-${EVOMAP_SENDER_ID:-}}"

if [[ -z "$A2A_NODE_ID_VALUE" ]]; then
  echo "❌ A2A_NODE_ID not set (fallback EVOMAP_SENDER_ID also empty)"
  exit 2
fi

if [[ "$A2A_NODE_ID_VALUE" != node_* ]]; then
  echo "⚠️ A2A_NODE_ID format suspicious: $A2A_NODE_ID_VALUE"
else
  echo "✅ A2A_NODE_ID ready: $A2A_NODE_ID_VALUE"
fi

echo "- EVOMAP_BASE_URL: ${EVOMAP_BASE_URL:-unset}"
echo "- EVOMAP_SENDER_ID: ${EVOMAP_SENDER_ID:+set}"
echo "- A2A_NODE_ID(runtime): ${A2A_NODE_ID:+set}"
