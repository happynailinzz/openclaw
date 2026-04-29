# task_plan.md

## Goal
按《社交平台情报抓取 SOP（OpenClaw版）》完成一次完整社交情报抓取、评分、归档与简报输出，覆盖 X/小红书/YouTube/Reddit/新闻网站/RSS，并单列“政务/国防 AI 供应链波动映射”。

## Phases
- [complete] 1. 读取现有 SOP、历史格式与可用抓取路径
- [complete] 2. 执行多源抓取与失败回退
- [complete] 3. 结构化评分、去重、分层
- [complete] 4. 生成归档文件、memory 留痕与简报

## Constraints
- 周三运行，Step A 每周 skills 复查本轮跳过
- 单源失败不阻塞全流程
- 输出固定格式，附来源链接
- 目标质量：成功率>=85%，重复率<=20%，高价值命中率>=60%（估计）

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| memory_search 不可用（credentials/provider error） | 1 | 向结果中显式说明，改用本地文件/历史归档辅助 |
