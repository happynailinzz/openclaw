import requests,re
html=requests.get('https://sports.sina.com.cn/nba/').content.decode('utf-8','ignore')
pat=re.compile(r'<div class="match-card".*?<span class="match-league">(.*?)</span>\s*<span class="match-date">(.*?)</span>\s*<span class="match-status[^"]*">(.*?)</span>.*?<span class="match-team-name">(.*?)</span>\s*<div class="match-team-score">(.*?)</div>.*?<span class="match-team-name">(.*?)</span>\s*<div class="match-team-score">(.*?)</div>',re.S)
rows=[]
for m in pat.finditer(html):
    league,date,status,t1,s1,t2,s2=[x.strip() for x in m.groups()]
    rows.append((date,status,t1,s1,t2,s2))
print('rows',len(rows))
for r in rows:
    if r[0].startswith('04/21') or r[0].startswith('04/22') or r[0].startswith('04/20'):
        print('|'.join(r))
