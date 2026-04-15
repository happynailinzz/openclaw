import requests,re,urllib.parse
url='https://henb.nea.gov.cn/'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=20)
print('status',r.status_code,'len',len(r.text))
for pat in ['href="([^"]+)"','href=\'([^\']+)\'']:
    pass
# print likely article urls with text around them
for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',r.text,re.S|re.I):
    href,text=m.groups()
    txt=re.sub(r'<.*?>','',text)
    txt=re.sub(r'\s+',' ',txt).strip()
    if len(txt)>=2:
        if any(k in href for k in ['/article/','/xwfb/','/tzgg/','/yw/']) or any(k in txt for k in ['监管','电力','能源','市场','系统','数智','数字']):
            if href.startswith('./'): href='https://henb.nea.gov.cn/'+href[2:]
            elif href.startswith('/'): href='https://henb.nea.gov.cn'+href
            print('-',txt[:100],'|',href)
