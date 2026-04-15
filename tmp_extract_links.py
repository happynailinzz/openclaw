import requests,re
sites=[('henb','https://henb.nea.gov.cn/'),('gov','https://www.gov.cn/')]
for name,url in sites:
    try:
        r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=20)
        print(f'### {name} {url} status {r.status_code} len {len(r.text)}')
        matches=[]
        for m in re.finditer(r'href=["\']([^"\']+)["\'][^>]*>(.*?)<',r.text,re.S):
            href,text=m.groups()
            txt=re.sub(r'<.*?>','',text).strip()
            if any(k in txt for k in ['电力','监管','数据','数字','信息','人工智能','算力','能源','平台','新型电力系统']):
                matches.append((txt,href))
        for txt,href in matches[:30]:
            print('-',txt[:60],'|',href)
    except Exception as e:
        print('ERR',name,e)
    print()