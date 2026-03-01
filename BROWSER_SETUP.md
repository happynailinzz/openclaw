# Browser Setup

A headless and headed Chrome browser is now installed for OpenClaw using Puppeteer.

## Paths
- Chrome executable: `/root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome`

## Environment Setup
Required dependencies installed via apt:
- libnss3, libatk1.0-0, libatk-bridge2.0-0, libcups2, libgbm1, libasound2, libpangocairo-1.0-0, libxss1, libgtk-3-0
- xvfb, x11-xserver-utils, xfonts-100dpi, xfonts-75dpi, xfonts-scalable, xfonts-cyrillic

## Usage (CLI)

**Headless Mode**
```bash
/root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome --headless --no-sandbox --disable-gpu --dump-dom https://example.com
```

**Headed Mode (via Xvfb virtual frame buffer)**
```bash
xvfb-run -a /root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome --no-sandbox https://example.com
```

> **Note:** Since OpenClaw runs as `root`, Chrome requires the `--no-sandbox` flag to execute properly.
