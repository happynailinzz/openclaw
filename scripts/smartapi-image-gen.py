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
    model    = os.environ.get("IMAGE_GEN_BACKUP_MODEL") or os.environ.get("IMAGE_GEN_MODEL", "gemini-3.1-flash-image-preview")

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
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
    except error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        sys.exit(1)

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    # 提取 base64 图片
    m = re.search(r'data:image/\w+;base64,([A-Za-z0-9+/=\s]+)', content)
    if not m:
        print("未找到图片数据，响应内容前500字符：", content[:500])
        sys.exit(1)

    b64_data = re.sub(r'\s', '', m.group(1))
    img_bytes = base64.b64decode(b64_data)

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'wb') as f:
        f.write(img_bytes)

    print(output)

if __name__ == "__main__":
    main()
