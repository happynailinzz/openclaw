# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行 2026-04-25 02:00 UTC 一轮完整 social intel 监控，覆盖 X/小红书/YouTube/Reddit/新闻网站/RSS，并输出固定格式简报、结构化归档与 memory 留痕。

## Phases
- [complete] Phase 1: 前置检查（日期、记忆路由、上轮复盘）
- [complete] Phase 2: 多源抓取与失败回退
- [complete] Phase 3: 去重、评分、主题映射
- [complete] Phase 4: 归档、memory 留痕、简报输出

## Rules
- 本次为周六，Step A 仅记录“非周一，跳过每周复查”。
- 单源失败不阻塞全流程。
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence。
- 评分规则：核心关键词+2，高可信源+2，业务直接相关+3，营销噪音-2，重复内容-3。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| YouTube 搜索页仅返回前端脚本壳 | 1 | 记失败回退，不阻塞主流程 |
| X 返回错误壳页 | 1 | 记失败回退，不阻塞主流程 |
| 小红书聚合回退无命中 | 1 | 记失败回退，整体流程继续 |
| browser 网关超时 | 1 | 停止重试，按 SOP 记 browser 兜底失败 |
