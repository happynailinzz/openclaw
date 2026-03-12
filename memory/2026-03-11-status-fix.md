# Session: 2026-03-11 07:08:03 UTC

- **Session Key**: agent:main:main
- **Session ID**: 899fe2d2-af2e-4eb6-892c-cf5896130d26
- **Source**: telegram

## Conversation Summary

assistant: [[reply_to_current]] 查清了，刚才那条 `install=unknown; channel=unknown; latest=unknown` 本质上是**状态摘要脚本没取到值，不是系统整体挂了**。

现在实际情况是：
- `install`：OpenClaw 主体是正常装着的，`openclaw status` 能正常返回
- `channel`：当前已加载的是 `Telegram`，不是 unknown
- `latest`：我这次没直接看到版本更新摘要字段，但当前运行实例是 `OpenClaw 2026.3.8`

所以那条回执的问题，不是“啥都不知道”，而是**摘要逻辑拿字段失败后直接把 unknown 往外吐了**。  
结论你可以按人话理解成：**服务正常，Telegram 正常挂着，当前版本是 2026.3.8；坏的是摘要脚本，不是主服务。**
user: System: [2026-03-11 04:22:17 UTC] Exec completed (lucky-fa, code 0) :: . │ │ │ ✗ missing │ 📨 imsg │ iMessage/SMS CLI for listing chats, history, and sending │ openclaw-bundled │ │ │ │ messages via Messages.app. │ │ │ ✓ ready │ 📦 mcporter │ Use the …
System: [2026-03-11 04:22:17 UTC] Exec completed (rapid-sh, code 0) :: 21k/200k (11%) · 🗄️ 98% cached │ └───────────────────────────────────────────────┴────────┴──────────┴───────────────┴─────────────────────────────────┘ FAQ: https://docs.opencla…
System: [2026-03-11 04:22:30 UTC] Exec completed (dawn-pra, code 0) :: │ │ │ │ voice │ │ Manage Talk voice selection (list/set). │ │ │ Telegram │ telegram │ loaded │ stock:telegram/index.ts │ 2026.3.8-beta.1 │ │ │ │ │ Telegram channel plugin │ │

Conversation info (untrusted metadata):
```json
{
  "message_id": "2055",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 04:24 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

把它修好
user: System: [2026-03-11 04:25:16 UTC] Exec completed (fast-gul, code 0) :: you need │ │ │ │ │ to fetch new skills on the fly, sync installed skills to │ │ │ │ │ latest or a specific version, or publish new/updated skill │ │ │ │ │ folders with the npm-ins…
System: [2026-03-11 04:25:42 UTC] Exec completed (delta-da, code 0) :: penClaw and inspect update channel status webhooks * Webhook helpers and integrations Examples: openclaw models --help Show detailed help for the models command. openclaw channels…

Conversation info (untrusted metadata):
```json
{
  "message_id": "2057",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 04:28 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

按你说的办
user: System: [2026-03-11 04:29:07 UTC] Exec completed (young-bi, code 0) :: ng nothing (mostly). Usage: openclaw system [options] [command] System tools (events, heartbeat, presence) Options: -h, --help Display help for command Commands: event Enqueue a s…
System: [2026-03-11 04:29:45 UTC] Exec completed (calm-fjo, code 0) :: │ bundled │ │ ✓ ready │ 💾 session-memory │ Save session context to memory when /new or /reset command is │ openclaw- │ │ │ │ issued │ bundled │ └──────────┴──────────────────────…
System: [2026-03-11 04:31:44 UTC] Exec completed (crisp-tr, code 0) :: penClaw and inspect update channel status webhooks * Webhook helpers and integrations Examples: openclaw models --help Show detailed help for the models command. openclaw channels…

Conversation info (untrusted metadata):
```json
{
  "message_id": "2058",
  "reply_to_id": "2038",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 04:29 UTC",
  "has_reply_context": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

Replied message (untrusted, for context):
```json
{
  "sender_label": "赛博虾米🦐",
  "body": "继续完了，已经落成两份文件：\n\n• 证据清单：articles/2026-03-10-ai-众生相-openclaw-国内厂商图谱-证据清单.md\n• 正文第一版：articles/2026-03-10-ai-众生相-openclaw-国内厂商图谱.md\n\n这一版我已经按你刚才定的边界收住了：\n\n• 只写已经有明确动作落地的厂商\n• 目前正文聚焦 阿里云、百度智能云/千帆、腾讯云、火山引擎、中科曙光\n• 没把 华为、浪潮云、地方/园区 那些证据不够硬的内容硬塞进去\n\n这版的核心判断也已经压进去了：同一波 OpenClaw 热度，不同厂商不是在做同一件事，而是在把它往自己最擅长的商业环节里收。\n\n下一步最自然的是二选一：\n\n1. 我直接继续把这篇改成更像公众号成稿的“去 AI 味版”\n2. 我直接继续出你那套固定版式的 refined HTML"
}
```

成文发到这里给我看看
assistant: [[reply_to_current]] 发你看，这版是当前成文稿：

```markdown
# AI 众生相——OpenClaw 热度下的国内厂商图谱

作者：余炜勋

这段时间，OpenClaw 在开发者圈和中文互联网里突然热起来，很多人第一反应是：又一个火了的开源 Agent 项目。

但如果把视角再拉高一点，你会发现，真正值得看的，其实不是 OpenClaw 本身，而是它火起来之后，国内一批厂商接住这波热度的方式。

有意思的地方就在这儿。

同样是看见 OpenClaw 热了，不同厂商并没有做同一种动作。

有人先把它做成“分钟级部署”的上云入口；有人把它纳入自家模型和 Skills 生态；有人围绕企业微信、飞书、钉钉、QQ 这些办公入口做接入；还有人更进一步，直接把它往行业智能体、私有化、安全可信交付上收。

所以，这篇文章真正想回答的问题不是“OpenClaw 为什么火”，而是：

**在 OpenClaw 热度背后，国内厂商分别在抢什么，又各自露出了怎样的商业姿态？**

## 一，不是都在做 OpenClaw，而是在借 OpenClaw 抢入口

如果只看表面，会觉得大家都在围着一个开源项目做文章。

但往下拆就会发现，厂商盯上的，根本不只是 OpenClaw 这个名字。

他们真正盯上的，是 Agent 时代可能出现的几个关键入口：

- 模型入口
- 云资源入口
- 办公消息入口
- Skills / 工具链入口
- 私有化与安全交付入口
- 行业解决方案入口

OpenClaw 之所以敏感，是因为它刚好卡在这些入口的交叉点上。

它不是一个只会聊天的壳子，也不是一个停在演示层的工具。它能接模型、调工具、跑任务、连消息渠道，还能做记忆和自动化。谁把 OpenClaw 接住，谁就有机会顺手把自己的模型、云主机、技能生态、企业办公场景，甚至安全和运维服务一起带进去。

这也是为什么，同样面对一波热度，不同厂商的动作会长得完全不一样。

## 二，阿里云：把 OpenClaw 收进“上云 + 模型 + IM 接入”的一体化产品链

如果说谁把这波热度接得最像“成熟商业化动作”，阿里云算一个比较典型的样本。

一方面，阿里云已经给 OpenClaw 配了比较完整的模型接入文档。官方帮助中心里，已经明确把 OpenClaw 接入百炼模型这件事讲得很细：支持哪些模型、怎么配置 Base URL、怎么填 API Key、怎么安装、怎么完成初始配置，路径已经不是“概念级支持”，而是可以直接上手。

另一方面，阿里云并没有把它停留在“文档支持”这一层，而是继续往“商业页 + 套餐 + 场景接入”去推。它已经上线了“不用写代码，分钟级部署 OpenClaw”的活动页，里面讲得非常直接：本地部署容易休眠、断网、更新麻烦，而轻量应用服务器可以把 OpenClaw 变成一个 7x24 在线的 AI 助手。再往下看，它还进一步把企业微信、QQ、钉钉、飞书这些国内主流 IM 的接入一起打包进去，甚至连 Coding Plan 这样的组合套餐都配上了。

这就说明，阿里云想卖的不是“你也来玩玩 OpenClaw”，而是一个更完整的东西：

**云资源 + 模型 + 可视化配置 + 办公入口接入。**

说白了，阿里云看到的不是一个开源 Agent 项目，而是一条新的开发者上云路径。

## 三，百度智能云：把 OpenClaw 直接吸进 Agent 平台和 Skills 生态里

百度这条路，又是另一种味道。

它不是先强调“把 OpenClaw 托起来”，而是更像在说：你既然要做 OpenClaw，那就顺手把百度这整套 Agent 能力也一起用起来。

现在百度千帆已经推出了“千帆 OpenClaw 一键体验”，强调 3 到 5 分钟完成部署、免费计算资源支持、可选百度官方 Skills，还会给代金券、配合 Coding Plan 降低使用成本。这已经不是单纯在做部署教程，而是在把 OpenClaw 放进百度自己的 Agent 开发和能力分发体系里。

更关键的是，百度智能云的“快速部署 OpenClaw 定制 AI 助手”页面，不只是讲怎么装，而是把轻量服务器、BCC、Tokens 包、百度搜索、百科、学术检索、PPT 生成这些官方 Skills 全都串在一起。你会发现，在这个页面里，OpenClaw 更像一个前台入口，而千帆、轻量云、技能市场和资源包才是背后的真正主角。

所以百度这条线，重点不在“卖一个开源助手”，而在于：

**把 OpenClaw 变成自家 Agent 平台、官方 Skills 和模型调用链的流量入口。**

这其实很聪明。因为一旦开发者和企业从 OpenClaw 这个入口进来了，后面接百度搜索、百科、学术、PPT、深度研究 Agent，整个生态就顺势带进去了。

## 四，腾讯云：把热度先收进“云应用入口 + 企业场景接入”

腾讯云目前的动作，和阿里、百度比起来没有那么重，但方向也很清楚。

一是已经有了 OpenClaw 的云应用页；二是开发者社区已经开始围绕“云上 OpenClaw 接入企业微信”“接入飞书”这类场景做内容铺设。

这说明腾讯云至少已经看见了两件事：

第一，OpenClaw 不是一个只能放在开发者本地玩的东西，它可以变成云上可交付的应用镜像或标准化云应用；

第二，在中国市场里，Agent 如果不往企业微信、飞书这种工作入口去接，热度很难真正变成使用量。

所以腾讯云现在的姿态，虽然还偏“云应用承载 + 开发者教育 + 场景接入”，但它本质上抢的也是入口，而且是很典型的中国式入口：

**不是先抢模型，而是先抢企业工作流里的触达位置。**

## 五，火山引擎：把 OpenClaw 做成“部署模板 + 办公入口 + 安全服务”组合拳

火山引擎的动作也很有代表性。

它在云服务器文档体系里，已经把 OpenClaw（原 Moltbot）单列成一个明确的 AI 应用类别，围绕飞书、企业微信、钉钉、QQ 这些典型办公入口给出快速部署文档。这就已经不是“顺手写了篇教程”，而是产品层面在给 OpenClaw 开路。

更值得注意的是，火山引擎这条线还在继续往安全和运维方向延伸。除了部署文档外，还出现了“创建 OpenClaw（Linux）任务部署 AI 助手安全服务”这类内容。这个动作非常说明问题：在它眼里，OpenClaw 已经不是一个玩具，而是一个要被放进正式云环境里、需要考虑权限边界和安全治理的对象。

所以火山引擎这条路，可以概括为：

**用模板化部署承接开发者热度，用飞书/企微等办公入口承接使用场景，再用安全服务承接企业化需求。**

这和它自身一贯擅长的路径也很一致：不是只做底层资源，而是做“更容易用起来”的平台组合。

## 六，中科曙光：把 OpenClaw 往行业智能体和政企私有化交付上收

如果前面几家更偏“云厂商和平台厂商的自然动作”，那中科曙光这条线就更有“政企交付”的味道了。

曙光官网已经公开写出一篇很直接的文章：《5分钟部署！曙光云 × Moltbot 革新行业智能体》。这篇内容里最重要的地方，不是“5分钟部署”这几个字，而是它后面那套表述：不是简单把 Moltbot 部署到云端，而是和曙光云现有的行业大模型、数据处理能力、行业智能体平台深度联动；不仅讲通用助手能力，还讲煤炭等行业里的垂直场景；不仅讲部署，还讲应用镜像、私有化部署、安全可信底座。

这意味着什么？

意味着在曙光这里，OpenClaw 已经不再只是一个开发者项目，而是被重新解释成：

**行业智能体入口、私有化部署载体，以及安全可信交付的一部分。**

这和阿里、百度、腾讯、火山又不一样。

前几家更多是在接开发者、接生态、接场景；而曙光更像是在说，这波热度最后会落到行业客户、政企项目、私有化交付和安全可信这条线上，而它正好擅长这一段。

这就是典型的“同一波热度，不同商业收口方式”。

## 七，为什么同一波热度，会长出五种不同姿态

把这几家放在一起看，就很清楚了。

它们并不是在围着同一个热点做重复劳动，而是在借同一个热点，把自己最核心的能力重新包装、重新前置。

阿里云卖的是“上云 + 模型 + IM 接入 + 套餐化配置”；
百度卖的是“Agent 平台 + 官方 Skills + 搜索与知识能力”；
腾讯云偏向“云应用入口 + 企业工作流接入”；
火山引擎卖的是“模板化部署 + 办公入口 + 安全运维增强”；
中科曙光则把它往“行业智能体 + 私有化 + 安全可信 + 行业方案交付”上收。

所以，所谓“AI 众生相”，说到底不是在看谁最懂 OpenClaw，而是在看：

**同一个开源 Agent 热点，分别照出了不同厂商最想抓住的那一段价值链。**

有人想先抓开发者，有人想先抓模型调用，有人想先抓企业办公入口，有人想先抓行业落地，有人想先抓安全可信和私有化交付。

这就是真正有意思的地方。

## 八，这波动作后面，真正变化的不是工具，而是市场认知

如果再往前看一步，这些动作背后其实还有一个更深的变化。

过去很多厂商谈 AI，还是在讲“大模型能力有多强”“推理速度有多快”“上下文有多长”。但 OpenClaw 这类项目火起来之后，市场开始越来越清楚地意识到：

真正能形成新入口的，不是单个模型参数，而是“模型 + 工具 + 渠道 + 任务执行 + 记忆 + 自动化”组成的完整工作流。

这会带来一个很现实的结果：

今后谁能接住 Agent 热度，拼的就不只是模型，而是能不能把模型、云、消息入口、工具链、安全和行业场景一起拧成一个交付闭环。

从这个角度看，OpenClaw 火不火只是表象。真正值得重视的是，它已经开始逼着国内厂商用更完整的方式去回答一个问题：

**在 Agent 时代，你到底准备卖什么？**

有人卖部署，有人卖模型，有人卖生态，有人卖安全，有人卖行业方案。

这，才是这波热度真正照出来的厂商图谱。

## 九，最后说一句

如果把这波现象只理解成“一个开源项目火了”，那就看浅了。

更准确的理解应该是：

**OpenClaw 只是一个触发点，它把国内厂商在 Agent 时代各自的站位、焦虑和抢位动作，提前暴露出来了。**

而且这件事还没结束。

今天先落地的是阿里云、百度、腾讯云、火山引擎、中科曙光这几类动作；接下来，围绕算力、一体机、私有化交付、安全、园区和地方产业配套，后面大概率还会有更多动作继续冒出来。

但至少到现在，第一批“已经把动作做出来”的厂商，轮廓已经很清楚了。

OpenClaw 这只虾，已经不只是开发者在养了。

厂商们，也已经下场了。

---

## 来源说明

- 知识库：暂无直接命中本题的现成笔记，本文以外部公开信息为主
- 延伸：基于当前工作区中 OpenClaw 部署、生产化、消息渠道、模型接入和政企落地相关积累，对各厂商动作进行了归类分析
- 外部：阿里云 OpenClaw 页面与百炼接入文档、百度智能云/千帆 OpenClaw 页面、腾讯云 OpenClaw 云应用与开发者社区文章、火山引擎 OpenClaw 部署文档、中科曙光 Moltbot/行业智能体相关文章
```

我直说，这版已经能看，但还不算“狠”。  
最大的问题有两个：

- 结构是清楚的，但篇幅有点平均，几家厂商像并排铺开，冲击力还不够
- 语言已经比前一版顺了，但还偏“分析型成文”，离真正适合公众号传播的“劲儿”还差一口

如果你要，我下一步会直接这么改：
1. 开头更锋利，先把“这不是一篇写 OpenClaw 的文章，而是一篇借 OpenClaw 看厂商抢位的文章”打出去
2. 中段不再平均铺陈，而是拉出“谁在卖云、谁在卖模型、谁在卖入口、谁在卖行业交付”的对照感
3. 结尾再收得更像观点稿，而不是研究总结

你回我一句 `继续压`，我就直接把这一版再提一档。
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "2064",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 04:52 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

继续 OK
assistant: [[reply_to_current]] 我已经继续压了一版，正文还是这个文件：

`articles/2026-03-10-ai-众生相-openclaw-国内厂商图谱.md`

这次我做的不是小修，是直接换成了更像观点稿的打法：
- 开头先把“这不是写 OpenClaw 本身，而是借它看厂商抢位”打明
- 中段不再平均铺陈，而是把每家厂商的“收口方式”拉得更清楚
- 结尾也收成了“OpenClaw 只是引子，抢位才是正文”

我现在的判断是：**这一版已经比上一版更适合公众号了。**
下一步如果你点头，就该直接进：
1. refined HTML
2. 标题再压一轮，冲打开率
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "2066",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 04:56 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

改完发到这边给我审审
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "2069",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 06:55 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

新增一个模型：provider：astron，模型：astron-code-latest， "baseUrl": "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2",
 "apiKey": "442ab53a1862cd9c0ccdbbe27f0f1097:ZjVjNDNiN2JjZjMzNzk1ZGIyZWNjMmNm",
 "api": "openai-completions",
 "models": [
 {
 "id": "astron-code-latest",
 "name": "astron-code-latest",
 "reasoning": false,
 "input": ["text"],
 "contextWindow": 98304,
 "maxTokens": 65536
assistant: [[reply_to_current]] 已加好。

- 新 provider：`astron`
- 新模型：`astron/astron-code-latest`
- 别名我顺手配成了：`astroncode`
- 网关已经自动重启生效

你现在可以直接用：
- `astron/astron-code-latest`
- 或简写 `astroncode`

顺手提醒一句：你刚才把 `apiKey` 明文发出来了，这个最好后面换一把，别在聊天里长期裸奔。
user: Pre-compaction memory flush. Store durable memories now (use memory/2026-03-11.md; create memory/ if needed). IMPORTANT: If the file already exists, APPEND new content only — do not overwrite existing entries. Do NOT create timestamped variant files (e.g., 2026-03-11-HHMM.md); always use the canonical 2026-03-11.md filename. If nothing to store, reply with NO_REPLY.
Current time: Wednesday, March 11th, 2026 — 6:58 AM (UTC) / 2026-03-11 06:58 UTC
user: System: [2026-03-11 07:02:42 UTC] Model switched to aicat/gpt-5.4.

Conversation info (untrusted metadata):
```json
{
  "message_id": "2081",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 07:03 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

检查 astron/astron-code-latest 可用性
assistant: [[reply_to_current]] 查了，结论先说：

- `astron/astron-code-latest` 已经**成功注册进模型列表**
- 但我刚做的实际调用里，**并没有真正切到 astron**
- 这次本地 smoke test 最后实际跑起来的还是：`cpa/gpt-5.3-codex`

关键证据：
- `openclaw models list` 里已经能看到 `astron/astron-code-latest`，别名 `astroncode` 也在
- 但测试返回的 `meta.agentMeta.model` 显示实际使用的是 `gpt-5.3-codex`
- 也就是说，**配置写进去了，但 `OPENCLAW_MODEL=astroncode` 这条本地调用链没有把模型切过去**

所以现在的真实状态不是“astron 不可用”，而是：

- **配置层：OK**
- **显式调用切模：还没验证通**
- **可用性：目前不能算已验证**

下一步我建议直接做两件事：
1. 查清 OpenClaw 本地/网关调用到底该用什么方式强制指定模型
2. 用正确方式再打一遍真正的 astron 实际请求，确认它是“能返回”还是“鉴权/接口协议有问题”

你这次要的是“检查可用性”，那我现在不给你装验证过了。  
目前只能算：**加进去了，但还没打通到真正出结果这一步。**
user: System: [2026-03-11 07:03:58 UTC] Exec completed (nimble-c, code 0) :: o the default gateway port, then start it. openclaw gateway ... Gateway control via WebSocket. openclaw agent --to +15555550123 --message "Run summary" --deliver Talk directly to …
System: [2026-03-11 07:05:10 UTC] Exec completed (good-lag, code 0) :: rtiesCount": 3 }, { "name": "memory_search", "summaryChars": 334, "schemaChars": 139, "propertiesCount": 3 }, { "name": "memory_get", "summaryChars": 151, "schemaChars": 128, "pro…

Conversation info (untrusted metadata):
```json
{
  "message_id": "2083",
  "sender_id": "1511915498",
  "sender": "Ethan YU",
  "timestamp": "Wed 2026-03-11 07:05 UTC"
}
```

Sender (untrusted metadata):
```json
{
  "label": "Ethan YU (1511915498)",
  "id": "1511915498",
  "name": "Ethan YU",
  "username": "happynailzz1983"
}
```

验证这个模型的可用
assistant: [[reply_to_current]] 验证完了，这个模型是可用的。

结果：
- 接口直连返回 `200`
- 实际模型：`astron-code-latest`
- 返回内容：`ASTRON_OK`

我刚才是直接按 OpenAI 兼容接口打的：
- Base URL：`https://maas-coding-api.cn-huabei-1.xf-yun.com/v2`
- Endpoint：`/chat/completions`
- 鉴权：`Authorization: Bearer ...`

所以现在可以下结论：

- **模型本身可用**
- **API key 可用**
- **baseUrl 没填错**
- **OpenAI 兼容协议是通的**

补一句，前面没在 OpenClaw 本地调用里切过去，不代表模型坏了，说明更像是：
- OpenClaw CLI 那条 `--local` 调用链没有按我那种方式显式切到 `astroncode`
- 但 provider 本身是通的，模型可正常出结果

如果你要，我下一步就继续把 **OpenClaw 内部显式切到 `astroncode` 的调用方式也给你打通**。
