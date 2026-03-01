import urllib.request, os, json

DS_ID = '05f4a9d0-f883-4d12-a99e-53f092231295'
KEY = os.environ["MATON_API_KEY"]

topics = [
    {
        "title": "郑州怎么成了算力之城？一家公司，三年，430亿",
        "summary": "2025年郑州完成历史性身份转换，从千年商都到算力之城。拆解超聚变3年从0到430亿的路径，以及一家龙头企业如何带动郑州整条算力产业链跃迁。数据锚点：超聚变430亿营收、郑州AI产业规模350亿、全省100+算力中心布局。适合关注中原产业机会的政企决策者。",
        "direction": "河南AI发展",
        "themes": ["算力", "郑州", "产业升级", "超聚变"],
        "sources": ["外部"],
    },
    {
        "title": "河南喊了500个AI场景，哪些是真的在跑？",
        "summary": "河南省AI+行动计划锁定医疗、教育、工业、农业、文旅、政务等9大行业，首批13家AI行业赋能中心已挂牌，500个典型应用场景目标。本文区分真实落地场景（AI诊疗、智慧养殖、工业质检、政务审批）与停留在PPT里的场景，反常识角度切入。",
        "direction": "河南AI发展",
        "themes": ["人工智能+", "场景落地", "河南", "行业应用"],
        "sources": ["外部"],
    },
    {
        "title": "河南算力全国前列，为什么大模型还是要靠引进来？",
        "summary": "河南算力基础设施投入大、排名靠前，但大模型研发能力仍依赖外省头部（科大讯飞、华为、百度等来豫合作），本地原生大模型几乎空白。拆解算力底座与AI软实力之间的差距，以及河南下一步补课的方向。深度分析向，需补充本地数据。",
        "direction": "河南AI发展",
        "themes": ["大模型", "算力", "河南", "产业短板"],
        "sources": ["外部", "延伸"],
    },
    {
        "title": "河南工厂里的AI，真实落地进度是什么？",
        "summary": "河南是全国重要制造业大省，AI赋能新型工业化是省级战略。工业AI落地难点：场景数据稀缺、工人接受度低、改造周期长。具体切入：超聚变液冷服务器进工厂、郑州富士康智能化改造、洛阳装备制造AI质检。适合制造业负责人和政企数字化决策者。",
        "direction": "河南AI发展",
        "themes": ["工业AI", "制造业", "河南", "数字化转型"],
        "sources": ["外部"],
    },
    {
        "title": "郑州AI场景战略地图出来了，你的机会在哪格？",
        "summary": "郑州2025年已出台十五五AI+场景战略布局，聚能大算力+大模型路线明确。以政策地图为基础，拆解场景优先级、哪类企业能接住、怎么进入。适合想在河南AI产业链找位置的企业和政策敏感型投资者，与寰曜数能业务直接相关，适合对外提案型内容。",
        "direction": "河南AI发展",
        "themes": ["郑州", "AI场景", "十五五", "产业机会"],
        "sources": ["外部", "延伸"],
    },
]

for t in topics:
    payload = {
        "parent": {"data_source_id": DS_ID},
        "properties": {
            "文章标题": {"title": [{"text": {"content": t["title"]}}]},
            "摘要": {"rich_text": [{"text": {"content": t["summary"]}}]},
            "选题方向": {"select": {"name": t["direction"]}},
            "主题方向": {"multi_select": [{"name": n} for n in t["themes"]]},
            "来源": {"multi_select": [{"name": n} for n in t["sources"]]},
            "类型": {"select": {"name": "选题"}},
            "状态": {"select": {"name": "待写"}},
            "选题时间": {"date": {"start": "2026-02-28"}},
        }
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request('https://gateway.maton.ai/notion/v1/pages', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {KEY}')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Notion-Version', '2025-09-03')
    res = json.load(urllib.request.urlopen(req))
    print("OK", t["title"][:28], "->", res.get("id"))
