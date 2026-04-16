import requests
from bs4 import BeautifulSoup
r=requests.get('https://sports.sina.com.cn/nba/',timeout=20,headers={'User-Agent':'Mozilla/5.0'})
r.encoding='utf-8'
soup=BeautifulSoup(r.text,'html.parser')
seen=set(); n=0
for a in soup.find_all('a',href=True):
    txt=' '.join(a.get_text(' ',strip=True).split())
    href=a['href']
    if not txt or not any('\u4e00'<=c<='\u9fff' for c in txt):
        continue
    key=(txt,href)
    if key in seen: 
        continue
    seen.add(key)
    print(txt,'|||',href)
    n+=1
    if n>=180:
        break
