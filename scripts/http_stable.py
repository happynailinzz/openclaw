#!/usr/bin/env python3
"""Small, dependency-free HTTP helper with retry/backoff.

Goals:
- Standard library only (urllib)
- Deterministic failure with trace
- Safe defaults for GET/POST JSON
"""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class HttpTrace:
    attempts: int
    sleep_s: float
    last_error: str
    last_status: Optional[int] = None


def _is_retryable_http(status: int) -> bool:
    # 408: request timeout; 429: rate limit; 5xx: transient server errors
    return status in (408, 429) or 500 <= status <= 599


def _sleep(backoff_s: float, jitter_s: float) -> float:
    j = random.random() * jitter_s
    t = backoff_s + j
    time.sleep(t)
    return t


def request_text(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: int = 30,
    retries: int = 3,
    backoff_base_s: float = 0.6,
    backoff_max_s: float = 8.0,
    jitter_s: float = 0.25,
) -> Tuple[str, HttpTrace]:
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=dict(headers or {}))

    attempts = 0
    slept = 0.0
    last_err = ""
    last_status: Optional[int] = None

    for i in range(retries + 1):
        attempts = i + 1
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "ignore")
                return raw, HttpTrace(attempts=attempts, sleep_s=slept, last_error="", last_status=resp.status)
        except urllib.error.HTTPError as e:
            last_status = getattr(e, "code", None)
            try:
                body = e.read().decode("utf-8", "ignore")
            except Exception:
                body = ""
            last_err = f"HTTP {last_status}: {body[:200]}".strip()
            if last_status is not None and _is_retryable_http(int(last_status)) and i < retries:
                backoff = min(backoff_max_s, backoff_base_s * (2**i))
                slept += _sleep(backoff, jitter_s)
                continue
            break
        except Exception as e:
            last_err = str(e)
            if i < retries:
                backoff = min(backoff_max_s, backoff_base_s * (2**i))
                slept += _sleep(backoff, jitter_s)
                continue
            break

    raise RuntimeError(json.dumps({
        "ok": False,
        "url": url,
        "trace": {
            "attempts": attempts,
            "sleep_s": round(slept, 3),
            "last_status": last_status,
            "last_error": last_err,
        },
    }, ensure_ascii=False))


def request_json(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 3,
    backoff_base_s: float = 0.6,
    backoff_max_s: float = 8.0,
    jitter_s: float = 0.25,
) -> Tuple[Dict[str, Any], HttpTrace]:
    hdrs = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=hdrs)

    attempts = 0
    slept = 0.0
    last_err = ""
    last_status: Optional[int] = None

    for i in range(retries + 1):
        attempts = i + 1
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "ignore")
                # json.load() on HTTPResponse can fail when body is empty; be defensive
                out = json.loads(raw) if raw.strip() else {}
                return out, HttpTrace(attempts=attempts, sleep_s=slept, last_error="", last_status=resp.status)
        except urllib.error.HTTPError as e:
            last_status = getattr(e, "code", None)
            try:
                body = e.read().decode("utf-8", "ignore")
            except Exception:
                body = ""
            last_err = f"HTTP {last_status}: {body[:200]}".strip()
            if last_status is not None and _is_retryable_http(int(last_status)) and i < retries:
                backoff = min(backoff_max_s, backoff_base_s * (2**i))
                slept += _sleep(backoff, jitter_s)
                continue
            break
        except Exception as e:
            last_err = str(e)
            if i < retries:
                backoff = min(backoff_max_s, backoff_base_s * (2**i))
                slept += _sleep(backoff, jitter_s)
                continue
            break

    raise RuntimeError(json.dumps({
        "ok": False,
        "url": url,
        "trace": {
            "attempts": attempts,
            "sleep_s": round(slept, 3),
            "last_status": last_status,
            "last_error": last_err,
        },
    }, ensure_ascii=False))
