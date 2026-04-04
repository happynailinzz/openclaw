# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》完成一次完整情报抓取，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，产出可检索、可评分、可复盘、可推送的简报，并写入本地留痕。

## Phases
- [complete] Phase 1: 建立抓取计划与来源清单
- [complete] Phase 2: 多源抓取与失败回退
- [complete] Phase 3: 结构化整理、评分、去重
- [complete] Phase 4: 写入本地归档与输出简报

## Constraints
- 本次时间：2026-04-04 02:00 UTC（周六），Step A 每周复查仅周一执行，本次跳过
- 单源失败不阻塞全流程
- 输出必须包含固定栏目与质量指标

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files 路径先读错 | 1 | 改读 ~/.agents/skills/planning-with-files/SKILL.md |
| edit 工具多次因混用参数报错 | 1 | 改用 write 直接覆盖 findings/progress/task_plan |
