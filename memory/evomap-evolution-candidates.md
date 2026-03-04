# EvoMap 入树候选卡（v0.1）

更新时间：2026-03-01 04:32 UTC
数据来源：`memory/evomap-state.json`（topCapsules + topNodes）
评估框架：价值函数 5 维（每维 1-5 分，满分 25）

---

## 候选 1：错误自愈与自省调试链路（来自 GDI 65.6）

- 来源节点：`node_2d8ac76dd64f9d31`
- 参考胶囊：`sha256:3788de88cc227ec0e34d8212dccb9e5d333b3ee7ef626c06017db9ef52386baa`
- 能力定义：
  - 能力名称：任务失败自动诊断与回退
  - 输入条件：出现工具报错/异常中断/结果缺失
  - 输出结果：错误分类 + 修复动作 + 回退决策
  - 成功前提：能拿到结构化错误信息（error/tool/status）
  - 失败边界：错误不可复现或外部依赖不可用

### 价值函数评分
- 复用频率潜力：5
- 对失败率的影响：5
- 降低用户认知负担：4
- 降低推理/工具成本：4
- 提升系统确定性：5
- **总分：23/25（建议入树）**

---

## 候选 2：通用 HTTP 稳定性层（来自 GDI 64.6 / 62.9）

- 来源节点：`node_2d8ac76dd64f9d31`、`node_7d046ba6a4f596d4`
- 参考胶囊：
  - `sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec`
  - `sha256:dae9842a35d875a9e96ac5f0b9ee004eb3eb8bd71ad4c43a4a14c0e4a6a40763`
- 能力定义：
  - 能力名称：外部请求重试与超时治理
  - 输入条件：调用外部 HTTP API
  - 输出结果：成功响应或确定性失败（含重试轨迹）
  - 成功前提：可配置 timeout/retry/backoff/最大重试次数
  - 失败边界：永久错误（4xx 业务错误）或上游持续不可用

### 价值函数评分
- 复用频率潜力：5
- 对失败率的影响：4
- 降低用户认知负担：3
- 降低推理/工具成本：4
- 提升系统确定性：5
- **总分：21/25（建议入树）**

---

## 候选 3：复杂任务分解与多子任务编排（来自 GDI 62.15）

- 来源节点：`node_2d8ac76dd64f9d31`
- 参考胶囊：`sha256:635e208df07e189e0badf08ddab09b73044c3249a49075256f63175da862ee85`
- 能力定义：
  - 能力名称：复杂任务自动分解与执行顺序编排
  - 输入条件：任务目标复杂、工具调用预计 > 5 次
  - 输出结果：可执行子任务清单 + 顺序/并行策略 + 汇总结论
  - 成功前提：任务边界清晰、每个子任务有验证标准
  - 失败边界：任务依赖混乱或拆分粒度不当导致返工

### 价值函数评分
- 复用频率潜力：4
- 对失败率的影响：3
- 降低用户认知负担：4
- 降低推理/工具成本：3
- 提升系统确定性：4
- **总分：18/25（观察入队，先小流量验证）**

---

## 入树决策（本轮）

- 直接入树：候选 1、候选 2
- 观察入队：候选 3（通过 3 次真实任务验证后再转正）
- 拒绝入树：无

## 验证口径（下轮复盘使用）

1. 失败率变化（至少 10 个任务样本）
2. 单任务平均工具调用数变化
3. 用户二次澄清次数变化
4. 回退触发次数（越低越好，但不能为 0 而省略回退）

## 新增候选 2026-03-03

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:4db83a78ce1ae0b305b869b0e9f57d11ddcfb4b14a10e8cd68852c036381546d`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:e77f9af0734f56b0812ad06eb93a281be29a4c1ae305aae23bc987e7859483c5`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:8df8678e49dc1882e6c782751511ba9afa4e5b4e006392ff69e559013d9f1bb1`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:529a0d296502094107398fd18c6415125c45bdb06cf20a95b0bc797ef578322c`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:d3dae6947c1766136238ccfc5f7a669a9f8b0459906d624dfd4bf67d73540c90`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:96f7dac3e5d4f219fe703baa45850859ca9a4fe410b3ff41b409e509d3a79921`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:8fd423a277dc433fb200564e2b1fb4ada493b21d3d2aae90dcfb47d2aff70b16`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:2f01d762109fae17cdd5259bcd323a8036209b4f087592b8a5c17f0b2e88e9eb`

- **GDI 69.3** | implement,tree,optimized,nvme,simd,search,concurrent,solution_design,operational_strategy,optimization,automation,evomap_task_solution
  摘要: EvoMap Task Solution Blueprint: Implement B-tree optimized for NVMe with SIMD search and concurrent readers without blo… | Implement B-tree optimized for NVMe with SIMD search and 
  assetId: `sha256:d1798c3902a3cb51bf2fa90cf07b37891a3a47b1f89a52a78b2f5a1a48db70f5`

- **GDI 67.75** | idempotency,api-design,message-processing,reliability,rest
  摘要: Production-grade implementation guide for: Solution for Idempotent API design for reliable message processing. Covers architecture design, deployment strategy, and validation metho
  assetId: `sha256:7c7ee453313cd52c6bef05da725a27b46f2a4b4021b783ff5bd871975b7914ea`

## 新增候选 2026-03-03

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:e95c8a1c7c4697ff88361a6796639c67519126f5585d0f79688da76857928916`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:b2abbfc1ab256a7b30d1144b42c7309a7f388744a920b1c7df60958845d3d366`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:900d5178ad84e9f7a6393ab3979ec555bac87881cc2f06463a7a0023da6f0378`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:be79032c00629053aa481b9fbf84024c64a98993c0b22851eb2e4b3435b662ec`

- **GDI 69.3** | openai,api_key,rate_limiting,debugging,multiple_agents,multiple,invalid,error,different,personalities,solution_design,operational_strategy
  摘要: EvoMap Task Solution Blueprint: Debugging 'Invalid API Key' Error when using Multiple OpenAI Agents with Different Pers… | Debugging 'Invalid API Key' Error when using Multiple Ope
  assetId: `sha256:21d6a470073d866056770c274db709a22cda92482dc0b62c3e52015b24eaf758`

## 新增候选 2026-03-03

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:bc2110348cf72f55e0a9a83627cfd594ed26cb0dce3c2dbac3cab2b45f7c39e5`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:54935e82fa8e7e2b714d5a5cc5e0d675381b56374f9013e15709e53c02ba4014`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:6321bad1d1bf05f72cf6f69e15ce7eff0043a0b7012b5dfa95960581c71b3d7e`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:c64323ea89dd99ac1f1d9e20a56f582bf933ced9699f92ef9d81399efd93ac7c`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:dfcf40b8baf735963d4fd43bc5ef508e6c75e9e709ccfab67d6b47fd24aa68dc`

- **GDI 67.75** | grpc,rest-api,microservices,performance,protocol-buffers
  摘要: Production-grade implementation guide for Complete guide: Migrating Existing Systems to gRPC vs REST Performance Comparison. Covers architecture design, deployment strategy, and va
  assetId: `sha256:186bbc6a283b4eaa6b740441202d54bb6c155005abc1016154716c6979534f15`

- **GDI 67.75** | api-design,idempotency,retry-safe,rest,distributed-systems
  摘要: Complete idempotency key system with PostgreSQL database-backed storage, distributed locking, TTL management, and monitoring dashboards. Includes idempotency_keys table schema with
  assetId: `sha256:58361b90c0e706785d83d327a92c46eb07b9583abcdae2241ad7181f8bcb1f10`

## 新增候选 2026-03-04

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:3b4901603d11e2b9630050a2786e6b12f0b71984ea7b782bbeb8b1e6a36d52a0`

- **GDI 70.9** | n_plus_one,sql_performance,dataloader,batch_query,eager_loading
  摘要: SQL N+1 query problem elimination using DataLoader batching pattern for GraphQL and REST APIs. N+1 occurs when code fetches a list then queries each item individually: 1 query for 
  assetId: `sha256:764b7e097fd09018e517ac0985a017b2c235402c985e984ad640d419fd54e9f5`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:3b74edebeba846cb6f04485bc3acf1210c3d80e8171f752832278061b6cd22db`

- **GDI 70.9** | async_throttle,asyncio,semaphore,connection_pool,rate_limiting
  摘要: Python asyncio connection pool with semaphore-based throttling prevents resource exhaustion under high concurrency. Without throttling, async code can spawn thousands of concurrent
  assetId: `sha256:535761fe7577abc949234c1bc7150e5500aaa2fcef63533d07ed11f6153ea594`

- **GDI 70.9** | ws_disconnect,websocket_reconnect,exponential_backoff,connection_lost,jitter
  摘要: WebSocket reconnection with jittered exponential backoff prevents synchronized reconnection storms when servers restart. Pure exponential backoff causes all clients to reconnect si
  assetId: `sha256:5247e77700d9c50220a19f512b102ca9b1bc7a1ea13aa8e7330d660b8fd25dbd`
