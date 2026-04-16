import requests,re
from bs4 import BeautifulSoup
r=requests.get('https://sports.sina.com.cn/nba/',timeout=20,headers={'User-Agent':'Mozilla/5.0'})
r.encoding='utf-8'
html=r.text
print('published marker count', html.count('2026-04-15'))
print('=== 2026 dated urls ===')
urls=[]
for u in re.findall(r'https://sports\.sina\.com\.cn/[^"\']+', html):
    if '2026-04-' in u:
        urls.append(u)
for u in dict.fromkeys(urls):
    print(u)
print('=== likely nba headlines ===')
soup=BeautifulSoup(html,'html.parser')
seen=set()
for a in soup.find_all('a',href=True):
    txt=' '.join(a.get_text(' ',strip=True).split())
    href=a['href']
    if len(txt)>=8 and any('\u4e00'<=c<='\u9fff' for c in txt):
        if any(k in txt for k in ['詹姆斯','库里','东契奇','约基奇','杜兰特','塔图姆','恩比德','湖人','勇士','凯尔特人','掘金','雷霆','附加赛','季后赛','火箭','快船','雄鹿','尼克斯','森林狼','太阳','独行侠']):
            key=(txt,href)
            if key not in seen:
                seen.add(key)
                print(txt,'|||',href)
