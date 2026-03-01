# OpenClaw 记忆整合部署计划（v1）

## 目标
将「分层架构 + 混合检索 + Memos + 本地记忆 + Token预算」完整落地为可执行配置与脚本。

## Phase 1（P0）配置与安全
- [x] 配置 `config/memos.env`（base_url + api_key）
- [x] 保护密钥不入库（`.gitignore`）
- [x] 增加 `base_id` 与统一配置文件

## Phase 2（P0）能力落地
- [x] 提供 memos 客户端脚本（add/search）
- [x] 提供检索路由脚本（热→温→冷 + 混合评分）
- [x] 提供 token 预算策略文件

## Phase 3（P1）运行规范
- [x] 提供记忆维护 SOP（日更/周更）
- [x] 提供部署说明（接入点、调用方式、回滚）
- [x] 执行一次联调测试（add + search + route）

## 阻塞条件
- 若 Memos 服务端接口策略变更（header/path），需更新客户端脚本。

## 输出
- 可运行脚本 + 配置文件 + 策略文档
- 验证结果与下一步优化点
- Git 提交记录
