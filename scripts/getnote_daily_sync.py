#!/usr/bin/env python3
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

WORKSPACE = pathlib.Path('/root/.openclaw/workspace')
OPENCLAW_CONFIG = pathlib.Path('/root/.openclaw/openclaw.json')
MEMORY_DIR = WORKSPACE / 'memory'
OUT_DIR = WORKSPACE / 'reports' / 'getnote-sync'
STATE_PATH = MEMORY_DIR / 'getnote-sync-state.json'
API_BASE = 'https://openapi.biji.com'


def load_getnote_config():
    data = json.loads(OPENCLAW_CONFIG.read_text())
    entries = data.get('skills', {}).get('entries', {})
    cfg = entries.get('getnote', {})
    api_key = cfg.get('apiKey') or os.environ.get('GETNOTE_API_KEY')
    client_id = (cfg.get('env') or {}).get('GETNOTE_CLIENT_ID') or os.environ.get('GETNOTE_CLIENT_ID')
    if not api_key or not client_id:
        raise RuntimeError('missing getnote api config')
    return api_key, client_id


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')


def read_text(path):
    if not path.exists():
        return ''
    return path.read_text(errors='ignore')


def extract_section(text, heading):
    pattern = re.compile(rf'(^##+\s+{re.escape(heading)}.*?)(?=^##+\s+|\Z)', re.M | re.S)
    m = pattern.search(text)
    return m.group(1).strip() if m else ''


def list_markdown_outputs(day):
    results = []
    for p in WORKSPACE.glob('*.md'):
        if p.name.startswith('MEMORY') or p.name in {'AGENTS.md', 'SOUL.md', 'TOOLS.md', 'USER.md', 'IDENTITY.md', 'HEARTBEAT.md', 'BOOTSTRAP.md'}:
            continue
        try:
            stat = p.stat()
        except FileNotFoundError:
            continue
        modified = dt.datetime.utcfromtimestamp(stat.st_mtime).date()
        if modified == day:
            results.append(p)
    return sorted(results)


def build_summary(target_day):
    day_str = target_day.isoformat()
    prev_memory = read_text(MEMORY_DIR / f'{day_str}.md')
    sections = []

    if prev_memory:
        for heading in [
            '河南省各地级市2026年重点工作收集任务完成',
            'OpenClaw / AI 行业观察类文章配图 prompt 工作流',
            'Get笔记纳入记忆系统（2026-03-13 00:15 UTC）',
        ]:
            sec = extract_section(prev_memory, heading)
            if sec:
                sections.append(sec)

    md_outputs = list_markdown_outputs(target_day)
    outputs_lines = []
    for p in md_outputs[:20]:
        outputs_lines.append(f'- `{p.name}`')
    outputs_block = ''
    if outputs_lines:
        outputs_block = '## 当日产出文件\n' + '\n'.join(outputs_lines)
        sections.append(outputs_block)

    if not sections:
        return ''

    header = [
        f'# {day_str} 研究成果与对话总结',
        '',
        f'- 汇总日期：{dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}',
        f'- 覆盖日期：{day_str}',
        '- 来源：workspace memory / 当日产出文档 / 对话沉淀',
        '',
        '## 摘要',
        '- 本笔记由 OpenClaw 每日自动汇总生成，用于同步前一天研究成果与关键对话结论。',
        '',
    ]
    return '\n\n'.join(['\n'.join(header).strip()] + sections).strip() + '\n'


def post_note(api_key, client_id, title, content, tags):
    payload = {
        'title': title,
        'content': content,
        'note_type': 'plain_text',
        'tags': tags,
        'parent_id': 0,
    }
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        API_BASE + '/open/api/v1/resource/note/save',
        data=body,
        headers={
            'Authorization': api_key,
            'X-Client-ID': client_id,
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8', errors='ignore')
    return raw


def main():
    now = dt.datetime.utcnow()
    target_day = now.date() - dt.timedelta(days=1)
    state = load_state()
    day_key = target_day.isoformat()
    if state.get('lastSyncedDay') == day_key:
        print(f'skip: already synced {day_key}')
        return 0

    content = build_summary(target_day)
    if not content.strip():
        print(f'skip: no content for {day_key}')
        return 0

    api_key, client_id = load_getnote_config()
    title = f'OpenClaw 每日研究总结｜{day_key}'
    tags = ['OpenClaw', '每日总结', '研究沉淀']
    raw = post_note(api_key, client_id, title, content, tags)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f'{day_key}.json').write_text(raw + '\n')

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'invalid getnote response: {exc}')

    if not parsed.get('success'):
        raise RuntimeError(f'getnote save failed: {raw}')

    state['lastSyncedDay'] = day_key
    state['lastNoteTitle'] = title
    state['lastSyncedAt'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    save_state(state)
    print(f'ok: synced {day_key} -> {title}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore')
        print(f'http error: {exc.code} {detail}', file=sys.stderr)
        raise
    except Exception as exc:
        print(f'error: {exc}', file=sys.stderr)
        raise
