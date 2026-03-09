#!/usr/bin/env bash
set -euo pipefail

DISPLAY_NUM="${DISPLAY_NUM:-:1}"
CHROME_BIN="/root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome"
PROFILE_DIR="/tmp/openclaw-chrome-profile"
XVFB_LOG="/tmp/xvfb-openclaw.log"
CHROME_LOG="/tmp/openclaw-chrome.log"

if ! pgrep -f "Xvfb ${DISPLAY_NUM}" >/dev/null 2>&1; then
  nohup Xvfb "${DISPLAY_NUM}" -screen 0 1440x900x24 >"${XVFB_LOG}" 2>&1 &
  sleep 1
fi

if ! ss -ltn 2>/dev/null | grep -q ':9222 '; then
  nohup env DISPLAY="${DISPLAY_NUM}" "${CHROME_BIN}" \
    --no-sandbox \
    --remote-debugging-port=9222 \
    --remote-allow-origins=* \
    --user-data-dir="${PROFILE_DIR}" \
    about:blank >"${CHROME_LOG}" 2>&1 &
  sleep 2
fi

ss -ltnp 2>/dev/null | grep -E ':(9222)\b' || true
