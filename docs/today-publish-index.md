# Today Publish Index

日期：2026-03-09

## 一、文章主文件

- Markdown：`articles/2026-03-09-河南电力数字化项目窗口已经打开.md`
- HTML：`articles/2026-03-09-河南电力数字化项目窗口已经打开.html`
- 公众号排版版：`articles/2026-03-09-河南电力数字化项目窗口已经打开-wechat.html`
- 咨询报告风：`articles/2026-03-09-河南电力数字化项目窗口已经打开-consulting.html`
- 参考样式重排版：`articles/2026-03-09-河南电力数字化项目窗口已经打开-wechat-refined.html`

## 二、公众号草稿箱

- 第一版：`8gRyeWzNxD0B0xYzMKllW9YHn78WtKNuPk3RGGqR8ubEyc3Chw0pu9WLEbiD6EsR`
- 咨询报告风版：`8gRyeWzNxD0B0xYzMKllW_KqE1DJW38tU8bJ2JdlOLBXWX8CsJWBXkB-J8ozMQbL`
- `publish.sh --fast` 跑通版：`8gRyeWzNxD0B0xYzMKllW1jT0FAq9cck6SHHBZ5tYjhutCByH3LpmyiHw7cr4r6s`
- 参考样式 refined 版：`8gRyeWzNxD0B0xYzMKllW5IsydtnvYFpDgs4HzJ5LqssVSSDDM6IKMGRMsicj2ej`

## 三、Notion

- 页面 ID：`31e70dc2-6079-811c-951c-e6bc4db4f729`

## 四、发布链相关

- 主发布脚本：`scripts/publish.sh`
- 快发 SOP：`docs/publish-fast-sop.md`
- 相关 commit：`fa6bf52` (`improve fast publish flow`)

## 五、Cron 第一轮整改

- 删除：`test:lianghui-henan-industries:now`
- 停用：`test:lianghui-henan-industries:next-minute`
- 改为明确 Telegram 投递：
  - `digest:overseas-cn-news:0800`
  - `digest:overseas-cn-news:1400`
  - `monitor:github-updates:0900`

## 六、Cron 第二轮整改

- 改为明确 Telegram 投递：
  - `digest:equity-tracks:1600`
  - `report:ai-infra-capital-weekly:mon1005`

## 七、封面与配图

- 当前占位封面：`articles/imgs/cover-2026-03-02-河南源网荷储数字化.png`
- 已补一套新风格提示词：电力系统信息图 / 产业决策可视化 / 监管科技感
