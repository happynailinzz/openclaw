#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

NOTION_VERSION = "2025-09-03"
NOTION_BASE = "https://gateway.maton.ai/notion/v1"
DEFAULT_DS_ID = "31170dc2-6079-8003-bc57-000bd143337d"  # 微信公众号文章库


def notion_request(method, path, key, payload=None, timeout=60):
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{NOTION_BASE}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Notion-Version", NOTION_VERSION)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def parse_md(md: str):
    title = None
    author = None

    m = re.search(r"^title:\s*\"?(.*?)\"?$", md, flags=re.M)
    if m:
        title = m.group(1).strip()

    ma = re.search(r"^author:\s*\"?(.*?)\"?$", md, flags=re.M)
    if ma:
        author = ma.group(1).strip()

    if not title:
        mh = re.search(r"^#\s+(.+?)\s*$", md, flags=re.M)
        if mh:
            title = mh.group(1).strip()

    if not title:
        title = "网页摘录"

    return title, author or "mp.weixin.qq.com"


def chunks(text, size=1500):
    i = 0
    while i < len(text):
        yield text[i : i + size]
        i += size


def get_children(block_id, key):
    out = []
    cursor = None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if cursor:
            path += "&start_cursor=" + urllib.parse.quote(cursor)
        resp = notion_request("GET", path, key)
        out.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return out


def clear_children(block_id, key):
    for b in get_children(block_id, key):
        bid = b.get("id")
        if not bid:
            continue
        try:
            notion_request("DELETE", f"/blocks/{bid}", key)
        except Exception:
            pass


def append_md(page_id, url, md, key):
    content = f"来源链接：{url}\n\n{md}".strip()
    blocks = []
    for c in chunks(content, 1500):
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": c}}]},
        })

    written = 0
    for i in range(0, len(blocks), 80):
        batch = blocks[i : i + 80]
        notion_request("PATCH", f"/blocks/{page_id}/children", key, payload={"children": batch})
        written += len(batch)
    return written


def main():
    ap = argparse.ArgumentParser(description="把本地 markdown 正文写入微信公众号文章库（Notion）")
    ap.add_argument("--url", required=True, help="原文链接")
    ap.add_argument("--md", required=True, help="本地 markdown 文件路径")
    ap.add_argument("--data-source-id", default=DEFAULT_DS_ID)
    ap.add_argument("--page-id", default=None, help="已有页面ID（传入则覆盖更新）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    md_path = Path(args.md)
    if not md_path.exists():
        print(f"ERROR: markdown 文件不存在: {md_path}", file=sys.stderr)
        sys.exit(2)

    md = md_path.read_text(encoding="utf-8", errors="ignore")
    title, author = parse_md(md)
    today = dt.date.today().isoformat()

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "title": title,
            "author": author,
            "md_chars": len(md),
            "url": args.url,
        }, ensure_ascii=False, indent=2))
        return

    key = os.environ.get("MATON_API_KEY")
    if not key:
        print("ERROR: MATON_API_KEY 未设置", file=sys.stderr)
        sys.exit(3)

    props = {
        "文章标题": {"title": [{"text": {"content": title[:180]}}]},
        "文章链接": {"url": args.url},
        "公众号名称": {"rich_text": [{"text": {"content": author[:180]}}]},
        "笔记": {"rich_text": [{"text": {"content": "已通过本地有头浏览器抓取并入库。"}}]},
        "收藏日期": {"date": {"start": today}},
        "阅读状态": {"status": {"name": "阅读中"}},
        "分类": {"select": {"name": "技术"}},
        "标签": {"multi_select": [{"name": "行业动态"}]},
    }

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

    clear_children(page_id, key)
    written = append_md(page_id, args.url, md, key)

    print(json.dumps({
        "ok": True,
        "page_id": page_id,
        "url": page.get("url"),
        "title": title,
        "blocks_written": written,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
