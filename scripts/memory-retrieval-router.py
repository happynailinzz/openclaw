#!/usr/bin/env python3
"""
Memory Retrieval Router v2
三源检索：本地日志/MEMORY.md → qmd 知识库（obsidian+articles+memory）→ Memos 冷记忆
"""
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


def recent_memory_files(days=3):
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


def search_qmd(query: str, max_snippets=3, max_chars=600):
    """跨所有 qmd collection 检索（obsidian + articles + memory）"""
    try:
        p = subprocess.run(
            ["qmd", "search", query, "--limit", str(max_snippets)],
            capture_output=True, text=True, timeout=15
        )
        if p.returncode != 0 or not p.stdout.strip():
            return {"ok": False, "hits": [], "error": p.stderr.strip() or "no output"}

        hits = []
        current = {}
        for line in p.stdout.splitlines():
            line = line.rstrip()
            if line.startswith("qmd://"):
                if current:
                    hits.append(current)
                parts = line.split(" ", 2)
                current = {"source": parts[0], "score_raw": parts[1] if len(parts) > 1 else ""}
                current["snippet"] = ""
            elif line.startswith("Title:"):
                current["title"] = line[6:].strip()
            elif line.startswith("Score:"):
                current["score"] = line[6:].strip()
            elif line.startswith("Context:"):
                current["context"] = line[8:].strip()
            elif line.startswith("@@ ") or (current and "snippet" in current and line.strip()):
                if not line.startswith("@@"):
                    current["snippet"] = (current.get("snippet", "") + "\n" + line).strip()
                    if len(current["snippet"]) > max_chars:
                        current["snippet"] = current["snippet"][:max_chars]
        if current:
            hits.append(current)

        return {"ok": True, "hits": hits[:max_snippets]}
    except Exception as e:
        return {"ok": False, "hits": [], "error": str(e)}


def search_memos(query: str, user_id: str, conversation_id: str):
    cmd = [
        "python3",
        str(ROOT / "scripts" / "memos-client.py"),
        "search",
        query,
        user_id,
        conversation_id,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if p.returncode != 0:
        return {"ok": False, "error": p.stdout or p.stderr}
    try:
        data = json.loads(p.stdout)
        return {"ok": True, "data": data}
    except Exception:
        return {"ok": False, "error": p.stdout}


def compress_memos_hits(memos_result: dict, max_snippets=3, max_chars=500):
    if not memos_result.get("ok"):
        return {"ok": False, "error": memos_result.get("error", "memos search failed"), "hits": []}

    raw = memos_result.get("data", {})
    payload = (((raw.get("response") or {}).get("data") or {}))
    items = payload.get("memory_detail_list") or []

    ranked = []
    for m in items:
        relativity = float(m.get("relativity") or 0)
        confidence = float(m.get("confidence") or 0)
        score = relativity * 0.7 + confidence * 0.3
        ranked.append({
            "id": m.get("id"),
            "memory_type": m.get("memory_type"),
            "score": round(score, 4),
            "memory_key": (m.get("memory_key") or "")[:120],
            "memory_value": (m.get("memory_value") or "")[:max_chars],
            "tags": m.get("tags") or [],
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    hits = ranked[:max_snippets]
    return {"ok": True, "hits": hits, "meta": {"total": len(items), "returned": len(hits)}}


def main():
    if len(sys.argv) < 2:
        print("Usage: memory-retrieval-router.py <query> [user_id] [conversation_id]")
        sys.exit(1)

    query = sys.argv[1]
    cfg = load_cfg()
    r = cfg.get("retrieval", {})
    memos_cfg = cfg.get("memos", {})

    user_id = sys.argv[2] if len(sys.argv) > 2 else memos_cfg.get("defaultUserId", "dongcheng-laotao")
    conv_id = sys.argv[3] if len(sys.argv) > 3 else memos_cfg.get("defaultConversationId", "openclaw-main")

    max_local = int(r.get("maxLocalSnippets", 3))
    max_qmd = int(r.get("maxQmdSnippets", 3))
    max_memos = int(r.get("maxMemosSnippets", 3))
    max_chars = int(r.get("maxSnippetChars", 500))

    local_hits = collect_local_snippets(query, max_snippets=max_local, max_chars=max_chars)
    qmd_hits = search_qmd(query, max_snippets=max_qmd, max_chars=600)
    memos_result = search_memos(query, user_id, conv_id)
    memos_hits = compress_memos_hits(memos_result, max_snippets=max_memos, max_chars=max_chars)

    out = {
        "query": query,
        "route": ["local_memory", "qmd_knowledge", "memos"],
        "local_hits": local_hits,
        "qmd_hits": qmd_hits,
        "memos_hits": memos_hits,
        "token_saving_hint": {
            "local_snippets": len(local_hits),
            "qmd_snippets": len(qmd_hits.get("hits", [])),
            "memos_snippets": len(memos_hits.get("hits", [])),
            "note": "优先注入 local_hits + qmd_hits.hits 精简片段；memos 作为补充。",
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
