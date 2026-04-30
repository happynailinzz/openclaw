# task_plan.md

## Goal
执行一次《社交平台情报抓取 SOP（OpenClaw版）》完整流程，围绕用户业务相关方向抓取 X / 小红书 / YouTube / Reddit / 新闻网站 / RSS 情报，完成评分、去重、简报、分发、留痕与可检索归档。

## Phases
- [complete] Phase 1: 读取上下文并建立工作文件
- [complete] Phase 2: 多源抓取与失败回退
- [complete] Phase 3: 结构化整理、评分、筛噪
- [complete] Phase 4: 输出简报、归档、记忆留痕

## Constraints
- 非周一，跳过 Step A skills 周检
- 单源失败不阻塞全流程
- 输出字段固定：platform/title/published_at/url/summary/signals/confidence
- 价值评分规则：关键词+2，高可信源+2，业务直接相关+3，营销噪音-2，重复-3

## Notes
- 当前为 cron 场景，最终 plain-text reply 会自动投递到当前聊天。
- 优先官方/高可信源；社交平台若直接抓取受阻，采用 RSS / 镜像 / 新闻转述回退。
