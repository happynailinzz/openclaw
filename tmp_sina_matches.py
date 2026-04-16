import requests,re
from bs4 import BeautifulSoup
r=requests.get('https://sports.sina.com.cn/nba/',timeout=20,headers={'User-Agent':'Mozilla/5.0'})
r.encoding='utf-8'
html=r.text
# crude regex around match cards
for m in re.finditer(r'<div class="match-card".*?</div>\s*</div>\s*</div>', html, re.S):
    block=m.group(0)
    date=re.search(r'match-date">([^<]+)<', block)
    status=re.search(r'match-status[^>]*>([^<]+)<', block)
    teams=re.findall(r'match-team-name">([^<]+)<', block)
    scores=re.findall(r'match-team-score">([^<]+)<', block)
    if date and len(teams)==2 and len(scores)==2:
        print(date.group(1).strip(), '|', status.group(1).strip() if status else '', '|', teams[0], scores[0], 'vs', teams[1], scores[1])
