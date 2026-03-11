# 《AI 众生相——OpenClaw 热度下的国内厂商图谱》证据清单

作者：余炜勋
时间：2026-03-10

## 选题收束

本篇只聚焦“已经有明确动作落地”的厂商，不写泛 Agent 叙事，不写尚未与 OpenClaw 明确挂钩的推演性厂商。

## 可写厂商

### 1. 阿里云
- 动作：推出“分钟级部署 OpenClaw”商业页，强调 7x24 在线、轻量应用服务器承载、企业微信/QQ/钉钉/飞书接入、Coding Plan 组合套餐。
- 动作：提供 OpenClaw 对接阿里云百炼模型的官方文档，明确模型列表、Base URL、API Key、安装与配置步骤。
- 可写判断：阿里云并不是只提供模型接口，而是在把 OpenClaw 包成“云资源 + 模型 + IM 接入 + 可视化配置”的一体化上云产品。
- 来源：
  - https://www.aliyun.com/activity/ecs/clawdbot
  - https://help.aliyun.com/zh/model-studio/openclaw

### 2. 百度智能云 / 千帆
- 动作：推出“千帆 OpenClaw 一键体验”，强调 3-5 分钟部署、免费计算资源支持、百度官方 Skills、代金券与 Coding Plan。
- 动作：推出“快速部署 OpenClaw 定制 AI 助手”落地页，包含轻量服务器/BCC、Tokens 包、百度搜索/百科/学术/PPT 等官方 Skills、7x24 运行叙事。
- 可写判断：百度是把 OpenClaw 直接吸纳进自家的 Agent 开发平台与 Skill 分发生态中，目标不是单点部署，而是让 OpenClaw 成为千帆能力调用入口。
- 来源：
  - https://qianfan.cloud.baidu.com/qianfandev/topic/687768
  - https://cloud.baidu.com/product/BCC/moltbot.html

### 3. 腾讯云
- 动作：已有 OpenClaw 云应用页。
- 动作：开发者社区已有“云上 OpenClaw 快速接入企业微信指南”等教程内容。
- 可写判断：腾讯云当前动作更偏向“云应用承载 + 国内 IM 接入 + 开发者教育”，本质是在抢入口与接入场景。
- 来源：
  - https://app.cloud.tencent.com/detail/SPU_BHGJGAFIIJ7195
  - https://cloud.tencent.com/developer/article/2625147

### 4. 火山引擎
- 动作：文档体系里已将 OpenClaw（原 Moltbot）单列为 AI 应用，围绕飞书、企业微信、钉钉、QQ 等给出快速部署文档。
- 动作：延伸到“部署 AI 助手安全服务”等能力。
- 可写判断：火山引擎不是只做教程，而是在把 OpenClaw 纳入“开发者部署模板 + 企业办公入口 + 安全运维增强”的产品线。
- 来源：
  - https://www.volcengine.com/docs/6396/2189942
  - https://www.volcengine.com/docs/6396/2222366

### 5. 中科曙光
- 动作：官网文章明确写出“5分钟部署！曙光云 × Moltbot革新行业智能体”。
- 动作：强调与行业大模型、数据处理能力、行业智能体平台联动，支持应用镜像、私有化部署、安全可信底座。
- 可写判断：曙光云不是在卖“通用助手热度”，而是在把 OpenClaw/Moltbot 收编进“行业智能体 + 安全可信 + 私有化部署”的政企交付框架。
- 来源：
  - https://www.sugon.com/cut?id=2805&nav_id=48

## 当前不写的厂商/方向
- 华为：当前拿到的是更泛化的 Agent 网络 / AgenticCore 证据，与 OpenClaw 直接绑定不足。
- 浪潮云：有上位叙事和搜索结果，但当前缺少足够直接的 OpenClaw 落地原文证据；可放下一篇。
- 地方/政策/园区：泛 AI 与算力券信号有，但与 OpenClaw 直接挂钩证据不足，先不写。

## 文章主判断
- OpenClaw 热度起来后，国内厂商不是在同一种方式跟进，而是分别往自己最擅长的商业环节去收：
  - 阿里云：云资源 + 模型 + IM 接入 + 可视化配置
  - 百度：Agent 平台 + Skills 生态 + 算力/代金券
  - 腾讯云：云应用入口 + 企业微信/飞书等场景接入
  - 火山引擎：开发者模板化部署 + 办公入口 + 安全服务
  - 中科曙光：行业智能体 + 私有化 + 安全可信 + 行业交付
- 所谓“AI 众生相”，真正要写的不是一个开源项目火了，而是这波热度把不同厂商的商业姿态照了出来。
