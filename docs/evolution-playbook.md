# Evolution System Playbook（EvoMap × Capability Evolver × Self-Improving × Proactive）

> 目标：让进化系统“稳定产出”，而不是“频繁折腾”。

## 0) 基线原则（必须遵守）

1. **半自动优先**：默认 `--review`，不直接自动改核心代码。
2. **小步迭代**：每周仅上线 1-2 条高价值改进。
3. **可回滚**：每次改动前后都可追踪（git + 日志）。
4. **结果导向**：只保留能提升命中率/效率/稳定性的进化。

---

## 1) 组件分工

- **EvoMap (`scripts/evomap-runner.js`)**：发现高价值任务/信号
- **Capability Evolver**：从历史中生成“可执行进化候选”
- **Self-Improving**：沉淀纠错与偏好（避免重复犯错）
- **Proactive Agent**：巡检、提醒、节奏化执行

---

## 2) 日常节奏（Daily）

### 每日自动（已有）
- social-intel cron（10:00 Asia/Shanghai）
- memory daily flush（03:00 UTC）
- 心跳 + EvoMap runner

### 每日人工（5-10分钟）
1. 跑环境检查：
   ```bash
   bash scripts/check-evolution-env.sh
   ```
2. 跑 evolver 审核模式：
   ```bash
   bash scripts/run-evolver-review.sh
   ```
3. 把当日关键纠错写入：
   - `~/self-improving/corrections.md`

---

## 3) 周节奏（Weekly）

每周固定一次（建议周一 10:30 Asia/Shanghai）：

1. 汇总候选：
   - `memory/evomap-evolution-candidates.md`
   - `memory/evomap-state.json`
2. 选 1-2 条高价值候选（按影响/风险/可验收）
3. 人工审查后上线
4. 记录“上线前后效果”到 `memory/lessons.md`

### 候选优先级（从高到低）
1. 减少重复劳动（可量化节省时长）
2. 提高信息命中率（更少漏报/误报）
3. 提升交付稳定性（失败率下降）

---

## 4) 月节奏（Monthly）

1. 清理失效规则与低价值候选
2. 回顾近30天：
   - 成功上线数
   - 回滚数
   - 产出提升点
3. 更新 `MEMORY.md`（仅保留长期有效规则）

---

## 5) 风险闸门（Go / No-Go）

满足以下才允许上线：

- [ ] 不涉及密钥/凭据/外部敏感数据
- [ ] 变更范围明确且可回滚
- [ ] 通过 `security-scanner` 和人工复核
- [ ] 有清晰验收标准（命中率、耗时、错误率至少一项）

任一不满足：**延期上线**。

---

## 6) 一键命令清单

```bash
# 环境就绪检查
bash scripts/check-evolution-env.sh

# 进化审核模式
bash scripts/run-evolver-review.sh

# EvoMap 心跳/任务探测
node scripts/evomap-runner.js

# Proactive 安全体检
bash skills/proactive-agent/scripts/security-audit.sh
```

---

## 7) 每周提醒 Cron（模板，仅提醒，不自动改代码）

> 可在 OpenClaw Cron 中新增一个 job，prompt 仅做“候选评审提醒”。

- 名称：`evolution:weekly-review:mon1030`
- 表达式：`30 10 * * 1`
- 时区：`Asia/Shanghai`
- Prompt 示例：

```
请执行本周进化评审（只评审，不自动改代码）：
1) 读取 memory/evomap-state.json 与 memory/evomap-evolution-candidates.md
2) 给出Top 3候选（影响/风险/验收标准）
3) 明确推荐最多2条进入上线队列
4) 若无高质量候选，回复“本周不发布进化改动”
```

