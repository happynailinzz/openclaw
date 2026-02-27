#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
CONFIG_PATH="/root/.openclaw/openclaw.json"
ENV_DIR="$HOME/.config/openclaw"
ENV_FILE="$ENV_DIR/env"
SYSTEMD_DROPIN_DIR="$HOME/.config/systemd/user/openclaw-gateway.service.d"
SYSTEMD_DROPIN_FILE="$SYSTEMD_DROPIN_DIR/env.conf"
KNOWLEDGE_PATH="/opt/openclaw/knowledge/secendME"

echo "[bootstrap] starting OpenClaw bootstrap..."

if ! command -v openclaw >/dev/null 2>&1; then
  echo "[bootstrap] ERROR: openclaw not found in PATH"
  exit 1
fi

mkdir -p "$ENV_DIR"
if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<'EOF'
# OpenClaw runtime env (fill values, do NOT commit this file)
# MATON_API_KEY=
# TAVILY_API_KEY=
# BRAVE_API_KEY=
# OPENAI_API_KEY=
# GOOGLE_API_KEY=
# VOYAGE_API_KEY=
EOF
  chmod 600 "$ENV_FILE"
  echo "[bootstrap] created env template: $ENV_FILE"
else
  chmod 600 "$ENV_FILE"
  echo "[bootstrap] env file exists: $ENV_FILE"
fi

mkdir -p "$SYSTEMD_DROPIN_DIR"
cat > "$SYSTEMD_DROPIN_FILE" <<EOF
[Service]
EnvironmentFile=%h/.config/openclaw/env
EOF
echo "[bootstrap] wrote systemd drop-in: $SYSTEMD_DROPIN_FILE"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[bootstrap] ERROR: config not found at $CONFIG_PATH"
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/.openclaw/openclaw.json')
cfg=json.loads(p.read_text(encoding='utf-8'))

agents=cfg.setdefault('agents',{})
defs=agents.setdefault('defaults',{})
ms=defs.setdefault('memorySearch',{})
extra=ms.setdefault('extraPaths',[])
if '/opt/openclaw/knowledge/secendME' not in extra:
    extra.append('/opt/openclaw/knowledge/secendME')

models=cfg.setdefault('models',{})
aliases=models.setdefault('aliases',{})
aliases.setdefault('g31p','cpa/gemini-3.1-pro-high')
aliases.setdefault('g3f','cpa/gemini-3-flash')
aliases.setdefault('sonnet46','cpa/claude-sonnet-4-6')
aliases.setdefault('opus46','cpa/claude-opus-4-6-thinking')

p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
print('[bootstrap] ensured config: memorySearch.extraPaths + model aliases')
PY

if command -v systemctl >/dev/null 2>&1; then
  systemctl --user daemon-reload || true
  systemctl --user restart openclaw-gateway || true
  sleep 2
fi

openclaw gateway status || true

echo "[bootstrap] done."
echo "[bootstrap] next: fill secrets in $ENV_FILE, then run: systemctl --user restart openclaw-gateway"
