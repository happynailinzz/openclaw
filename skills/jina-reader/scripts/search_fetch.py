#!/usr/bin/env python3
import argparse
import json
import re
import sys
import urllib.request


TAVILY_ENDPOINT = "https://api.tavily.com/search"


def tavily_search(api_key: str, query: str, max_results: int, timeout: int):
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }

    req = urllib.request.Request(
        TAVILY_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))

    return data.get("results", [])


def build_reader_url(src: str) -> str:
    src = src.strip()
    if not src.startswith(("http://", "https://")):
        src = "https://" + src
    return "https://r.jina.ai/" + src


def fetch_markdown(url: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (OpenClaw jina-reader search-fetch)",
            "Accept": "text/plain,text/markdown,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_meta(md: str):
    title = author = published = None
    for line in md.splitlines()[:50]:
        s = line.strip()
        if s.startswith("Title:"):
            title = s.split(":", 1)[1].strip() or None
        elif s.startswith("Author:"):
            author = s.split(":", 1)[1].strip() or None
        elif s.startswith("Published Time:"):
            published = s.split(":", 1)[1].strip() or None
    if not title:
        m = re.search(r"^#\s+(.+)$", md, flags=re.MULTILINE)
        if m:
            title = m.group(1).strip()
    return title, author, published


def main():
    p = argparse.ArgumentParser(description="Search with Tavily and fetch each result via Jina Reader")
    p.add_argument("query", help="Search query")
    p.add_argument("--top", type=int, default=3, help="How many Tavily results to fetch (default: 3)")
    p.add_argument("--max-chars", type=int, default=10000, help="Per-page markdown truncation")
    p.add_argument("--timeout", type=int, default=40, help="HTTP timeout seconds")
    args = p.parse_args()

    api_key = None
    # Read from env manually to keep deps minimal
    import os

    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        print("ERROR: TAVILY_API_KEY is missing", file=sys.stderr)
        sys.exit(2)

    try:
        results = tavily_search(api_key, args.query, max_results=max(1, args.top), timeout=args.timeout)
    except Exception as e:
        print(f"ERROR: tavily search failed: {e}", file=sys.stderr)
        sys.exit(3)

    out = {
        "query": args.query,
        "count": 0,
        "items": [],
    }

    for r in results[: args.top]:
        src_url = (r.get("url") or "").strip()
        if not src_url:
            continue

        reader_url = build_reader_url(src_url)
        item = {
            "source_url": src_url,
            "reader_url": reader_url,
            "search_title": r.get("title"),
            "search_score": r.get("score"),
            "title": None,
            "author": None,
            "published": None,
            "content_markdown": None,
            "error": None,
        }

        try:
            md = fetch_markdown(reader_url, timeout=args.timeout)
            if args.max_chars > 0:
                md = md[: args.max_chars]
            t, a, pub = parse_meta(md)
            item["title"] = t
            item["author"] = a
            item["published"] = pub
            item["content_markdown"] = md
        except Exception as e:
            item["error"] = str(e)

        out["items"].append(item)

    out["count"] = len(out["items"])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
