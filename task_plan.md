# 社交情报抓取任务计划

## 目标
按《社交平台情报抓取 SOP（OpenClaw版）》执行一次完整流程，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出结构化情报、评分分层、供应链波动映射、归档与推送摘要。

## 阶段
- [complete] A. 周一 skills 发现与可用性检查
- [complete] B. 多源抓取与失败回退
- [complete] C. 结构化整理与评分
- [complete] D. 生成简报、归档、记忆留痕

## 约束
- 单源失败不阻塞全流程
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence
- 质量目标：成功率>=85%，重复率<=20%，高价值命中率>=60%（估计）
- 新增一级主题：政务/国防 AI 供应链波动映射

## 错误记录
| 错误 | 尝试 | 处理 |
|---|---:|---|
| planning skill 首次路径读取失败 | 1 | 改读 ~/.agents/skills/planning-with-files/SKILL.md |
| X 抓取失败 | 1 | web_fetch 壳页；browser 超时，按 SOP 回退 |
| YouTube 抓取失败 | 1 | web_fetch 仅前端脚本；browser 超时，按 SOP 回退 |
| 小红书抓取失败 | 1 | web_fetch fetch failed；browser 超时，按 SOP 回退 |
