#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
REQUIRED_SKILLS=(tavily-search baidu-search jina-reader humanize-zh notion-api-skill obsidian word-docx excel-xlsx)

section() {
  echo
  echo "==== $1 ===="
}

ok() { echo "[OK] $1"; }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; }

section "Version"
if command -v openclaw >/dev/null 2>&1; then
  openclaw --version || true
else
  fail "openclaw not found"
  exit 1
fi

section "Gateway"
if openclaw gateway status >/tmp/openclaw-gateway-status.txt 2>&1; then
  ok "gateway reachable"
else
  warn "gateway status command returned non-zero"
fi
sed -n '1,80p' /tmp/openclaw-gateway-status.txt || true

section "Cron"
if openclaw cron list --json >/tmp/openclaw-cron.json 2>/dev/null; then
  python3 - <<'PY'
import json
j=json.load(open('/tmp/openclaw-cron.json'))
jobs=j.get('jobs',[])
print(f"cron_jobs={len(jobs)}")
for x in jobs:
    s=x.get('state',{})
    print(f"- {x['name']}: enabled={x.get('enabled')} last={s.get('lastStatus')} consecutiveErrors={s.get('consecutiveErrors',0)}")
PY
else
  warn "cannot read cron list"
fi

section "Memory"
if openclaw memory status --json >/tmp/openclaw-memory.json 2>/dev/null; then
  python3 - <<'PY'
import json
arr=json.load(open('/tmp/openclaw-memory.json'))
for item in arr:
    st=item.get('status',{})
    print('agent=',item.get('agentId'))
    print(' provider=',st.get('provider'),' searchMode=',st.get('custom',{}).get('searchMode'))
    print(' extraPaths=',st.get('extraPaths'))
    reason=st.get('custom',{}).get('providerUnavailableReason')
    if reason and st.get('provider')=='none':
        print(' note=embeddings provider not configured')
PY
else
  warn "cannot read memory status"
fi

section "Skills"
missing=0
for s in "${REQUIRED_SKILLS[@]}"; do
  if [ -f "$SKILLS_DIR/$s/SKILL.md" ]; then
    ok "skill present: $s"
  else
    warn "skill missing: $s"
    missing=$((missing+1))
  fi
done

section "Notion/Maton env (gateway process)"
pid=$(systemctl --user show -p MainPID --value openclaw-gateway.service 2>/dev/null || echo 0)
if [ -n "$pid" ] && [ "$pid" != "0" ] && [ -r "/proc/$pid/environ" ]; then
  if tr '\0' '\n' < "/proc/$pid/environ" | grep -q '^MATON_API_KEY='; then
    ok "MATON_API_KEY present in gateway process env"
  else
    warn "MATON_API_KEY missing in gateway process env"
  fi
else
  warn "cannot inspect gateway process env"
fi

section "Workspace quick checks"
[ -f "$WORKSPACE/HEARTBEAT.md" ] && ok "HEARTBEAT.md present" || warn "HEARTBEAT.md missing"
[ -f "$WORKSPACE/MEMORY.md" ] && ok "MEMORY.md present" || warn "MEMORY.md missing"
[ -f "$WORKSPACE/SKILLS_CHEATSHEET.md" ] && ok "SKILLS_CHEATSHEET.md present" || warn "SKILLS_CHEATSHEET.md missing"

echo
echo "Verification complete."
