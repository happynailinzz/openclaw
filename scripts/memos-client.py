#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error

from http_stable import request_json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "config" / "memos.env"
CFG_PATH = ROOT / "config" / "memory-integration.json"

def load_env(path: Path):
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip()
    return env

def load_cfg(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def req_json(url: str, token: str, payload: dict):
    out, _trace = request_json(
        "POST",
        url,
        headers={
            "Authorization": f"Token {token}",
        },
        payload=payload,
        timeout=30,
        retries=3,
        backoff_base_s=0.8,
        backoff_max_s=8.0,
        jitter_s=0.3,
    )
    return out

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"add", "search"}:
        print("Usage:\n  memos-client.py add <text> [user_id] [conversation_id]\n  memos-client.py search <query> [user_id] [conversation_id]")
        sys.exit(1)

    env = load_env(ENV_PATH)
    cfg = load_cfg(CFG_PATH)
    memos_cfg = (cfg.get("memos") or {})

    base_url = (env.get("MEMOS_BASE_URL") or "").rstrip("/")
    api_key = env.get("MEMOS_API_KEY") or ""
    base_id = env.get("MEMOS_BASE_ID") or memos_cfg.get("baseId")
    if not base_url or not api_key:
        print(json.dumps({"ok": False, "error": "Missing MEMOS_BASE_URL or MEMOS_API_KEY"}, ensure_ascii=False))
        sys.exit(2)

    cmd = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else ""
    user_id = sys.argv[3] if len(sys.argv) > 3 else memos_cfg.get("defaultUserId", "openclaw-user")
    conv_id = sys.argv[4] if len(sys.argv) > 4 else memos_cfg.get("defaultConversationId", "openclaw-main")

    try:
        if cmd == "add":
            payload = {
                "user_id": user_id,
                "conversation_id": conv_id,
                "messages": [{"role": "user", "content": text}],
            }
            if base_id:
                payload["base_id"] = base_id
            out = req_json(f"{base_url}/add/message", api_key, payload)
            print(json.dumps({"ok": True, "action": "add", "response": out}, ensure_ascii=False))
        else:
            payload = {
                "user_id": user_id,
                "conversation_id": conv_id,
                "query": text,
            }
            if base_id:
                payload["base_id"] = base_id
            out = req_json(f"{base_url}/search/memory", api_key, payload)
            print(json.dumps({"ok": True, "action": "search", "response": out}, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print(json.dumps({"ok": False, "error": f"HTTP {e.code}", "body": body}, ensure_ascii=False))
        sys.exit(3)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(4)

if __name__ == "__main__":
    main()
