# 任务计划：社交平台情报抓取 SOP（OpenClaw版）

## 目标
执行一次完整的多平台情报抓取与筛选流程，输出固定格式简报，并完成本地留痕与可检索归档。

## 阶段
- [complete] Phase 1: 检查技能/通道可用性（Step A，因非周一按SOP跳过周检）
- [complete] Phase 2: 多源抓取与失败回退（Step B/C）
- [complete] Phase 3: 结构化整理与价值评分（Step D/E）
- [complete] Phase 4: 分发与沉淀（Step F，本地留痕与归档完成；Telegram 由本次返回摘要承载）
- [complete] Phase 5: 生成固定格式简报

## 约束
- 单源失败不阻塞全流程
- 输出必须包含：platform/title/published_at/url/summary/signals/confidence
- 单列“政务/国防 AI 供应链波动映射”
- 质量指标需估计成功率、重复率、高价值命中率

## 错误记录
| 阶段 | 问题 | 处理 |
|---|---|---|
| Phase 2 | 小红书搜索结果以服务市场/招聘噪音为主，未形成有效情报 | 记录为单源失效，不阻塞整体流程 |
| Phase 4 | edit 工具参数模式冲突 | 改为直接 write 覆盖计划文件 |
