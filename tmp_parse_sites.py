import requests,re,urllib.parse
sites=[('zhengzhou','https://www.zhengzhou.gov.cn/'),('henb','https://henb.nea.gov.cn/')]
keywords=['人工智能','数据','数字','算力','能源','电力','平台','项目','签约','合作','示范','试点','源网荷储']
for name,url in sites:
    print(f'## {name} {url}')
    try:
        r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=20)
        html=r.text
        seen=0
        for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',html,re.S|re.I):
            href,text=m.groups()
            txt=re.sub(r'<.*?>','',text)
            txt=re.sub(r'\s+',' ',txt).strip()
            if not txt: continue
            if any(k in txt for k in keywords):
                if href.startswith('//'): href='https:'+href
                elif href.startswith('/'):
                    from urllib.parse import urljoin
                    href=urljoin(url,href)
                print('-',txt[:80],'|',href)
                seen+=1
                if seen>=25: break
        if seen==0: print('(no keyword anchors)')
    except Exception as e:
        print('ERR',e)
    print()