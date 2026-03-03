#!/bin/bash
# auto-backup.sh - workspace 自动 Git 备份
# 由 cron 每日调用，路径：/root/.openclaw/workspace/scripts/auto-backup.sh

set -e

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "[backup] 无变更，跳过"
  exit 0
fi

# 添加所有变更（.gitignore 会自动过滤 .env 等敏感文件）
git add -A

# 提交
DATE=$(date '+%Y-%m-%d %H:%M UTC')
git commit -m "auto: daily backup ${DATE}" --allow-empty

# 推送
git push origin master

echo "[backup] 完成：${DATE}"
