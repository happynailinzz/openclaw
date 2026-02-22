#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每天晨报（郑州天气 + 农历/节假日/五行穿衣）
- 天气：wttr.in JSON
- 农历/节假日/五行：读取用户提供的年度 JSON
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


def wuxing_summary(record: dict) -> tuple[list[str], str]:
    lunar = record.get("lunar", "-")
    solar_term = record.get("solar_term")
    holiday = record.get("holiday")
    rest_day = record.get("rest_day")

    wx = record.get("wuxing", {})
    day_stem = wx.get("day_stem", "-")
    day_wx = wx.get("day_wuxing", "-")
    guide = wx.get("guide", {})

    def g(name: str) -> tuple[str, str]:
        item = guide.get(name, {})
        element = item.get("element", "-")
        colors = item.get("colors", [])
        return element, "、".join(colors)

    guiren_el, guiren_colors = g("贵人")
    bijian_el, bijian_colors = g("比肩")
    jincai_el, jincai_colors = g("进财")
    xiaohao_el, xiaohao_colors = g("消耗")
    jiyong_el, jiyong_colors = g("忌用")

    parts = [
        "📅 今日黄历",
        f"- 农历：{lunar}",
        f"- 节气：{solar_term if solar_term else '无'}",
        f"- 节假日：{holiday if holiday else '无'}",
        f"- 作息：{'休息日' if rest_day else '工作日'}",
        f"- 日干五行：{day_stem}（{day_wx}）",
        "",
        "🎨 五行穿衣",
        f"- 贵人色：{guiren_el}（{guiren_colors}）",
        f"- 比肩色：{bijian_el}（{bijian_colors}）",
        f"- 进财色：{jincai_el}（{jincai_colors}）",
        f"- 消耗色：{xiaohao_el}（{xiaohao_colors}）",
        f"- 忌用色：{jiyong_el}（{jiyong_colors}）",
    ]

    yi_ji = f"今日宜：优先选「{guiren_colors}」或「{bijian_colors}」系；今日忌：尽量避开「{jiyong_colors}」系。"
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
        wx_lines, yi_ji = wuxing_summary(rec)
        lines.extend(wx_lines)
        lines.extend(["", f"✅ 今日宜忌：{yi_ji}"])
    else:
        lines.append("农历/节假日/五行：未在年度文件中找到当天记录。")

    lines.extend(["", "祝你今天顺顺利利，出门有好运。🥟"])
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
