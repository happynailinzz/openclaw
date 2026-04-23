# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》执行一次完整流程，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出结构化简报、评分、归档与留痕。

## Phases
- [complete] 1. 读取 SOP / 历史上下文 / 设定关键词池
- [complete] 2. 多源抓取（优先 API/MCP/技能，失败则逐级回退）
- [complete] 3. 去重、评分、分层、生成固定格式简报
- [complete] 4. 分发与沉淀（Telegram、本地 memory、可检索归档）

## Constraints
- 单源失败不阻塞全流程
- 输出固定包含：发现、政务/国防 AI 供应链波动映射、依据、建议动作、低优先级观察、质量指标
- 质量目标：成功率>=85%，重复率<=20%，高价值命中率>=60%（估计）
- 周一才做 Step A skills 复查；当前为周四，默认跳过

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| X 仅返回错误壳页 | 1 | 记失败并回退到新闻/RSS/官方站点 |
| 小红书仅返回备案/壳页 | 1 | 记失败，不阻塞主流程 |
| YouTube feed 400，搜索页仅返回前端脚本 | 1 | 记失败，依赖新闻/官方站点补足 |
| browser 工具网关超时 | 1 | 按技能提示不再重试，直接记录 browser 不可用 |
