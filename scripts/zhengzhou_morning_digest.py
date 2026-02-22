#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每天晨报（郑州天气 + 农历/节假日/五行穿衣）
- 天气：wttr.in JSON
- 农历/节假日/五行：读取用户提供的年度 JSON
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CITY = "郑州"
TZ = timezone(timedelta(hours=8))  # Asia/Shanghai
WUXING_JSON = Path("/root/daily_wuxing_2026.json")


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
        f"{city}天气：{desc}，{min_t}~{max_t}℃，当前{temp}℃（体感{feels}℃），"
        f"湿度{humidity}%，降雨概率约{rain_prob}%。"
    )

    # 穿衣建议（按体感+降雨+湿度）
    try:
        f = int(feels)
    except Exception:
        f = 20

    if f <= 5:
        wear = "厚羽绒/呢大衣 + 保暖内搭，围巾可安排。"
    elif f <= 12:
        wear = "厚外套（棉服/毛呢）+ 针织打底，早晚注意防风。"
    elif f <= 18:
        wear = "夹克/风衣 + 长袖，体感偏凉时加一层薄针织。"
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


def wuxing_summary(record: dict) -> list[str]:
    lunar = record.get("lunar", "-")
    solar_term = record.get("solar_term")
    holiday = record.get("holiday")
    rest_day = record.get("rest_day")

    wx = record.get("wuxing", {})
    day_stem = wx.get("day_stem", "-")
    day_wx = wx.get("day_wuxing", "-")
    guide = wx.get("guide", {})

    parts = [f"农历：{lunar}"]
    if solar_term:
        parts.append(f"节气：{solar_term}")
    parts.append(f"节假日：{holiday if holiday else '无'}")
    parts.append("作息：休息日" if rest_day else "作息：工作日")
    parts.append(f"日干五行：{day_stem}（{day_wx}）")

    def g(name: str) -> str:
        item = guide.get(name, {})
        colors = "、".join(item.get("colors", []))
        element = item.get("element", "-")
        return f"{name}：{element}（{colors}）"

    parts.append("五行穿衣：")
    parts.append(f"- {g('贵人')}")
    parts.append(f"- {g('比肩')}")
    parts.append(f"- {g('进财')}")
    parts.append(f"- {g('消耗')}")
    parts.append(f"- {g('忌用')}")

    return parts


def main() -> int:
    today = datetime.now(TZ).date().isoformat()

    try:
        weather_line, wear_line = weather_summary(CITY)
    except Exception as e:
        weather_line = f"{CITY}天气：获取失败（{e}）"
        wear_line = "穿衣建议：天气数据异常，建议按体感分层穿搭。"

    lines = [
        f"早安，今天是 {today}",
        weather_line,
        wear_line,
        "",
    ]

    rec = load_wuxing_record(today)
    if rec:
        lines.extend(wuxing_summary(rec))
    else:
        lines.append("农历/节假日/五行：未在年度文件中找到当天记录。")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
