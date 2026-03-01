# OpenClaw 记忆整合部署说明

## 1. 配置文件
- `config/memos.env`（私密，不入库）
- `config/memory-integration.json`（公开配置）

## 2. 脚本
- `scripts/memos-client.py`
  - `add <text> [user_id] [conversation_id]`
  - `search <query> [user_id] [conversation_id]`
- `scripts/memory-retrieval-router.py <query> [user_id] [conversation_id]`

## 3. 快速验证
```bash
python3 scripts/memos-client.py add "测试：我喜欢云吞"
python3 scripts/memos-client.py search "喜欢吃什么"
python3 scripts/memory-retrieval-router.py "记忆优化方案"
```

## 4. 一键会话循环（推荐）
```bash
scripts/memory-cycle.sh pre  "OpenClaw 记忆整合部署"
scripts/memory-cycle.sh post "已完成分层记忆与混合检索接入"
```

## 5. 调用接入建议
- 回答前：调用 `memory-cycle.sh pre`（或 `memory-retrieval-router.py`）
- 回答后：调用 `memory-cycle.sh post` 写入关键结论
- 为节省 token：仅注入精简证据片段，不注入完整原始返回
- 公众号相关任务：在路由中加入 Notion「文章选题草稿箱」作为优先检索源之一（与 Obsidian 并行）
- 周期维护：按 `memory/memory-maintenance-sop.md` 执行

## 6. 回滚
- 停用 Memos：移除 `config/memos.env` 或将路由脚本中的 memos 调用注释
- 保留本地记忆：`memory/` + `MEMORY.md` 继续可用
