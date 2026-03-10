# Findings

## 2026-03-10
- OpenClaw 分享文档的核心定位：不要讲成“AI 聊天工具”，而要讲成“可自托管的 Agent 基础设施”。
- 部署建议明确分两套：本地 macOS + 国产模型；海外服务器 + 国外模型中转。
- 本地文档可支撑的真实经验点包括：生产化 SOP、记忆整合、cron 规则、脚本化发布、巡检与恢复。
- CLI 侧可用于分享演示的命令包括：`openclaw status`、`openclaw skills`、`openclaw plugins`、`openclaw security audit`。
- 当前工作区已经沉淀出可讲的优化案例：memory 分层、cron/heartbeat 分工、publish 脚本、HTML refined 后处理、systemd/loopback/环境变量治理。
