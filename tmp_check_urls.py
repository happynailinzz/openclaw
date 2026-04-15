import requests,re
urls=[
('fgw_platform','http://fgw.henan.gov.cn/2024/12-02/3093787.html'),
('fgw_ai','http://fgw.henan.gov.cn/2025/04-24/3151541.html'),
('henan_compute','https://www.henan.gov.cn/2024/09-29/3068786.html'),
('henan_dispatch','https://www.henan.gov.cn/2024/12-01/3093282.html'),
('luohe_ai','https://www.luohe.gov.cn/zdlyxxgkzl/qtly/zqsk/content_1046324'),
('zhengzhou_home','https://www.zhengzhou.gov.cn/'),
('henb_home','https://henb.nea.gov.cn/')
]
for name,url in urls:
    try:
        r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=20,allow_redirects=True)
        print(f'### {name} status={r.status_code} final={r.url} len={len(r.text)}')
        t=''
        m=re.search(r'<title[^>]*>(.*?)</title>',r.text,re.S|re.I)
        if m:t=re.sub(r'\s+',' ',m.group(1)).strip()
        print('TITLE:',t[:200])
        print('HEAD:',re.sub(r'\s+',' ',r.text[:500])[:500])
    except Exception as e:
        print(f'### {name} ERROR {e}')
    print('---')