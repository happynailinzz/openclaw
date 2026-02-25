#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Workspace cleanup utility (safe by default)

Usage:
  cleanup-workspace.sh [--dry-run|--apply] [--workspace <path>] [--include-jsonl]

Options:
  --dry-run        Preview only (default)
  --apply          Move matched files into workspace .trash/<timestamp>/
  --workspace PATH Workspace path (default: script parent directory)
  --include-jsonl  Include *.jsonl session/process files in candidates
  -h, --help       Show this help

What it targets by default:
  *.tmp, *.log, *.bak-*, *.deb, .DS_Store
  site_scan_*.json, huanyao_extracted_*.json

Safety:
  - Never deletes directly
  - Excludes .git and .trash
  - Writes a report to reports/cleanup/
EOF
}

MODE="dry-run"
INCLUDE_JSONL="false"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --apply) MODE="apply"; shift ;;
    --workspace)
      WORKSPACE="${2:-}"
      [[ -n "$WORKSPACE" ]] || { echo "Missing value for --workspace" >&2; exit 1; }
      shift 2
      ;;
    --include-jsonl) INCLUDE_JSONL="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

WORKSPACE="$(cd "$WORKSPACE" && pwd)"
REPORT_DIR="$WORKSPACE/reports/cleanup"
mkdir -p "$REPORT_DIR"

TS="$(date +%F-%H%M%S)"
REPORT_FILE="$REPORT_DIR/cleanup-$TS-$MODE.txt"
TRASH_DIR="$WORKSPACE/.trash/$TS"

human_size() {
  local bytes="$1"
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec --suffix=B "$bytes"
  else
    awk -v b="$bytes" 'function human(x){s="B KMGTPE";while(x>=1024&&length(s)>1){x/=1024;s=substr(s,3)};return sprintf("%.1f%s",x,substr(s,1,1))} BEGIN{print human(b)}'
  fi
}

# Build find expression
FIND_ARGS=(
  "$WORKSPACE"
  "(" -path "$WORKSPACE/.git" -o -path "$WORKSPACE/.git/*" -o -path "$WORKSPACE/.trash" -o -path "$WORKSPACE/.trash/*" ")" -prune
  -o -type f
  "(" -name "*.tmp" -o -name "*.log" -o -name "*.bak-*" -o -name "*.deb" -o -name ".DS_Store" -o -name "site_scan_*.json" -o -name "huanyao_extracted_*.json"
)

if [[ "$INCLUDE_JSONL" == "true" ]]; then
  FIND_ARGS+=( -o -name "*.jsonl" )
fi

FIND_ARGS+=( ")" -print0 )

mapfile -d '' FILES < <(find "${FIND_ARGS[@]}")
COUNT="${#FILES[@]}"
TOTAL_BYTES=0

for f in "${FILES[@]}"; do
  if [[ -f "$f" ]]; then
    size=$(stat -c %s "$f" 2>/dev/null || echo 0)
    TOTAL_BYTES=$((TOTAL_BYTES + size))
  fi
done

{
  echo "Workspace cleanup report"
  echo "timestamp: $(date -Is)"
  echo "mode: $MODE"
  echo "workspace: $WORKSPACE"
  echo "include_jsonl: $INCLUDE_JSONL"
  echo "candidate_count: $COUNT"
  echo "candidate_total_bytes: $TOTAL_BYTES"
  echo "candidate_total_human: $(human_size "$TOTAL_BYTES")"
  echo
  echo "Candidates:"
  for f in "${FILES[@]}"; do
    rel="${f#$WORKSPACE/}"
    sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
    echo "- $rel ($(human_size "$sz"))"
  done
} > "$REPORT_FILE"

if [[ "$MODE" == "dry-run" ]]; then
  echo "[DRY-RUN] candidates: $COUNT, total: $(human_size "$TOTAL_BYTES")"
  echo "Report: $REPORT_FILE"
  exit 0
fi

if [[ "$COUNT" -eq 0 ]]; then
  echo "[APPLY] no candidates."
  echo "Report: $REPORT_FILE"
  exit 0
fi

mkdir -p "$TRASH_DIR"
MOVED=0
for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  rel="${f#$WORKSPACE/}"
  dest="$TRASH_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  mv "$f" "$dest"
  MOVED=$((MOVED + 1))
done

echo >> "$REPORT_FILE"
echo "Apply result:" >> "$REPORT_FILE"
echo "moved_count: $MOVED" >> "$REPORT_FILE"
echo "trash_dir: $TRASH_DIR" >> "$REPORT_FILE"

echo "[APPLY] moved: $MOVED file(s)"
echo "Trash: $TRASH_DIR"
echo "Report: $REPORT_FILE"
