#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from http_stable import request_text, request_json

DEFAULT_DS_ID = "31170dc2-6079-8003-bc57-000bd143337d"  # 微信公众号文章库
NOTION_VERSION = "2025-09-03"
BASE = "https://gateway.maton.ai/notion/v1"


def eprint(*args):
    print(*args, file=sys.stderr)


def http_get(url, timeout=60):
    raw, _trace = request_text(
        "GET",
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
        retries=3,
        backoff_base_s=0.8,
        backoff_max_s=10.0,
        jitter_s=0.3,
    )
    return raw


def notion_request(method, path, key, payload=None, timeout=60):
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Notion-Version", NOTION_VERSION)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def parse_x_url(url):
    m = re.search(r"x\.com/([^/]+)/status/(\d+)", url)
    if not m:
        m = re.search(r"twitter\.com/([^/]+)/status/(\d+)", url)
    if not m:
        raise ValueError("URL 格式不正确，需包含 /<user>/status/<id>")
    return m.group(1), m.group(2)


def extract_payload(raw_text):
    title = None
    published = None
    markdown = None

    mt = re.search(r"Title:\s*(.*?)\s*/\s*X", raw_text)
    if mt:
        title = mt.group(1).strip()

    mp = re.search(r"Published Time:\s*(.*?)\n", raw_text)
    if mp:
        published = mp.group(1).strip()

    mm = re.search(r"Markdown Content:\n(.*)", raw_text, flags=re.S)
    if mm:
        markdown = mm.group(1).strip()
    else:
        markdown = raw_text.strip()

    return title, published, markdown


def looks_blocked(markdown):
    bad_markers = [
        "Don’t miss what’s happening",
        "Something went wrong, but don’t fret",
        "See new posts",
        "Log in",
    ]
    if len(markdown) < 200:
        return True
    return any(x in markdown for x in bad_markers)


def fetch_best(username, tweet_id):
    candidates = [
        ("x-direct", f"https://r.jina.ai/http://x.com/{username}/status/{tweet_id}"),
        ("vxtwitter", f"https://r.jina.ai/http://vxtwitter.com/{username}/status/{tweet_id}"),
        ("fxtwitter", f"https://r.jina.ai/http://fxtwitter.com/{username}/status/{tweet_id}"),
    ]

    last = None
    for source, url in candidates:
        try:
            raw = http_get(url)
            title, published, markdown = extract_payload(raw)
            if not looks_blocked(markdown):
                return {
                    "source": source,
                    "fetch_url": url,
                    "title": title,
                    "published": published,
                    "markdown": markdown,
                }
            last = {
                "source": source,
                "fetch_url": url,
                "title": title,
                "published": published,
                "markdown": markdown,
            }
        except Exception as ex:
            last = {"source": source, "fetch_url": url, "error": str(ex)}

    return last


def parse_publish_date(published):
    if not published:
        return None
    for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S GMT"]:
        try:
            return dt.datetime.strptime(published, fmt).date().isoformat()
        except Exception:
            pass
    return None


def build_properties(title, url, username, note, publish_date=None):
    props = {
        "文章标题": {"title": [{"text": {"content": title[:180]}}]},
        "文章链接": {"url": url},
        "公众号名称": {"rich_text": [{"text": {"content": f"X / {username}"}}]},
        "笔记": {"rich_text": [{"text": {"content": note[:1800]}}]},
        "收藏日期": {"date": {"start": dt.date.today().isoformat()}},
        "阅读状态": {"status": {"name": "阅读中"}},
        "分类": {"select": {"name": "技术"}},
        "标签": {"multi_select": [{"name": "技术"}, {"name": "行业动态"}]},
    }
    if publish_date:
        props["发布日期"] = {"date": {"start": publish_date}}
    return props


def get_children(block_id, key):
    out = []
    cursor = None
    while True:
        path = f"/blocks/{block_id}/children"
        if cursor:
            path += "?start_cursor=" + urllib.parse.quote(cursor)
        resp = notion_request("GET", path, key)
        out.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return out


def clear_children(block_id, key):
    children = get_children(block_id, key)
    for b in children:
        bid = b.get("id")
        if not bid:
            continue
        try:
            notion_request("DELETE", f"/blocks/{bid}", key)
        except Exception:
            pass


def chunk_text(text, size=1800):
    i = 0
    while i < len(text):
        yield text[i : i + size]
        i += size


def append_markdown(page_id, original_url, source_name, markdown, key):
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "原文（X 抽取）"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"来源链接：{original_url}"}}]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"抓取链路：{source_name}"}}]
            },
        },
    ]

    parts = [p.strip() for p in re.split(r"\n\s*\n", markdown) if p.strip()]
    for p in parts:
        for c in chunk_text(p):
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": c}}]
                    },
                }
            )

    for i in range(0, len(blocks), 80):
        notion_request(
            "PATCH",
            f"/blocks/{page_id}/children",
            key,
            payload={"children": blocks[i : i + 80]},
        )
    return len(blocks)


def main():
    parser = argparse.ArgumentParser(description="X 链接抓正文并入库 Notion（微信公众号文章库）")
    parser.add_argument("url", help="x.com 或 twitter.com 的 status 链接")
    parser.add_argument("--data-source-id", default=DEFAULT_DS_ID, help="Notion 数据源 ID")
    parser.add_argument("--page-id", default=None, help="已有页面ID（传入则覆盖更新）")
    args = parser.parse_args()

    key = os.environ.get("MATON_API_KEY")
    if not key:
        print("ERROR: MATON_API_KEY 未设置", file=sys.stderr)
        sys.exit(2)

    username, tweet_id = parse_x_url(args.url)
    fetched = fetch_best(username, tweet_id)

    if not fetched or (not fetched.get("markdown")):
        print(json.dumps({"ok": False, "error": "抓取失败", "detail": fetched}, ensure_ascii=False))
        sys.exit(1)

    markdown = fetched.get("markdown", "")
    title = fetched.get("title") or f"X帖子收藏｜{username}/{tweet_id}"
    publish_date = parse_publish_date(fetched.get("published"))

    blocked = looks_blocked(markdown)
    if blocked:
        note = "抓取受限，仅保存链接与占位，待后续补全文。"
    else:
        note = f"已补正文（来源：{fetched.get('source')} + r.jina.ai）。"

    props = build_properties(
        title=title,
        url=args.url,
        username=username,
        note=note,
        publish_date=publish_date,
    )

    if args.page_id:
        page = notion_request("PATCH", f"/pages/{args.page_id}", key, payload={"properties": props})
        page_id = args.page_id
    else:
        payload = {"parent": {"data_source_id": args.data_source_id}, "properties": props}
        page = notion_request("POST", "/pages", key, payload=payload)
        page_id = page.get("id")

    blocks_written = 0
    if not blocked:
        clear_children(page_id, key)
        blocks_written = append_markdown(page_id, args.url, fetched.get("source", "unknown"), markdown, key)

    print(
        json.dumps(
            {
                "ok": True,
                "page_id": page_id,
                "url": page.get("url"),
                "title": title,
                "publish_date": publish_date,
                "source": fetched.get("source"),
                "blocked": blocked,
                "blocks_written": blocks_written,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
