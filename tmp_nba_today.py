import requests,re
html=requests.get('https://sports.sina.com.cn/nba/').content.decode('utf-8','ignore')
items=[]
for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
    href=m.group(1)
    text=re.sub(r'<.*?>','',m.group(2)).strip()
    if not text:
        continue
    if '/basketball/nba/' in href or href.startswith('//sports.sina.com.cn/basketball/nba/') or '/nba/' in href:
        items.append((href,text))
print('total',len(items))
seen=set(); count=0
for href,text in items:
    key=(href,text)
    if key in seen: continue
    seen.add(key)
    if len(text) < 6 or len(text) > 60: continue
    print(text,'|||',href)
    count += 1
    if count >= 260: break
