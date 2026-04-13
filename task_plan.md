# task_plan.md

## Goal
执行一次《社交平台情报抓取 SOP（OpenClaw版）》完整流程，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出可评分、可归档、可复盘的 10:00 社交情报简报。

## Phases
- [complete] P1 准备：读取约束、确认是否周一、建立计划文件
- [complete] P2 Step A：skills 发现与可用性检查
- [complete] P3 Step B/C：多源抓取与失败回退
- [complete] P4 Step D/E：结构化整理、评分、去重、分层
- [complete] P5 Step F：本地归档、memory 留痕、生成摘要

## Scoring Rule
- 命中核心关键词 +2
- 高可信源 +2
- 业务直接相关 +3
- 营销噪音 -2
- 重复内容 -3

## Quality Targets
- 成功率 >=85%
- 重复率 <=20%
- 高价值命中率 >=60%
- 突发延迟 <=30 分钟

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| X bird 缺少 Cookie 凭证 | 1 | 记为 direct fail，未阻塞流程，改走新闻/RSS 回退 |
| Reddit 搜索 403 | 1 | 记为 IP/反爬受限，未阻塞流程 |
| 小红书 MCP 18060 连接拒绝 | 1 | 记为服务离线，未阻塞流程 |
| web_fetch 访问 s.jina.ai 返回 401 | 1 | 放弃该回退链路，改用 Google News RSS + 定点正文抓取 |
| YouTube yt-dlp 缺少 JS runtime | 1 | 记为 degraded，未纳入核心发现 |
