import urllib.request, json

KEY = "YYMAagQ3cS0VIxh3oKgqDywCmhh5pKmuG7BvJj7YBaTwu9kx6owMVxYlK_JspPxU52p4fUha7is0IeKnuMNAHTt-Ls9BxhGHhvs"
DB_ID = "05f4a9d0-f883-4d12-a99e-53f092231295"
BASE = "https://gateway.maton.ai/notion/v1"

def req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Authorization', f'Bearer {KEY}')
    r.add_header('Content-Type', 'application/json')
    r.add_header('Notion-Version', '2025-09-03')
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

page = req("POST", "/pages", {
    "parent": {"database_id": DB_ID},
    "properties": {
        "文章标题": {"title": [{"text": {"content": "河南1010个源网荷储项目，数字化这道关怎么过？"}}]},
        "摘要": {"rich_text": [{"text": {"content": "河南分四批做了192个项目、290亿投资，现在一口气又押1010个。装机容量不是瓶颈，数字化能不能跟上才是关键。"}}]},
        "来源": {"multi_select": [{"name": "外部资料"}]},
    }
})

if "id" not in page:
    print("页面创建失败:", page)
    exit(1)

pid = page["id"]
print("页面创建成功:", pid)

paragraphs = [
    "作者：余炜勋 | 2026-03-02",
    "河南刚做完一件在全国算得上大手笔的事：四批次、192个源网荷储一体化项目、总投资约290亿元落地。绿电年均消纳80亿度，用电成本每年减少12亿到18亿元。然后，2024年12月，省里又发了一份方案，一口气安排了1010个新项目。",
    "装机容量不是瓶颈，数字化能不能跟上，才是这1010个项目能不能真正跑起来的关键。",
    "一、源网荷储的信息化在做什么",
    "把四层整合起来不难，难的是让这四层实时协同——储能什么时候充，什么时候放；负荷什么时候响应，让多少；源端出力明天大概是多少，今晚的调度策略怎么定。这就是信息化的核心工作：把四层的实时数据打通，用算法生成调度策略，用平台闭环执行与反馈。",
    "2026年1月9日投运的河南油田源网荷储一体化智慧能源管控平台，接入变电站、风电、光伏、储能等多源数据，通过智能算法优化储能充放电策略。国网河南电力2025年完成企业级数据中台建设，单日最大新能源消纳能力突破4000万千瓦，利用率同比提升0.7个百分点。数据治理，直接决定消纳能力上限。",
    "二、当前卡点",
    "四个卡点：①数据孤岛——不同厂商协议格式，数据进不了同一平台，调度成空谈。②预测精度不足——河南示范项目引入气象—负荷双因子预测模型，日负荷预测误差从15%降至8%，自发自用率升至78%，这是整个调度逻辑的可行性门槛。③接口标准缺失——每个项目定制集成，成本极高。④运营断层——验收后建设团队撤场，运营无人接手，三个月后指标和预期差一截。",
    "三、1010个项目的数字化机会",
    "工业类（最大盘子）：需要真正能算账的能源管控平台，实时监测+负荷预测+储能调度+电费结算一体化。增量配网类（决策链最短）：新建局域配电网，信息化方案最容易完整落地。农村类（兰考模式可复制）：轻量化能源管理系统，功能够用、部署简单、运维成本低。",
    "四、谁能接住这波机会",
    "不是卖设备的，不是做大屏的，是能把平台+数据+运营做成闭环的。从三个可验收结果倒推：①绿电消纳率——光伏发出来的电有多少真正被自己用掉；②电费节约额——每年实际少交多少，最有说服力的续约理由；③调度响应时长——区分能用和好用的分水岭。三个指标能在验收文件里写清楚、持续可测，项目就从建设型转向运营型。",
    "写在最后——能接住这波机会的，是那些能把数字化做成可验收结果的团队。不是方案最漂亮的，是能坐在甲方财务室里，翻出去年电费单，跟今年对账的。",
    "数据来源：河南省发改委 / 河南省源网荷储一体化实施方案（2024.12）/ 中石化新闻网 / 人民日报中国能源报 / 中国电力网",
]

blocks = [
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": p}}]}}
    for p in paragraphs
]

result = req("PATCH", f"/blocks/{pid}/children", {"children": blocks})
if "results" in result:
    print(f"正文写入成功，共{len(result['results'])}个块")
else:
    print("正文写入结果:", result)
