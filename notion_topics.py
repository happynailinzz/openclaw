import urllib.request, os, json

DS_ID = '05f4a9d0-f883-4d12-a99e-53f092231295'
KEY = os.environ["MATON_API_KEY"]

topics = [
    {
        "title": "矿安〔2026〕1号：那些一直拖着没做智能化的矿山，今年没法再等了",
        "summary": "2026年1月国家矿山安全监察局印发矿安〔2026〕1号文，28条硬措施首次将矿山智能化建设与安全生产合规硬挂钩。透明地质、智能掘进、AI巡检、无人驾驶装备成为强制方向。角度：不是政策解读八股文，是帮读者看清楚——这次有真约束，不上智能化=踩安全合规红线。",
        "direction": "油气矿山智能化",
        "themes": ["矿山智能化", "政策解读", "安全生产"],
        "sources": ["外部"],
    },
    {
        "title": "从示范到强制：十五五智能矿山的时间表，你看清楚了吗？",
        "summary": "十四五靠66处国家级示范矿山带动，十五五要求60%以上煤矿实现自动化，非煤矿山智能化建设指南（2025年版）已落地。帮读者看清2026-2030年各类矿山必须完成的智能化指标与对应采购、改造窗口期。",
        "direction": "油气矿山智能化",
        "themes": ["矿山智能化", "十五五", "政策解读"],
        "sources": ["外部"],
    },
    {
        "title": "矿山智能化的中原机会：河南凭什么能接住这波产业升级？",
        "summary": "河南是全国重要的煤炭、有色金属、铝土矿产地，郑州有工业互联网加能源数字化产业基础。帮本地政企读者建立认知——矿山智能化是一波有地域机会的产业升级浪潮，中原不是旁观者。需补充本地案例或数据支撑。",
        "direction": "油气矿山智能化",
        "themes": ["矿山智能化", "中原机会", "产业升级"],
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
    print("OK", t["title"][:30], "->", res.get("id"))
