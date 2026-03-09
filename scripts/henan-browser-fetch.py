#!/usr/bin/env python3
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from urllib.parse import urlparse

ROUTING_PATH = "/root/.openclaw/workspace/config/henan-source-routing.json"
CDP_BASE = "http://127.0.0.1:9222"


def load_routing():
    with open(ROUTING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mode(host, routing):
    for item in routing.get("browserFetch", []):
        if item.get("host") == host:
            return "browser_cdp", item
    for item in routing.get("fallbackOnly", []):
        if item.get("host") == host:
            return "fallback_only", item
    return "direct", None


def cdp_new_tab(url):
    req = urllib.request.Request(CDP_BASE + "/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def cdp_list():
    with urllib.request.urlopen(CDP_BASE + "/json/list", timeout=10) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage", "message": "henan-browser-fetch.py <url>"}, ensure_ascii=False))
        sys.exit(2)

    url = sys.argv[1]
    host = urlparse(url).netloc
    routing = load_routing()
    mode, _item = get_mode(host, routing)

    if mode == "fallback_only":
        rule = routing.get("fallbackRules", {}).get(host, {})
        print(json.dumps({
            "ok": False,
            "mode": mode,
            "host": host,
            "url": url,
            "status": rule.get("statusLabel", "原站受限"),
            "strategy": rule.get("strategy", []),
        }, ensure_ascii=False))
        return

    if mode == "browser_cdp":
        page = cdp_new_tab(url)
        time.sleep(3)
        tabs = cdp_list()
        match = None
        for t in tabs:
            if t.get("id") == page.get("id"):
                match = t
                break
        print(json.dumps({
            "ok": True,
            "mode": mode,
            "host": host,
            "url": url,
            "tabId": page.get("id"),
            "title": (match or {}).get("title", ""),
            "pageUrl": (match or {}).get("url", url),
            "note": "CDP tab opened; use tab title/url as browser-level availability signal."
        }, ensure_ascii=False))
        return

    print(json.dumps({"ok": False, "mode": mode, "host": host, "url": url, "message": "host not routed; use normal fetch"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
