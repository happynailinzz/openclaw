# task_plan.md

## 任务
执行一次《社交平台情报抓取 SOP（OpenClaw版）》完整流程，输出 2026-04-09 10:00 社交情报简报，并完成本地留痕与可检索归档。

## 阶段
- [complete] 1. 读取已有 SOP / 历史样本 / 约束
- [complete] 2. 多渠道抓取（X / 小红书 / YouTube / Reddit / 新闻 / RSS）
- [complete] 3. 回退、去重、评分、分层
- [complete] 4. 生成简报 + 本地归档 + memory 留痕

## 约束
- Step A 仅周一执行技能复查；今天是周四，跳过。
- 主链路优先：API/MCP skill -> 专用脚本 -> web_fetch -> browser。
- 单源失败不得阻塞全流程。
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence。
- 必须单列【政务/国防 AI 供应链波动映射】。
- 质量目标：成功率>=85%，重复率<=20%，高价值命中率>=60%（估计）。

## 错误记录
| 错误 | 尝试 | 处理 |
|---|---:|---|
| memory/2026-04-08.md 与 2026-04-09.md 不存在 | 1 | 继续使用现有历史情报与归档样本，不阻塞 |
| planning-with-files 路径初次猜错 | 1 | 改读 /root/.agents/skills/planning-with-files/SKILL.md |
| edit 工具单次更新参数校验失败 | 1 | 改用 write 直接覆盖规划文件 |
