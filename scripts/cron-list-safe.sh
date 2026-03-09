#!/usr/bin/env sh
set -eu

TMP_OUT="${TMPDIR:-/tmp}/openclaw-cron-list.$$ .out"
TMP_ERR="${TMPDIR:-/tmp}/openclaw-cron-list.$$ .err"
# shellcheck disable=SC2039
TMP_OUT=$(printf '%s' "$TMP_OUT" | tr -d ' ')
TMP_ERR=$(printf '%s' "$TMP_ERR" | tr -d ' ')

cleanup() {
  rm -f "$TMP_OUT" "$TMP_ERR"
}
trap cleanup EXIT INT TERM

if command -v timeout >/dev/null 2>&1; then
  timeout 12s sh -c 'openclaw cron list >"$1" 2>"$2"' sh "$TMP_OUT" "$TMP_ERR" || true
else
  sh -c 'openclaw cron list >"$1" 2>"$2"' sh "$TMP_OUT" "$TMP_ERR" || true
fi

if [ -s "$TMP_OUT" ]; then
  sed -n '1,240p' "$TMP_OUT"
  exit 0
fi

if [ -s "$TMP_ERR" ]; then
  echo "[cron-list-safe] stderr:" >&2
  sed -n '1,120p' "$TMP_ERR" >&2
  exit 1
fi

echo "[cron-list-safe] no output captured" >&2
exit 1
