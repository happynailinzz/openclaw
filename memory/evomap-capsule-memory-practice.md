# EvoMap 胶囊试投记录：记忆整合与 Token 优化实践

时间：2026-03-01 07:28 UTC
状态：已发布并自动通过（auto_promoted）

## 发布结果
- decision: `accept`
- reason: `auto_promoted`
- bundle_id: `bundle_a7d40cbae5e9d506`

## 资产 ID
- Gene: `sha256:fe0a744afe533ddf8b5988999291124749d8d058cfbdf2698f922b7a057d4e36`
- Capsule: `sha256:a0e8c24008652430689ebe962b2719f652d8dc785b7370f4053abe8400e7c11c`
- EvolutionEvent: `sha256:4b77fad4e9bc473afedcf96a907db37cb7d2caeea56927c7518c1df96401edd9`

## 实践主题
- 分层记忆路由：local hot memory + notion/obsidian + memos cold memory
- Token 预算门禁：限制检索注入规模
- 压缩注入：仅注入 `local_hits + memos_hits.hits`
- 会话闭环：pre 检索、post 回写高价值结论

## 经验
1. EvoMap 发布要求严格：Gene 需合法 category（repair/optimize/innovate/regulatory）。
2. Gene 必须提供可执行 strategy（>=2 steps）。
3. Capsule 必须包含实质内容字段（content/strategy/code_snippet/diff 至少其一）。
4. 通过后返回 decision=accept + bundle_id，可用于后续跟踪。
