#!/usr/bin/env python3
"""
SmartAPI 图片生成脚本（chat completions 接口）
用法：python3 scripts/smartapi-image-gen.py "<prompt>" <output.png>
"""
import sys, os, re, base64, json
from urllib import request, error

def main():
    if len(sys.argv) < 3:
        print("用法：python3 scripts/smartapi-image-gen.py '<prompt>' <output.png>")
        sys.exit(1)

    prompt = sys.argv[1]
    output = sys.argv[2]

    base_url = os.environ.get("IMAGE_GEN_BACKUP_BASE_URL") or os.environ.get("IMAGE_GEN_BASE_URL", "https://api.smartapi.me/v1")
    api_key  = os.environ.get("IMAGE_GEN_BACKUP_API_KEY") or os.environ.get("IMAGE_GEN_API_KEY", "")
    model    = os.environ.get("IMAGE_GEN_BACKUP_MODEL") or os.environ.get("IMAGE_GEN_MODEL") or "gemini-3.1-flash-image-preview"

    # 失败重试：SmartAPI 有时返回纯文字/502；这里做指数退避 + 抖动
    max_tries = int(os.environ.get("SMARTAPI_IMAGE_MAX_TRIES", "8"))
    base_sleep = float(os.environ.get("SMARTAPI_IMAGE_BASE_SLEEP", "1.5"))

    last_err = None
    for i in range(1, max_tries + 1):
        # SmartAPI 的同一模型有时会返回“文字描述”而不是图片，尽量提示要图片
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt + "\n\n(Please return an image as base64 data URL.)"}],
            "stream": False
        }).encode()

        req = request.Request(
            f"{base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0)"
            }
        )

        try:
            with request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            m = re.search(r'data:image/\w+;base64,([A-Za-z0-9+/=\s]+)', content)
            if not m:
                last_err = f"no_image_in_response (try={i}) content_head={content[:120]!r}"
            else:
                b64_data = re.sub(r'\s', '', m.group(1))
                img_bytes = base64.b64decode(b64_data)
                # 简单 sanity check：太小大概率是错误/占位图
                if len(img_bytes) < 50_000:
                    last_err = f"image_too_small (try={i}) bytes={len(img_bytes)}"
                else:
                    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
                    with open(output, 'wb') as f:
                        f.write(img_bytes)
                    print(output)
                    return

        except error.HTTPError as e:
            last_err = f"http_error {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            last_err = f"exception: {e}"

        # 退避等待（1.5s, 3s, 6s ...）+ 抖动
        import random, time
        sleep_s = base_sleep * (2 ** (i - 1))
        sleep_s = min(sleep_s, 30.0) + random.uniform(0.05, 0.3)
        time.sleep(sleep_s)

    print("图片生成失败：重试已用尽")
    print("DEBUG base_url:", base_url)
    print("DEBUG model:", model)
    print("DEBUG last_err:", last_err)
    sys.exit(1)

if __name__ == "__main__":
    main()
