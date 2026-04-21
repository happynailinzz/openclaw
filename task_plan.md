# 社交情报抓取任务计划

- 任务：执行一次《社交平台情报抓取 SOP（OpenClaw版）》完整流程
- 时间：2026-04-21 02:00 UTC
- 目标：抓取 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS 情报，完成评分、筛噪、归档与简报

## Phase
- [complete] 1. 检查上下文与SOP要求
- [complete] 2. 多源抓取与失败回退
- [complete] 3. 结构化整理、评分、去重
- [complete] 4. 本地归档与memory留痕
- [in_progress] 5. 输出固定格式简报

## 关键约束
- 周一才执行 skills 复查；本次为周二，跳过 Step A
- 单源失败不阻塞
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence
- 评分分层：高价值>=5；中价值2-4；低价值<=1
- 不直接外发 Telegram，只注明应推送位置

## 错误记录
| 错误 | 尝试 | 处理 |
|---|---:|---|
| memory/2026-04-21.md 不存在 | 1 | 视为新一天，后续创建 |
| Reuters / BIS / FTI 等部分源不可直取 | 1 | 按SOP回退到其他新闻源与政府/政策替代源 |
| X / 小红书 / YouTube 提取不稳定 | 1 | 记为失败/部分成功，不阻塞全流程 |
