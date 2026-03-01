# Browser Takeover SOP

这套 SOP 规范了如何在后台无头模式下执行浏览器自动化任务，并在遇到反爬/验证码时，平滑地切换到 VNC 有头模式由人类接管，最后交还控制权继续自动执行。

## 适用场景
- 登录需进行滑块、图片点选等复杂验证的站点。
- 爬取过程中触发高频防刷机制（如 Cloudflare Turnstile）。
- 需要临时人机交互（如扫码登录）的自动化流程。

## 核心机制与流程

### 1. 无头自动化运行 (Autonomous Mode)
- **工具链**：优先使用 `browser` (OpenClaw 原生) 或 Puppeteer/Playwright 脚本，挂载 `--no-sandbox` 标志。
- **异常捕获**：在执行 DOM 提取或表单提交前，注入特征检测。如果页面包含 `captcha`、iframe 拦截特征或特定反爬提示，触发异常并挂起执行。

### 2. 人类接管阶段 (Takeover Mode)
- **环境切换**：捕获到验证码后，自动化脚本暂停当前 `page`，将其挂起（或重启带有 `--remote-debugging-port=9222` 的有头浏览器进程至虚拟桌面 `:1`）。
- **通知**：我通过当前对话通道向你发送“触发验证码，请接管”的警报。
- **操作步骤**：
  1. 打开 KasmVNC 访问地址：`https://<IP>:8444`。
  2. 登录账号：`nailwilson`，密码：`yyzz13116822`。
  3. 在桌面环境 (XFCE4) 的 Chrome 浏览器中，手动完成验证码/扫码。
  4. 验证通过后，在聊天窗口向我发送接管完成口令（默认：“已过” 或 “继续”）。

### 3. 控制权交还 (Resumption)
- **恢复**：我收到口令后，脚本解除挂起状态。
- **执行**：继续从断点处向下执行数据抓取或发文操作。

---

## 开发与调用规范（供 AI 内部使用）

在编写 Puppeteer 等 Node.js 爬虫脚本时，必须包含以下接管逻辑桩：

```javascript
// 示例：特征检测与挂起等待外部指令
const checkCaptcha = async (page) => {
    const hasCaptcha = await page.$('iframe[src*="captcha"]'); // 根据目标站调整特征
    if (hasCaptcha) {
        console.log("WAIT_FOR_TAKEOVER: 检测到验证码，已将界面留置在 VNC 桌面上。");
        // 进入死循环或阻塞等待特定文件/信号的写入，由外部对话传入恢复指令
        while (!require('fs').existsSync('/tmp/resume_signal')) {
            await new Promise(r => setTimeout(r, 2000));
        }
        require('fs').unlinkSync('/tmp/resume_signal');
        console.log("RESUME: 收到恢复指令，继续执行。");
    }
};
```

执行此类脚本时，使用 `process` 工具挂起轮询，并将桌面环境 (DISPLAY=:1) 绑定到 Chrome 启动参数中，确保 VNC 中可见。
