#!/usr/bin/env python3
import re
from pathlib import Path

LOG_PATH = Path('/root/.openclaw/workspace/reports/healthcheck/update-status.log')


def summarize_block(block: str) -> str | None:
    install = None
    channel = None
    latest = None
    status = None

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = re.match(r'^│\s*(Install|Channel|Update)\s*│\s*(.*?)\s*│$', line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
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


def rewrite_log(path: Path) -> int:
    text = path.read_text(errors='ignore')
    segments = re.split(r'(OpenClaw update status\n)', text)
    if len(segments) < 3:
        return 0

    rebuilt = [segments[0]]
    changed = 0

    for idx in range(1, len(segments), 2):
        marker = segments[idx]
        block = segments[idx + 1] if idx + 1 < len(segments) else ''
        lines = block.splitlines()
        filtered_lines = [line for line in lines if not re.match(r'^(Summary:|summary:)', line.strip())]
        new_summary = summarize_block('\n'.join(filtered_lines))
        if new_summary:
            filtered_lines.append(new_summary)
        new_block = '\n'.join(filtered_lines)
        if block.endswith('\n'):
            new_block += '\n'
        if new_block != block:
            changed += 1
        rebuilt.extend([marker, new_block])

    if changed:
        path.write_text(''.join(rebuilt))
    return changed


if __name__ == '__main__':
    changed = rewrite_log(LOG_PATH)
    print(f'updated_blocks={changed}')
