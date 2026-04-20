# 2026-04-20 02:00 UTC 社交情报抓取报告

- 执行一次 `monitor:social-intel-sop:1000` 社交情报抓取。
- 今日为周一，已按 SOP 执行 skills 复查：
  - 已发现可用：`xiaohongshu`、`write-xiaohongshu`、`agent-reach`、`daily-trending`、`jina-reader`、`find-skills`
  - 缺少直连技能：`reddit`、`youtube`、`x`
  - 回退链路：Reddit RSS / Google News RSS / web_fetch
- 本轮高价值发现集中在三条：
  1. 美国继续把限制从 AI 芯片延伸到芯片制造设备与服务，上游链波动仍在扩大；
  2. 白宫与 Anthropic 会谈，说明国防 AI 采购对模型厂商的风险认定仍在高位，但政策口径存在调整窗口；
  3. GSA 新 AI 条款继续把责任、披露、审计与人工兜底前置到政府承包商合同。
- 通道情况：News/RSS 成功；Reddit 成功但噪音高；YouTube 通过 Google News 回退且相关性不足；X 仅弱信号回退；小红书回退无命中。
- 结构化归档：`intel/social-intel/2026-04-20-0200-social-intel.json`
- 报告归档：`memory/social-intel/2026-04-20-0200-social-intel-report.md`
- 估计质量：成功率 83.3%，重复率 15%，高价值命中率 67%。
- 质量判定：重复率与高价值命中率达标，成功率略低于 85% 目标，主要卡在 X / 小红书 / YouTube 公开通道可用性不足。
