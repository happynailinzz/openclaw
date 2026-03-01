#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
MEM_DIR = ROOT / "memory"
CFG_PATH = ROOT / "config" / "memory-integration.json"

def load_cfg():
    if not CFG_PATH.exists():
        return {}
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))

def tokenize(s: str):
    return [t.lower() for t in re.findall(r"[\w\u4e00-\u9fff]+", s)]

def score_local(query: str, text: str, recency_boost: float = 0.0):
    q = set(tokenize(query))
    t = tokenize(text[:3000])
    if not q or not t:
        return 0.0
    hit = sum(1 for x in t if x in q)
    return float(hit) + recency_boost

def recent_memory_files(days=2):
    now = datetime.utcnow().date()
    out = []
    for i in range(days):
        d = now - timedelta(days=i)
        p = MEM_DIR / f"{d.isoformat()}.md"
        if p.exists():
            out.append(p)
    return out

def collect_local_snippets(query: str, max_snippets=3, max_chars=500):
    files = recent_memory_files(3)
    mem_long = ROOT / "MEMORY.md"
    if mem_long.exists():
        files.append(mem_long)

    scored = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        parts = re.split(r"\n\n+", text)
        for p in parts:
            s = p.strip()
            if len(s) < 20:
                continue
            sc = score_local(query, s, recency_boost=0.2 if "/memory/" in str(f) else 0.0)
            if sc > 0:
                scored.append({"source": str(f), "score": sc, "snippet": s[:max_chars]})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:max_snippets]

def search_memos(query: str, user_id: str, conversation_id: str):
    cmd = [
        "python3",
        str(ROOT / "scripts" / "memos-client.py"),
        "search",
        query,
        user_id,
        conversation_id,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"ok": False, "error": p.stdout or p.stderr}
    try:
        data = json.loads(p.stdout)
        return {"ok": True, "data": data}
    except Exception:
        return {"ok": False, "error": p.stdout}

def main():
    if len(sys.argv) < 2:
        print("Usage: memory-retrieval-router.py <query> [user_id] [conversation_id]")
        sys.exit(1)

    query = sys.argv[1]
    cfg = load_cfg()
    r = cfg.get("retrieval", {})
    memos_cfg = cfg.get("memos", {})

    user_id = sys.argv[2] if len(sys.argv) > 2 else memos_cfg.get("defaultUserId", "openclaw-user")
    conv_id = sys.argv[3] if len(sys.argv) > 3 else memos_cfg.get("defaultConversationId", "openclaw-main")

    max_local = int(r.get("maxLocalSnippets", 3))
    max_chars = int(r.get("maxSnippetChars", 500))

    local_hits = collect_local_snippets(query, max_snippets=max_local, max_chars=max_chars)
    memos_result = search_memos(query, user_id, conv_id)

    out = {
        "query": query,
        "route": ["local_memory", "memos"],
        "local_hits": local_hits,
        "memos": memos_result,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
