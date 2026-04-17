# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行 2026-04-17 02:00 UTC 一轮完整 social intel 监控，覆盖 X/小红书/YouTube/Reddit/新闻网站/RSS，并输出固定格式简报、结构化归档与 memory 留痕。

## Phases
- [complete] Phase 1: 前置检查（日期、技能可用性判断、记忆路由）
- [complete] Phase 2: 多源抓取与失败回退
- [complete] Phase 3: 去重、评分、主题映射
- [complete] Phase 4: 归档、memory 留痕、简报输出

## Rules
- 本次为周五，Step A 仅记录“非周一，跳过每周复查”。
- 单源失败不阻塞全流程。
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence。
- 评分规则：核心关键词+2，高可信源+2，业务直接相关+3，营销噪音-2，重复内容-3。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| YouTube 原始 feeds/videos.xml 404 | 1 | 改走 Google News/YouTube 代理回退，保住通道成功率 |
| X 小红书缺乏高可信原生增量 | 1 | 记为弱信号/聚合回退，不阻塞主流程 |
