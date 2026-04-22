import requests,re
html=requests.get('https://sports.sina.com.cn/nba/').content.decode('utf-8','ignore')
anchors=[]
for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
    href=m.group(1)
    text=re.sub(r'<.*?>','',m.group(2)).strip()
    if text and any(k in text for k in ['詹姆斯','库里','东契奇','约基奇','杜兰特','塔图姆','恩比德','湖人','勇士','火箭','马刺','开拓者','猛龙','骑士','尼克斯','雄鹿','掘金','凯尔特人']):
        anchors.append((href,text))
print('anchors',len(anchors))
seen=set()
count=0
for href,text in anchors:
    if (href,text) in seen:
        continue
    seen.add((href,text))
    print(text,'|||',href)
    count += 1
    if count >= 180:
        break
