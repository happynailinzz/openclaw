# task_plan.md

## Goal
执行一轮升级版「河南六大重点领域项目机会监控」，按固定结构输出高价值新增动作与可转化项目机会。

## Phases
- [complete] Phase 1: 检索路由与候选收集
- [complete] Phase 2: 正文确认与源头分级
- [in_progress] Phase 3: 机会提炼与简报输出

## Notes
- 优先官方/权威源；搜索摘要不能直接当结论。
- 若正文抓取失败，按既定 fallback 记录状态。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files 初始路径不在 workspace | 1 | 改读 ~/.agents/skills/planning-with-files/SKILL.md |
| Baidu Search 高频并发触发 429 | 1 | 降低并发，转 Jina/web_fetch 做正文确认 |
| 部分政采页 web_fetch 抽正文失败 | 1 | 改用 Jina Reader 抓正文 |
