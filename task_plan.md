# task_plan.md

## Goal
执行一轮升级版【河南六大重点领域项目机会监控】，按固定搜索路由完成“发现层→确认层”，输出可转化项目机会简报。

## Phases
- [complete] Phase 1: 读取上下文与确定搜索脚本/路由
- [complete] Phase 2: 发现层搜索（Tavily → cn-web-search → baidu-search → multi-search-engine）
- [complete] Phase 3: 确认层抓取（web_fetch / Jina / Scrapling）
- [complete] Phase 4: 去重、筛选高价值线索、生成简报

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| `/root/.openclaw/workspace/skills/planning-with-files/SKILL.md` 不存在 | 1 | 改读 `/root/.agents/skills/planning-with-files/SKILL.md` |
| `memory/2026-04-05.md` 不存在 | 1 | 仅读取 2026-04-04 与 MEMORY.md |
| 河南省政府/省发改委关键原文 403 | 1-4 | web_fetch / Jina / Scrapling basic / stealth 均失败，改用多源交叉确认并标记“原站受限待补” |

## Notes
- 严格区分发现层与确认层，不直接用搜索摘要当结论。
- 源头优先 A/B 类，C 类仅作线索。 
- 宁缺毋滥。每条最终结论必须带链接与状态。 
