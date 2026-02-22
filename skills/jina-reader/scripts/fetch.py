#!/usr/bin/env python3
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request


def build_reader_url(src: str) -> str:
    src = src.strip()
    if not src.startswith(("http://", "https://")):
        src = "https://" + src
    return "https://r.jina.ai/" + src


def parse_meta(md: str):
    title = None
    author = None
    published = None

    # Common markdown header style from extractors
    for line in md.splitlines()[:40]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("Title:"):
            title = s.split(":", 1)[1].strip() or None
        elif s.startswith("Author:"):
            author = s.split(":", 1)[1].strip() or None
        elif s.startswith("Published Time:"):
            published = s.split(":", 1)[1].strip() or None

    # Fallback: first H1
    if not title:
        m = re.search(r"^#\s+(.+)$", md, flags=re.MULTILINE)
        if m:
            title = m.group(1).strip()

    return title, author, published


def fetch(url: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (OpenClaw jina-reader skill)",
            "Accept": "text/plain,text/markdown,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main():
    p = argparse.ArgumentParser(description="Fetch web content via Jina Reader")
    p.add_argument("url", help="Original web URL")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds")
    p.add_argument("--max-chars", type=int, default=0, help="Truncate output chars (0 = no limit)")
    p.add_argument("--json", action="store_true", help="Return structured JSON")
    args = p.parse_args()

    src_url = args.url.strip()
    reader_url = build_reader_url(src_url)

    try:
        md = fetch(reader_url, args.timeout)
    except Exception as e:
        print(f"ERROR: failed to fetch via jina reader: {e}", file=sys.stderr)
        sys.exit(2)

    if args.max_chars and args.max_chars > 0:
        md = md[: args.max_chars]

    if args.json:
        title, author, published = parse_meta(md)
        payload = {
            "source_url": src_url,
            "reader_url": reader_url,
            "title": title,
            "author": author,
            "published": published,
            "content_markdown": md,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(md)


if __name__ == "__main__":
    main()
