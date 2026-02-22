---
name: jina-reader
description: Fetch and normalize web pages through Jina AI Reader (https://r.jina.ai/) to get clean markdown content, including difficult pages (dynamic sites, some paywalled content, X/Twitter links, and article pages with better extraction). Use when user asks to open links and read webpage content after search, or explicitly requests jina.ai Reader-style extraction.
metadata: { "openclaw": { "emoji": "🦐", "requires": { "bins": ["python3"], "env": ["TAVILY_API_KEY"] }, "primaryEnv": "TAVILY_API_KEY" } }
---

# Jina Reader

Use Jina Reader as a first-class fallback/alternative for webpage extraction.

## What it does

- Prefixes target URL with `https://r.jina.ai/`
- Returns AI-friendly markdown text
- Works well for many hard-to-read pages (including some login/paywall and X links)

## Usage

### A) Single-link fetch

```bash
python3 skills/jina-reader/scripts/fetch.py "https://example.com/article"
```

Optional flags:

```bash
python3 skills/jina-reader/scripts/fetch.py "https://example.com/article" --max-chars 12000
python3 skills/jina-reader/scripts/fetch.py "https://x.com/..." --timeout 40
python3 skills/jina-reader/scripts/fetch.py "https://example.com" --json
```

### B) Search + fetch (integrated)

Search with Tavily first, then open top results through Jina Reader and return structured JSON.

```bash
python3 skills/jina-reader/scripts/search_fetch.py "OpenClaw 2026" --top 3 --max-chars 8000
python3 skills/jina-reader/scripts/search_fetch.py "OpenClaw 2026" --top 3 --clean --summary --summary-chars 500
```

## Output behavior

- Default: prints markdown body directly
- `--json`: prints structured JSON with:
  - `source_url`
  - `reader_url`
  - `title`
  - `author`
  - `published`
  - `content_markdown`

## Notes

- No API key required
- If a page still fails, retry once with longer timeout
- Keep outputs concise with `--max-chars` for long pages
