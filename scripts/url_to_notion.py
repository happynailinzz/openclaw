#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from http_stable import request_json

DEFAULT_DS_ID = "31170dc2-6079-8003-bc57-000bd143337d"  # 微信公众号文章库
NOTION_VERSION = "2025-09-03"
NOTION_BASE = "https://gateway.maton.ai/notion/v1"


def notion_request(method, path, key, payload=None, timeout=60):
    out, _trace = request_json(
        method,
        f"{NOTION_BASE}{path}",
        headers={
            "Authorization": f"Bearer {key}",
            "Notion-Version": NOTION_VERSION,
        },
        payload=payload,
        timeout=timeout,
        retries=3,
        backoff_base_s=0.8,
        backoff_max_s=10.0,
        jitter_s=0.3,
    )
    return out


def http_get(url, timeout=60):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def safe_url_for_jina(url: str) -> str:
    # r.jina.ai accepts http://example or https://example. keep original as much as possible
    if not re.match(r"^https?://", url):
        url = "https://" + url
    return "https://r.jina.ai/http://" + re.sub(r"^https?://", "", url)


def extract_from_jina(raw_text):
    title = None
    published = None
    markdown = None

    mt = re.search(r"Title:\s*(.*?)\n", raw_text)
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

    # strip safety wrappers if present
    markdown = re.sub(r"^SECURITY NOTICE:.*?<<<EXTERNAL_UNTRUSTED_CONTENT[^>]*>>>\n", "", markdown, flags=re.S)
    markdown = re.sub(r"\n<<<END_EXTERNAL_UNTRUSTED_CONTENT[^>]*>>>\s*$", "", markdown, flags=re.S)
    return title, published, markdown.strip()


def parse_publish_date(published):
    if not published:
        return None
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%d",
    ]:
        try:
            return dt.datetime.strptime(published, fmt).date().isoformat()
        except Exception:
            pass
    return None


def looks_blocked(markdown):
    markers = [
        "Something went wrong, but don’t fret",
        "Don’t miss what’s happening",
        "Please disable",
        "captcha",
        "Access Denied",
    ]
    if len(markdown) < 120:
        return True
    low = markdown.lower()
    return any(m.lower() in low for m in markers)


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


def chunks(text, size=1800):
    i = 0
    while i < len(text):
        yield text[i : i + size]
        i += size


def append_markdown(page_id, original_url, source, markdown, key):
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "原文（URL 抽取）"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"来源链接：{original_url}"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"抓取链路：{source}"}}]},
        },
    ]

    parts = [p.strip() for p in re.split(r"\n\s*\n", markdown) if p.strip()]
    for p in parts:
        for c in chunks(p):
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": c}}]},
                }
            )

    for i in range(0, len(blocks), 80):
        notion_request("PATCH", f"/blocks/{page_id}/children", key, payload={"children": blocks[i : i + 80]})
    return len(blocks)


def domain_of(url):
    p = urllib.parse.urlparse(url if re.match(r"^https?://", url) else "https://" + url)
    return p.netloc.lower()


def main():
    ap = argparse.ArgumentParser(description="任意 URL 抓正文并入库 Notion（微信公众号文章库）")
    ap.add_argument("url", help="网页链接（支持 mp.weixin.qq.com 与普通网站）")
    ap.add_argument("--data-source-id", default=DEFAULT_DS_ID, help="Notion 数据源 ID")
    ap.add_argument("--page-id", default=None, help="已有页面ID（传入则覆盖更新）")
    ap.add_argument("--dry-run", action="store_true", help="只抓取不写 Notion")
    args = ap.parse_args()

    key = os.environ.get("MATON_API_KEY")
    if not key and not args.dry_run:
        print("ERROR: MATON_API_KEY 未设置", file=sys.stderr)
        sys.exit(2)

    original_url = args.url if re.match(r"^https?://", args.url) else "https://" + args.url
    fetch_url = safe_url_for_jina(original_url)
    raw = http_get(fetch_url)
    title, published, markdown = extract_from_jina(raw)

    dom = domain_of(original_url)
    publish_date = parse_publish_date(published)
    if not title or title in ["X", "Untitled"]:
        title = f"网页收藏｜{dom}"

    blocked = looks_blocked(markdown)
    note = (
        f"已补正文（来源：r.jina.ai）。"
        if not blocked
        else "抓取受限，仅保存链接与占位，待后续补全文。"
    )

    result = {
        "ok": True,
        "title": title,
        "domain": dom,
        "publish_date": publish_date,
        "blocked": blocked,
        "fetch_url": fetch_url,
        "preview": markdown[:300],
    }

    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    props = {
        "文章标题": {"title": [{"text": {"content": title[:180]}}]},
        "文章链接": {"url": original_url},
        "公众号名称": {"rich_text": [{"text": {"content": dom}}]},
        "笔记": {"rich_text": [{"text": {"content": note}}]},
        "收藏日期": {"date": {"start": dt.date.today().isoformat()}},
        "阅读状态": {"status": {"name": "阅读中" if not blocked else "未读"}},
        "分类": {"select": {"name": "技术"}},
        "标签": {"multi_select": [{"name": "行业动态"}]},
    }
    if publish_date:
        props["发布日期"] = {"date": {"start": publish_date}}

    if args.page_id:
        page = notion_request("PATCH", f"/pages/{args.page_id}", key, payload={"properties": props})
        page_id = args.page_id
    else:
        page = notion_request(
            "POST",
            "/pages",
            key,
            payload={"parent": {"data_source_id": args.data_source_id}, "properties": props},
        )
        page_id = page.get("id")

    blocks_written = 0
    if not blocked:
        clear_children(page_id, key)
        blocks_written = append_markdown(page_id, original_url, "r.jina.ai", markdown, key)

    result.update({"page_id": page_id, "url": page.get("url"), "blocks_written": blocks_written})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
