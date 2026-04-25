#!/usr/bin/env python3
import datetime as dt
import subprocess
from pathlib import Path

LOG_PATH = Path('/root/.openclaw/workspace/reports/healthcheck/update-status.log')
OPENCLAW_TIMEOUT_SECONDS = 25


def summarize_block(block: str) -> str | None:
    install = None
    channel = None
    latest = None
    status = None

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('│') and line.endswith('│'):
            parts = [p.strip() for p in line.strip('│').split('│')]
            if len(parts) >= 2:
                key = parts[0]
                value = parts[1]
                if key == 'Install':
                    install = value
                elif key == 'Channel':
                    channel = value
                elif key == 'Update':
                    latest = value
                    if 'up to date' in value:
                        status = 'up to date'
                    elif 'available' in value:
                        status = 'update available'
        elif line.startswith('Update available (') and not latest:
            latest = line
            status = 'update available'

    if not any([install, channel, latest, status]):
        return None

    parts = []
    if install:
        parts.append(f'install={install}')
    if channel:
        parts.append(f'channel={channel}')
    if latest:
        parts.append(f'latest={latest}')
    if status:
        parts.append(f'status={status}')
    return 'Summary: ' + '; '.join(parts)


def collect_update_status() -> str:
    proc = subprocess.run(
        ['timeout', str(OPENCLAW_TIMEOUT_SECONDS), 'openclaw', 'update', 'status'],
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout or ''
    stderr = proc.stderr or ''
    if proc.returncode == 124:
        return f'OpenClaw update status\n\ntimeout after {OPENCLAW_TIMEOUT_SECONDS}s\nSummary: status=timeout\n'
    text = stdout.strip('\n')
    if not text and stderr.strip():
        text = stderr.strip('\n')
    if not text:
        text = f'command exited with code {proc.returncode}'
    summary = summarize_block(text)
    if summary:
        text = '\n'.join([line for line in text.splitlines() if not line.strip().lower().startswith('summary:')])
        return f'OpenClaw update status\n\n{text}\n{summary}\n'
    return f'OpenClaw update status\n\n{text}\n'


def append_log(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    entry = f'===== {stamp} =====\n' + collect_update_status() + '\n'
    with path.open('a', encoding='utf-8') as fh:
        fh.write(entry)


if __name__ == '__main__':
    append_log(LOG_PATH)
    print(LOG_PATH)
