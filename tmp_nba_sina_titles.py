import requests,re
from html import unescape

r=requests.get('https://sports.sina.com.cn/nba/',headers={'User-Agent':'Mozilla/5.0'},timeout=20)
r.encoding='utf-8'
html=r.text
pat=re.compile(r'<a[^>]+href="(https://sports\.sina\.com\.cn/(?:basketball/nba|zt_d/nba|[^\"]*nba[^\"]*)[^\"]*)"[^>]*>(.*?)</a>', re.S)
seen=set()
count=0
for href,title in pat.findall(html):
    t=re.sub(r'<.*?>','',title)
    t=unescape(re.sub(r'\s+',' ',t)).strip()
    if not t or (href,t) in seen:
        continue
    seen.add((href,t))
    print(t,'|',href)
    count+=1
    if count>=120:
        break
print('COUNT',count)
