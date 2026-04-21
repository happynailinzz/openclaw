import json, subprocess, sys
queries = [
  '河南省工业和信息化厅 人工智能 项目 2026 site:hnit.gov.cn',
  '河南省发展和改革委员会 算力 数据中心 2026 site:fgw.henan.gov.cn',
  '河南省数据局 数据产业园 数据治理 2026 site:henan.gov.cn',
  '郑州 数据局 算力 人工智能 项目 2026 site:zhengzhou.gov.cn',
  '洛阳 工信局 数字化转型 项目 2026 site:ly.gov.cn',
  '许昌 数字化转型 试点 项目 2026 site:xuchang.gov.cn',
  '新乡 数字化转型 链主 项目 2026 site:xx.gov.cn',
  '鹤壁 数据 标注 人工智能 项目 2026 site:hebi.gov.cn',
  '中国移动河南 算力 数据中心 2026 site:ha.chinamobile.com',
  '国网河南 电力 数字化 示范 项目 2026 site:hn.sgcc.com.cn',
  '河南投资集团 算力 数据中心 2026 site:hnic.com.cn',
  '河南能源集团 数智化 项目 2026 site:hnecgc.com'
]
for q in queries:
    print('====', q)
    req = json.dumps({'query': q, 'count': 5, 'freshness': 'pw'}, ensure_ascii=False)
    p = subprocess.run(['python3', 'skills/baidu-search/scripts/search.py', req], capture_output=True, text=True)
    out = p.stdout[:5000]
    print(out)
    print()
