# Publish Fast SOP

适用场景：两会快反、河南本地热点、先发草稿箱占位、封面后补。

## 标准命令

最常用：

```bash
bash scripts/publish.sh articles/你的文章.md --fast
```

如果已有封面：

```bash
bash scripts/publish.sh articles/你的文章.md --fast --cover /绝对路径/封面.png
```

## `--fast` 的行为

- 直接跳过自动生图
- 封面优先顺序：
  1. `--cover` 手动指定封面
  2. 文章已有封面 `articles/imgs/cover-<slug>.png`
  3. 默认占位图 `articles/imgs/cover-2026-03-02-河南源网荷储数字化.png`
- 然后继续自动完成：
  - Markdown 转 HTML
  - 推送公众号草稿箱
  - 入库 Notion

## 发稿前最少检查

文章 frontmatter 至少包含：

```md
---
title: 文章标题
author: 余炜勋
description: 文章摘要
---
```

## 适用与不适用

适用：
- 热点快发
- 先占位进草稿箱
- 封面可以后补

不适用：
- 必须自动生成新封面
- 正式重稿、愿意等完整配图
- 需要一次成型的精排版本

## 备注

- 当前主发布链：`scripts/publish.sh`
- 资料采集链路：`scripts/wechat-capture.sh`、`scripts/wechat_to_notion.sh`
- 原问题复盘：之前的卡点在 Step 1 自动生封面，`--fast` 已绕开该阻塞点。
