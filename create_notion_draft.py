import urllib.request, os, json
from datetime import datetime

url = 'https://gateway.maton.ai/notion/v1/pages'
api_key = os.environ.get("MATON_API_KEY", "")

# Article content
title = "【切中当下痛点】AI 狂欢退潮后，政企数字化拿什么做“保底”？"
content = """# AI 狂欢退潮后，政企数字化拿什么做“保底”？

## 【引言：现象与刺痛】
这两年只要是个项目，不贴个“大模型”或“AI”标签都不好意思立项。大家一窝蜂建智算中心、买大模型服务。

潮水退去，很多地方政府和国企发现：买来的算力闲置了；接好的模型除了聊天写公文，根本下不去核心业务；花了大价钱的项目，最后连个能对上账的“业务结果”都验收不了。

当 AI 的滤镜碎了，政企数字化到底靠什么“保底”？

## 【核心板块一：为什么只买“技术”保不住底？】
盲区 1：有算力无数据。以为买了几十台服务器就是智能化，结果内部业务数据像下水道一样混乱，模型根本“吃”不到有用的业务口粮。
盲区 2：有模型无流程。试图用一个全能模型解决所有问题，却连自己原有的核心审批/生产流程都没梳理清楚。AI 只是挂在墙上的屏幕，没融进业务的血液里。

结论：单点技术外包商只会交给你一套“跑得通的代码”，但不管你“跑不跑得出业务利润/效率”。

## 【核心板块二：什么才是真正的“保底”？】
真正的保底，是让数字化从“花钱的基建”变成“看得见结果的资产”。

咨询规划（大脑）：别上来就买设备。先帮政企算账——你的痛点是什么？政策允许的边界在哪？能产生什么可量化的经济/社会效益？
系统集成与产品（躯干）：把算力中心、网络、模型、数据打通。不是做拼盘，而是做一套能跑通业务流程的系统。
生态与资金（血液）：很多政企想做但缺钱。靠谱的服务商不光给方案，还能拿着方案去对接专项债、产业基金，这才是真正的降维打击。

## 【结尾：回归商业本质的呼吁】
不管概念怎么变，政企数字化的第一性原理没变：解决实际问题，达成验收指标，实现资产增值。

别把数字化做成“样板间”，要做成能转起来的“流水线”。寰曜数能的“四位一体”，就是为了帮政企客户兜住这个底，让每一分投入都有闭环。
"""

# Current date in ISO format
today_iso = datetime.now().strftime("%Y-%m-%d")

payload = {
  "parent": {"database_id": "a8a41765-aec8-417e-8764-7506465bb42f"},
  "properties": {
    "文章标题": {
      "title": [{"text": {"content": title}}]
    },
    "选题方向": {
      "select": {"name": "商业"}
    },
    "状态": {
      "select": {"name": "写作中"}
    },
    "来源": {
      "multi_select": [{"name": "知识库"}, {"name": "延伸"}]
    },
    "类型": {
      "select": {"name": "草稿"}
    },
    "主题方向": {
      "multi_select": [{"name": "国资信创"}, {"name": "AI应用落地"}, {"name": "数据治理"}]
    },
    "选题时间": {
      "date": {"start": today_iso}
    }
  },
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": content
            }
          }
        ]
      }
    }
  ]
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')

req.add_header('Authorization', f'Bearer {api_key}')
req.add_header('Content-Type', 'application/json')
req.add_header('Notion-Version', '2022-06-28')

try:
    with urllib.request.urlopen(req) as response:
        print("Success! Page created.")
        print(json.dumps(json.load(response), indent=2))
except urllib.error.URLError as e:
    if hasattr(e, 'read'):
        print(f"Error: {e.code} - {e.read().decode('utf-8')}")
    else:
        print(f"Error: {e}")
