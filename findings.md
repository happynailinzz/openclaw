# findings.md

## 2026-04-06 社交情报抓取

### Step A：技能与通道检查
- 可见技能：`xiaohongshu`（可用于小红书搜索/详情/舆情分析）
- 可见替代技能：`agent-reach`（平台接入安装/配置）、`jina-reader`（难抓页面清洗）、`tavily`（搜索）
- 当前直接可用一等工具：`web_search`、`web_fetch`、`browser`
- 当前未见 Reddit/YouTube 专属 skill；默认走 `web_search` / `web_fetch` / `browser` 兜底

