#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.request


TAVILY_ENDPOINT = "https://api.tavily.com/search"
NOISE_PATTERNS = [
    r"^Navigation Menu$",
    r"^Skip to content$",
    r"^Sign in$",
    r"^Log in$",
    r"^Toggle navigation$",
    r"^Table of Contents$",
    r"^Back to top$",
    r"^Cookie",
    r"^Privacy Policy$",
    r"^Terms of Service$",
    r"^Advertis",
]


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
    for line in md.splitlines()[:80]:
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


def is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    for pat in NOISE_PATTERNS:
        if re.search(pat, s, flags=re.IGNORECASE):
            return True
    # nav-like bullet links
    if re.match(r"^\*\s+\[[^\]]+\]\(https?://", s):
        return True
    # very short chrome-y fragments
    if len(s) <= 2:
        return True
    return False


def clean_markdown(md: str) -> str:
    lines = md.splitlines()
    out = []
    blank = 0
    for ln in lines:
        if is_noise_line(ln):
            continue
        if not ln.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(ln)

    text = "\n".join(out).strip()
    # Drop boilerplate header blocks if present
    text = re.sub(r"^URL Source:.*?\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^Warning: This is a cached snapshot.*?\n", "", text, flags=re.MULTILINE)
    return text.strip()


def summarize_markdown(md: str, max_chars: int = 600) -> str:
    # Keep headline + first meaningful paragraphs
    chunks = [c.strip() for c in re.split(r"\n\s*\n", md) if c.strip()]
    keep = []
    for c in chunks:
        if is_noise_line(c):
            continue
        keep.append(c)
        if len("\n\n".join(keep)) >= max_chars:
            break
    s = "\n\n".join(keep)
    return s[:max_chars]


def main():
    p = argparse.ArgumentParser(description="Search with Tavily and fetch each result via Jina Reader")
    p.add_argument("query", help="Search query")
    p.add_argument("--top", type=int, default=3, help="How many Tavily results to fetch (default: 3)")
    p.add_argument("--max-chars", type=int, default=10000, help="Per-page markdown truncation")
    p.add_argument("--timeout", type=int, default=40, help="HTTP timeout seconds")
    p.add_argument("--clean", action="store_true", help="Denoise markdown (remove nav/footer/noise lines)")
    p.add_argument("--summary", action="store_true", help="Add concise summary_excerpt for each page")
    p.add_argument("--summary-chars", type=int, default=600, help="summary_excerpt max chars (default: 600)")
    args = p.parse_args()

    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        print("ERROR: TAVILY_API_KEY is missing", file=sys.stderr)
        sys.exit(2)

    try:
        results = tavily_search(api_key, args.query, max_results=max(1, args.top), timeout=args.timeout)
    except Exception as e:
        print(f"ERROR: tavily search failed: {e}", file=sys.stderr)
        sys.exit(3)

    out = {"query": args.query, "count": 0, "items": []}

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
            "summary_excerpt": None,
            "error": None,
        }

        try:
            md = fetch_markdown(reader_url, timeout=args.timeout)
            if args.clean:
                md = clean_markdown(md)
            if args.max_chars > 0:
                md = md[: args.max_chars]
            t, a, pub = parse_meta(md)
            item["title"] = t
            item["author"] = a
            item["published"] = pub
            item["content_markdown"] = md
            if args.summary:
                item["summary_excerpt"] = summarize_markdown(md, max_chars=max(120, args.summary_chars))
        except Exception as e:
            item["error"] = str(e)

        out["items"].append(item)

    out["count"] = len(out["items"])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
