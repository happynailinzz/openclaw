#!/usr/bin/env bash
set -e
exec xvfb-run -a /root/.cache/puppeteer/chrome/linux-145.0.7632.77/chrome-linux64/chrome --no-sandbox --disable-gpu "$@"
