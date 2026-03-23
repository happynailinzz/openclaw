【10:00 社交情报简报】
生成时间：2026-03-23 02:00 UTC（定时任务）
任务：monitor:social-intel-sop:1000
SOP：社交平台情报抓取 SOP（OpenClaw版）

Step A（周一技能复查）
- xiaohongshu：未发现专用可调用skill（当前环境无直接 xiaohongshu MCP）；回退链路=web_fetch/browse。
- reddit：无专用skill，但可通过Tavily+Reddit源链接抓取；回退链路可用。
- youtube：无专用skill，但可通过Tavily+YouTube链接抓取；回退链路可用。
- 替代技能：cn-web-search、multi-search-engine、agent-reach（当前未启用直接平台写入/读取接口）。

Step B/C 执行摘要
- 主通道：Tavily（news/general）+ web_fetch（Reuters/Google News RSS）。
- 失败回退：
  - X：站内直抓不稳定，回退到 site:x.com 检索与聚合源。
  - 小红书：检索可达但正文抽取不足，记录为低价值观察，不阻塞。
  - YouTube：搜索结果噪音高，优先保留机构/智库来源并降权处理。

Step D 结构化情报（抽样）
1) platform=新闻网站 | title=US Commerce Department withdraws planned rule on AI chip exports | published_at=2026-03-13 | url=https://www.reuters.com/business/us-commerce-department-withdraws-planned-rule-ai-chip-exports-government-website-2026-03-13/ | summary=美国商务部撤回AI芯片出口规则草案，政策进入再校准窗口。 | signals=[出口管制,AI芯片,政策变动] | confidence=0.90
2) platform=新闻网站 | title=US charges 3 tied to Super Micro Computer with helping smuggle billions of dollars of AI chips to China | published_at=2026-03-19 | url=https://www.reuters.com/world/us-charges-three-people-with-conspiring-divert-ai-tech-china-2026-03-19/ | summary=美国起诉涉AI芯片走私链条人员，执法强度上行。 | signals=[执法,走私,供应链风控] | confidence=0.89
3) platform=新闻网站 | title=Exclusive: Nvidia preparing Groq chips that can be sold in Chinese market, sources say | published_at=2026-03-17 | url=https://www.reuters.com/world/china/nvidia-preparing-groq-chips-that-can-be-sold-chinese-market-sources-say-2026-03-17/ | summary=厂商推进合规改型芯片，说明“限制-适配-再供给”路径持续。 | signals=[芯片替代,合规产品,对华供给] | confidence=0.87
4) platform=Reddit | title=Daily Discussion Friday 2026-03-13 (r/AMD_Stock) | published_at=2026-03-13 | url=https://www.reddit.com/r/AMD_Stock/comments/1rsd4o9/daily_discussion_friday_20260313/ | summary=投资者侧持续跟踪AI芯片出口草案与产业链风险传导。 | signals=[市场情绪,出口草案,产业链预期] | confidence=0.62
5) platform=YouTube | title=Optimizing U.S. Export Controls for Critical and Emerging Technologies | published_at=未知 | url=https://www.youtube.com/watch?v=VLB84OD-3nI | summary=CSIS持续讨论出口管制框架优化，对政策方向有参考价值。 | signals=[智库观点,出口管制,政策预期] | confidence=0.64
6) platform=X | title=Ryan Fedasiuk Highlights（AI/出口管制相关讨论） | published_at=滚动 | url=https://x.com/RyanFedasiuk/highlights | summary=X侧政策讨论热度高，但观点分化与噪音并存。 | signals=[舆情扩散,政策解读,军工AI] | confidence=0.55
7) platform=小红书 | title=AI出口管制检索（有效正文不足） | published_at=null | url=https://www.xiaohongshu.com/search_result?keyword=AI%20%E5%87%BA%E5%8F%A3%E7%AE%A1%E5%88%B6 | summary=检索页可访问，但本轮未获得高置信正文情报。 | signals=[平台可达,正文缺失] | confidence=0.95
8) platform=RSS | title=Google News RSS: AI chip export controls (7d) | published_at=2026-03-23 | url=https://news.google.com/rss/search?q=AI+chip+export+controls+when:7d&hl=en-US&gl=US&ceid=US:en | summary=近7天持续出现出口管制与地缘风险相关新闻聚合。 | signals=[新闻聚合,趋势验证] | confidence=0.76

Step E 评分与分层
- 评分规则：核心关键词+2，高可信源+2，业务直接相关+3，营销噪音-2，重复内容-3。
- 高价值（>=5）：#1 #2 #3
- 中价值（2-4）：#4 #5 #6 #8
- 低价值（<=1）：#7

Step F 沉淀
- 本地归档：已写入本报告 + latest_structured.json + 当日jsonl。
- Telegram：应推送“高+中价值摘要”（由上游定时通道投递）。
