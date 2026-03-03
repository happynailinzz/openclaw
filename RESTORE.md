# RESTORE.md - 快速恢复手册

服务器重建或迁移时，按以下顺序操作，目标：30分钟内恢复全部功能。

## 前置条件

- 能访问 GitHub `happynailinzz/openclaw`（私有仓库）
- 有 `~/.openclaw/openclaw.json` 备份（或记得各 API key）
- 有 `.baoyu-skills/.env` 备份（密钥文件）

---

## Step 1：安装 OpenClaw

```bash
npm install -g openclaw
openclaw setup
```

## Step 2：还原主配置

```bash
# 从备份还原（或手动重填）
cp /your/backup/openclaw.json ~/.openclaw/openclaw.json
openclaw gateway restart
```

关键字段：
- `models.providers.cpa.apiKey` — 主模型 API key
- `models.providers.AIcat` — AIcat 第三方配置
- `channels.telegram.botToken` — Telegram bot
- `agents.defaults.models.ai52` — 模型别名

## Step 3：还原 workspace

```bash
git clone https://github.com/happynailinzz/openclaw.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

## Step 4：还原密钥文件

```bash
# 从安全备份复制（或手动重填）
cp /your/backup/.env ~/.openclaw/workspace/.baoyu-skills/.env
```

文件位置：`~/.openclaw/workspace/.baoyu-skills/.env`
包含：微信、Notion、图片代理、Tavily、Memos、EvoMap、Baidu

## Step 5：还原 cron 任务

```bash
openclaw cron import ~/.openclaw/workspace/config/cron-export.json
# 或在 web UI 手动重建，参考 memory/ 目录下的日志
```

当前定时任务清单（备忘）：
- 每日 04:00 UTC — healthcheck
- 每日 07:30 CST — 郑州早报
- 每日 08:00 CST — 海外中文新闻
- 每日 14:00 CST — 海外中文新闻
- 每日 16:00 CST — 赛道股简报
- 每日 09:00 CST — GitHub 更新监控
- 每日 10:00 CST — 社交情报 SOP
- 每周一 10:05 CST — AI基建资本周报

## Step 6：还原知识库

```bash
# 确认 Obsidian 知识库路径
ls /opt/openclaw/knowledge/secendME

# 重建 qmd 索引
qmd collection add /opt/openclaw/knowledge/secendME --name obsidian
qmd collection add ~/.openclaw/workspace/articles --name articles
qmd collection add ~/.openclaw/workspace/memory --name memory

qmd context add qmd://obsidian "东城老饕的个人Obsidian知识库，包含行业观察、项目笔记、思考记录"
qmd context add qmd://articles "已发布或草稿状态的公众号文章"
qmd context add qmd://memory "工作记忆与项目进展日志"
```

## Step 7：还原社交平台 Cookie

```bash
# Twitter/X（需要重新从浏览器导出）
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"

# 小红书（由 mcporter 管理，检查状态）
agent-reach doctor
```

## Step 8：验证

```bash
openclaw gateway status          # 网关运行中
qmd search "源网荷储" -c obsidian # 知识库可搜索
openclaw cron list               # cron 任务在线
```

---

## 关键文件位置速查

| 文件 | 说明 |
|---|---|
| `~/.openclaw/openclaw.json` | 主配置（模型/渠道/别名）|
| `workspace/.baoyu-skills/.env` | 所有 API key 统一存放 |
| `workspace/config/` | EvoMap、Memos、mcporter 等子配置 |
| `workspace/memory/` | 工作记忆日志 |
| `workspace/articles/` | 公众号文章与配图 |
| `workspace/MEMORY.md` | 长期记忆索引 |
| `/opt/openclaw/knowledge/secendME` | Obsidian 知识库（确认备份）|

---

最后更新：2026-03-03
