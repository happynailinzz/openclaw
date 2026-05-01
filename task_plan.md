# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行一次完整社交情报抓取，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出固定格式简报、结构化归档与本地记忆留痕。

## Phases
- [complete] 1. 读取既有样本/SOP痕迹并确定本轮执行约束
- [complete] 2. 抓取各平台主源与回退源
- [complete] 3. 结构化去重、评分、分层、生成政务/国防 AI 供应链波动映射
- [complete] 4. 归档 JSON / 更新 memory / 输出简报

## Decisions
- 今日为周五，按 SOP 跳过 Step A 每周 skills 复查。
- 主抓取优先 web_fetch/RSS；对受限源保留失败样本并走回退，不因单源失败阻塞。
- 参考既有 social-intel 归档格式，保持字段兼容：platform/title/published_at/url/summary/signals/confidence。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| memory/2026-05-01.md 不存在 | 1 | 视为今日记忆尚未创建，后续已新建 |
| X 搜索页仅返回错误壳页 | 1 | 记为失败样本，不阻塞主流程 |
| 小红书公开页仅返回备案信息 | 1 | 记为失败样本，不阻塞主流程 |
