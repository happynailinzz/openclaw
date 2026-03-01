#!/usr/bin/env bash
set -euo pipefail

# 用途：在服务器环境稳定抓取微信公众号/网页为 markdown
# 特点：自动使用已安装的 Chrome for Testing + xvfb + --no-sandbox（root 友好）

if [[ $# -lt 1 ]]; then
  echo "用法: $0 <url> [output.md] [--wait]"
  exit 1
fi

URL="$1"
OUT="${2:-}"
MODE_WAIT="${3:-}"

CHROME_BIN="/root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome"
WRAPPER="/root/.openclaw/workspace/tmp/url-chrome-wrapper.sh"
SCRIPT="/root/.agents/skills/baoyu-url-to-markdown/scripts/main.ts"

if [[ ! -x "$CHROME_BIN" ]]; then
  echo "未找到 Chrome: $CHROME_BIN"
  exit 2
fi

mkdir -p /root/.openclaw/workspace/tmp
cat > "$WRAPPER" <<'EOF'
#!/usr/bin/env bash
set -e
exec xvfb-run -a /root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome --no-sandbox --disable-gpu "$@"
EOF
chmod +x "$WRAPPER"

export URL_CHROME_PATH="$WRAPPER"

CMD=(npx -y bun "$SCRIPT" "$URL")
if [[ -n "$OUT" ]]; then
  CMD+=(-o "$OUT")
fi
if [[ "$MODE_WAIT" == "--wait" ]]; then
  CMD+=(--wait)
fi

echo "[wechat-capture] URL: $URL"
echo "[wechat-capture] OUT: ${OUT:-auto}"
echo "[wechat-capture] WAIT: ${MODE_WAIT:-auto}"
"${CMD[@]}"
