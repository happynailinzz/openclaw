#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每天晨报（郑州天气 + 农历/节假日/五行穿衣）
- 天气：wttr.in JSON
- 农历/节假日：读取用户提供的年度 JSON
- 五行穿衣：优先按“日地支五行”推导（用户指定口径）
- 文案风格：公众号口吻 + emoji + 今日宜忌
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CITY = "郑州"
TZ = timezone(timedelta(hours=8))  # Asia/Shanghai
WUXING_JSON = Path("/root/daily_wuxing_2026.json")

# 五行 -> 颜色
WUXING_COLORS = {
    "木": ["绿", "青", "翠绿", "浅绿"],
    "火": ["红", "粉", "紫", "橙红"],
    "土": ["黄", "咖", "棕", "褐", "橙黄"],
    "金": ["白", "银", "灰", "米白", "乳白"],
    "水": ["黑", "蓝", "深蓝", "藏蓝"],
}

# 相生 / 相克
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
SHENG_INV = {v: k for k, v in SHENG.items()}  # 谁生我
KE_INV = {v: k for k, v in KE.items()}  # 谁克我

# 地支 -> 五行（用户指定口径）
BRANCH_TO_WUXING = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


def fetch_weather(city: str) -> dict:
    q = urllib.parse.quote(city)
    url = f"https://wttr.in/{q}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def weather_summary(city: str) -> tuple[str, str]:
    data = fetch_weather(city)

    current = data["current_condition"][0]
    today = data["weather"][0]

    desc = current.get("weatherDesc", [{"value": ""}])[0].get("value", "未知")
    temp = current.get("temp_C", "?")
    feels = current.get("FeelsLikeC", "?")
    humidity = current.get("humidity", "?")

    max_t = today.get("maxtempC", "?")
    min_t = today.get("mintempC", "?")
    hourly = today.get("hourly", [])
    rain_prob = max((int(h.get("chanceofrain", "0")) for h in hourly), default=0)

    weather_line = (
        f"{city}：{desc}，{min_t}~{max_t}℃，当前{temp}℃（体感{feels}℃），"
        f"湿度{humidity}%，降雨概率约{rain_prob}%。"
    )

    # 穿衣建议（按体感+降雨+湿度）
    try:
        f = int(feels)
    except Exception:
        f = 20

    if f <= 5:
        wear = "厚羽绒/呢大衣 + 保暖内搭，围巾手套建议安排。"
    elif f <= 12:
        wear = "厚外套（棉服/毛呢）+ 针织打底，早晚防风。"
    elif f <= 18:
        wear = "夹克/风衣 + 长袖，体感偏凉可加薄针织。"
    elif f <= 25:
        wear = "长袖或薄外套即可，通勤体感舒适。"
    else:
        wear = "短袖为主，注意防晒和补水。"

    extras = []
    if rain_prob >= 40:
        extras.append("带伞")
    if int(humidity) >= 80 if str(humidity).isdigit() else False:
        extras.append("可选速干材质")

    if extras:
        wear += "（" + "，".join(extras) + "）"

    return weather_line, f"穿衣建议：{wear}"


def load_wuxing_record(target_date: str) -> dict | None:
    if not WUXING_JSON.exists():
        return None
    data = json.loads(WUXING_JSON.read_text(encoding="utf-8"))
    for row in data:
        if row.get("date") == target_date:
            return row
    return None


def get_day_branch_wuxing(target_date: str) -> tuple[str | None, str | None, str]:
    """
    返回: (日地支, 当日五行, 口径说明)
    优先：日地支五行；回退：JSON中的日干五行
    """
    try:
        from lunar_python import Solar

        y, m, d = [int(x) for x in target_date.split("-")]
        lunar = Solar.fromYmd(y, m, d).getLunar()
        day_zhi = lunar.getDayZhi()
        day_wuxing = BRANCH_TO_WUXING.get(day_zhi)
        if day_wuxing:
            return day_zhi, day_wuxing, "日地支"
    except Exception:
        pass

    # 回退：用年度文件里已有的日干五行
    rec = load_wuxing_record(target_date)
    if rec:
        wx = rec.get("wuxing", {})
        return None, wx.get("day_wuxing"), "日干(回退)"

    return None, None, "未知"


def build_5_tiers(day_wuxing: str) -> dict:
    """
    按用户规则固定五档：
    1) 贵人色：被当日五行生（X生Y中的Y）
    2) 合作色：同当日五行（X）
    3) 进财色：克当日五行（克X者）
    4) 消耗色：生当日五行（生X者）
    5) 不利色：被当日五行克（X克者）
    """
    guiren = SHENG[day_wuxing]      # 被X生
    hezuo = day_wuxing              # 同X
    jincai = KE_INV[day_wuxing]     # 克X
    xiaohao = SHENG_INV[day_wuxing] # 生X
    buli = KE[day_wuxing]           # 被X克

    return {
        "贵人色": {"element": guiren, "colors": WUXING_COLORS[guiren]},
        "合作色": {"element": hezuo, "colors": WUXING_COLORS[hezuo]},
        "进财色": {"element": jincai, "colors": WUXING_COLORS[jincai]},
        "消耗色": {"element": xiaohao, "colors": WUXING_COLORS[xiaohao]},
        "不利色": {"element": buli, "colors": WUXING_COLORS[buli]},
    }


def wuxing_summary(record: dict, target_date: str) -> tuple[list[str], str]:
    lunar = record.get("lunar", "-")
    solar_term = record.get("solar_term")
    holiday = record.get("holiday")
    rest_day = record.get("rest_day")

    day_zhi, day_wuxing, basis = get_day_branch_wuxing(target_date)
    if not day_wuxing:
        day_wuxing = "木"  # 极端兜底
        basis = "默认兜底"

    tiers = build_5_tiers(day_wuxing)

    def line(name: str) -> str:
        item = tiers[name]
        return f"- {name}：{item['element']}（{'、'.join(item['colors'])}）"

    basis_text = f"{basis}{'（' + day_zhi + '）' if day_zhi else ''}"

    parts = [
        "📅 今日黄历",
        f"- 农历：{lunar}",
        f"- 节气：{solar_term if solar_term else '无'}",
        f"- 节假日：{holiday if holiday else '无'}",
        f"- 作息：{'休息日' if rest_day else '工作日'}",
        f"- 当日五行：{day_wuxing}（口径：{basis_text}）",
        "",
        "🎨 五行穿衣（固定五档）",
        line("贵人色"),
        line("合作色"),
        line("进财色"),
        line("消耗色"),
        line("不利色"),
    ]

    yi = "、".join(tiers["贵人色"]["colors"][:2]) + " / " + "、".join(tiers["合作色"]["colors"][:2])
    ji = "、".join(tiers["不利色"]["colors"][:2])
    yi_ji = f"今日宜：优先选「{yi}」系；今日忌：尽量避开「{ji}」系。"
    return parts, yi_ji


def main() -> int:
    today = datetime.now(TZ).date().isoformat()

    try:
        weather_line, wear_line = weather_summary(CITY)
    except Exception as e:
        weather_line = f"{CITY}天气：获取失败（{e}）"
        wear_line = "穿衣建议：天气数据异常，建议按体感分层穿搭。"

    lines = [
        f"🌤️ 郑州晨报｜{today}",
        "",
        "【天气与穿搭】",
        weather_line,
        f"👔 {wear_line}",
        "",
    ]

    rec = load_wuxing_record(today)
    if rec:
        wx_lines, yi_ji = wuxing_summary(rec, today)
        lines.extend(wx_lines)
        lines.extend(["", f"✅ 今日宜忌：{yi_ji}"])
    else:
        lines.append("农历/节假日/五行：未在年度文件中找到当天记录。")

    lines.extend(["", "祝你今天顺顺利利，出门有好运。🥟"])
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
