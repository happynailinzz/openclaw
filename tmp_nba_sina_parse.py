import requests,re
from bs4 import BeautifulSoup

url='https://sports.sina.com.cn/nba/'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=20)
r.encoding='utf-8'
html=r.text
print('HTML_LEN', len(html))

links=sorted(set(re.findall(r'https://sports\.sina\.com\.cn/basketball/nba/2026-04-18/doc-[^"\']+\.shtml', html)))
print('NBA_2026_04_18_LINKS', len(links))
for u in links[:50]:
    print('LINK', u)

pat=re.compile(r'<a[^>]+href="(https://sports\.sina\.com\.cn/[^\"]+2026-04-18[^\"]+\.shtml)"[^>]*>(.*?)</a>', re.S)
items=[]
for href,title in pat.findall(html):
    t=re.sub(r'<.*?>','',title).strip()
    t=re.sub(r'\s+',' ',t)
    if t:
        items.append((href,t))
print('ANCHOR_2026_04_18', len(items))
for href,t in items[:100]:
    print('ITEM', t, '|', href)

# match cards near today / tomorrow region
card_pat=re.compile(r'<div class="match-card".*?<span class="match-date">(.*?)</span>.*?<span class="match-status[^"]*">(.*?)</span>.*?<span class="match-team-name">(.*?)</span>.*?<div class="match-team-score">(.*?)</div>.*?<span class="match-team-name">(.*?)</span>.*?<div class="match-team-score">(.*?)</div>', re.S)
cards=[]
for date,status,t1,s1,t2,s2 in card_pat.findall(html):
    clean=lambda x: re.sub(r'\s+',' ',x).strip()
    cards.append((clean(date),clean(status),clean(t1),clean(s1),clean(t2),clean(s2)))
print('MATCH_CARDS', len(cards))
for row in cards[:25]:
    print('CARD', ' | '.join(row))
