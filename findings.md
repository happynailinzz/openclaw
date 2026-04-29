# findings.md

- 2026-04-29：已发现历史 social-intel 归档在 `intel/social-intel/` 与 `memory/social-intel/`。
- 2026-04-29：上一次 2026-04-28 运行中，X/小红书/YouTube/browser fallback 失败，新闻网站与 RSS 成功。
- 2026-04-29：memory_search 当前不可用，需要在本轮结果中保留该限制。
- 2026-04-29：本轮通过 `web_fetch + jina-reader + Google News RSS + Reddit RSS` 回填，成功拿到 DefenseScoop、ai.mil、state.gov、SpaceNews、Google News RSS 等高信号源。
- 2026-04-29：X 仅返回错误/登录壳页，小红书仅返回备案页脚，browser fallback 超时不可用，需后续依赖登录态技能或网关恢复。
