#!/usr/bin/env sh
set -eu

python3 - <<'PY'
import urllib.request, urllib.error, ssl, json

urls = [
    ('henan_gov', 'https://www.henan.gov.cn/2026/03-06/3331975.html'),
    ('henan_fgw', 'https://fgw.henan.gov.cn/2026/03-05/3330866.html'),
    ('henan_jyt_mobile', 'http://m.jyt.henan.gov.cn/2026-03/05/3331209.html'),
    ('henan_hca_miit', 'https://hca.miit.gov.cn/wzpz/tpxw/art/2026/art_29d6f4158d5c4b5894f1b27b331c2d57.html'),
    ('zz_gov', 'https://www.zhengzhou.gov.cn/'),
    ('zz_zzu', 'https://www.zzu.edu.cn/info/1217/87720.htm'),
    ('henan_nea', 'https://henb.nea.gov.cn/dtyw/jgdt/202603/t20260306_297496.html'),
    ('gov_cn', 'https://www.gov.cn/zhengce/202603/content_7060867.htm'),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for name, url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            print(json.dumps({
                'name': name,
                'status': r.status,
                'final_url': r.geturl(),
                'content_type': r.headers.get('Content-Type', ''),
            }, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(json.dumps({
            'name': name,
            'status': e.code,
            'error': 'HTTPError',
            'reason': str(e.reason),
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            'name': name,
            'status': 'ERR',
            'error': type(e).__name__,
            'reason': str(e),
        }, ensure_ascii=False))
PY
