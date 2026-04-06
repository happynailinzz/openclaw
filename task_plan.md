# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行一次完整流程，产出 2026-04-06 02:00 UTC 的社交情报简报，并完成本地留痕与归档。

## Phases
- [complete] Phase 1: 检查 SOP / 技能可用性 / 制定抓取策略
- [complete] Phase 2: 多平台抓取与失败回退
- [complete] Phase 3: 结构化整理、评分、去重
- [complete] Phase 4: 写入归档与 memory 留痕
- [complete] Phase 5: 输出固定格式简报

## Constraints
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence
- 必须单列：政务/国防 AI 供应链波动映射
- 单源失败不阻塞全流程
- 输出 plain text

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| memory/2026-04-06.md 不存在 | 1 | 视为当天尚未留痕，后续创建 |
| edit 工具参数冲突 | 1 | 改用 write 全量覆盖 task_plan.md |
