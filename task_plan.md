# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行一次完整社交情报抓取，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，完成结构化归档、评分筛噪、简报输出与本地留痕。

## Phases
- [complete] 1. 读取 SOP / 既有产物 / 建立执行框架
- [complete] 2. 多源抓取（按优先级与失败回退）
- [complete] 3. 结构化整理、评分、去重、分层
- [complete] 4. 生成简报、归档、memory 留痕

## Constraints
- 今天是周三，Step A（每周一 skills 复查）本次跳过。
- 单源失败不阻塞全流程。
- 输出固定格式，含新增一级主题“政务/国防 AI 供应链波动映射”。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files 初始路径误判 | 1 | 改读 /root/.agents/skills/planning-with-files/SKILL.md |
| Reddit 正文抓取失败（403） | 1 | 降级为搜索结果级舆情源，不纳入硬结论 |
| RSS 抓取失败（502） | 1 | 记为单源失败，不阻塞全流程 |
| 小红书搜索高噪音 | 1 | 标记失败并剔除核心结论，避免污染结果 |
