# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》完成一次 2026-04-02 02:00 UTC 的社交情报抓取，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出固定版式简报，同时完成本地留痕与可检索归档。

## Phases
- [in_progress] Phase 1: 读取既有SOP/历史样例，确认输出结构与评分规则
- [pending] Phase 2: 多源抓取（主通道+失败回退）
- [pending] Phase 3: 结构化、去重、评分、分层
- [pending] Phase 4: 写入归档与memory留痕
- [pending] Phase 5: 生成固定版式简报

## Constraints
- 优先链路：API/MCP skill -> 专用脚本 -> web_fetch -> browser
- 单源失败不阻塞全流程
- 输出字段：platform/title/published_at/url/summary/signals/confidence
- 评分：核心关键词+2，高可信源+2，业务直接相关+3，营销噪音-2，重复-3
- 分层：高价值>=5；中价值2-4；低价值<=1
- 固定版式：发现/政务国防AI供应链波动映射/依据/建议动作/低优先级观察/质量指标

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files 初始路径误判 | 1 | 改读 /root/.agents/skills/planning-with-files/SKILL.md |
| 当日 memory 文件不存在 | 1 | 继续任务，稍后写入新文件 |
