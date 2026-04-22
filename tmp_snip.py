import requests,re
html=requests.get('https://sports.sina.com.cn/nba/').content.decode('utf-8','ignore')
for key in ['詹姆斯','库里','东契奇','约基奇','杜兰特','塔图姆','恩比德','交易','伤病','教练','复出','缺阵']:
    idx=html.find(key)
    print('\nKEY',key,'IDX',idx)
    if idx!=-1:
        print(html[idx-600:idx+1200])
