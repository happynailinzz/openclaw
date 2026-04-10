# task_plan.md

## 任务
执行一次《社交平台情报抓取 SOP（OpenClaw版）》完整流程，覆盖 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS，并输出固定格式简报。

## 阶段
- [x] Phase 1：读取约束与确定执行框架
- [x] Phase 2：主通道抓取（web_search / web_fetch）
- [x] Phase 3：失败回退（补抓小红书、RSS、X）
- [x] Phase 4：结构化、评分、筛噪
- [x] Phase 5：本地归档与 memory 留痕
- [x] Phase 6：生成简报

## 关键决策
- 今日为周五，不执行“仅周一触发”的 skills 复查。
- 主通道优先用 web_search + web_fetch；X 与小红书因可访问性差，采用搜索摘要与页面可见片段回退。
- 高价值判断以“政策动作 + 厂商影响 + 交付影响”优先。

## 错误 / 风险
| 问题 | 处理 |
|---|---|
| skill 路径与注入路径不一致 | 用本机路径探测修正 |
| 小红书多数结果落到受限/失效页 | 记为弱命中，仅保留可见摘要 |
| X 未拿到稳定高质量状态页结果 | 记为部分失败，不阻塞全流程 |
| FDD 页面被 Cloudflare 拦截 | 改用 Reuters / NBC / IST / RAND 等替代高可信源 |

## 输出文件
- `findings.md`
- `progress.md`
- `data/social-intel/2026-04-10-social-intel.json`
- `data/social-intel/2026-04-10-briefing.md`
- `memory/2026-04-10.md`
