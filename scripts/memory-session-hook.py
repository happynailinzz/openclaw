#!/usr/bin/env python3
"""
Memory session hook for OpenClaw workflow.

Usage:
  python3 scripts/memory-session-hook.py pre "<query>" [user_id] [conversation_id]
  python3 scripts/memory-session-hook.py post "<final_summary>" [user_id] [conversation_id]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "scripts" / "memory-retrieval-router.py"
MEMOS = ROOT / "scripts" / "memos-client.py"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def pre(query, user_id, conv_id):
    code, out, err = run(["python3", str(ROUTER), query, user_id, conv_id])
    if code != 0:
        print(json.dumps({"ok": False, "stage": "pre", "error": out or err}, ensure_ascii=False))
        return 1
    print(out)
    return 0


def post(summary, user_id, conv_id):
    text = f"任务结论摘要：{summary}"
    code, out, err = run(["python3", str(MEMOS), "add", text, user_id, conv_id])
    if code != 0:
        print(json.dumps({"ok": False, "stage": "post", "error": out or err}, ensure_ascii=False))
        return 1
    print(out)
    return 0


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in {"pre", "post"}:
        print("Usage:\n  memory-session-hook.py pre <query> [user_id] [conversation_id]\n  memory-session-hook.py post <summary> [user_id] [conversation_id]")
        sys.exit(1)

    stage = sys.argv[1]
    text = sys.argv[2]
    user_id = sys.argv[3] if len(sys.argv) > 3 else "dongcheng-laotao"
    conv_id = sys.argv[4] if len(sys.argv) > 4 else "openclaw-main"

    if stage == "pre":
        sys.exit(pre(text, user_id, conv_id))
    else:
        sys.exit(post(text, user_id, conv_id))


if __name__ == "__main__":
    main()
