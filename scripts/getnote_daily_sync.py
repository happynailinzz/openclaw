#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

WORKSPACE = pathlib.Path('/root/.openclaw/workspace')
OPENCLAW_CONFIG = pathlib.Path('/root/.openclaw/openclaw.json')
MEMORY_DIR = WORKSPACE / 'memory'
OUT_DIR = WORKSPACE / 'reports' / 'getnote-sync'
STATE_PATH = MEMORY_DIR / 'getnote-sync-state.json'
LINK_INBOX = MEMORY_DIR / 'getnote-link-inbox.jsonl'
API_BASE = 'https://openapi.biji.com'
READONLY_NAMES = {
    'AGENTS.md', 'SOUL.md', 'TOOLS.md', 'USER.md', 'IDENTITY.md', 'HEARTBEAT.md', 'BOOTSTRAP.md', 'MEMORY.md'
}
TOPIC_RULES = [
    ('河南', ['河南', '郑州', '洛阳', '南阳', '安阳', '信阳', '开封', '许昌', '漯河', '鹤壁', '商丘', '周口', '驻马店', '济源', '三门峡', '焦作', '濮阳', '平顶山', '新乡']),
    ('政企数字化', ['政企', '信创', '数字化', '数据治理', '政府工作报告']),
    ('AI观察', ['OpenClaw', 'AI', 'Agent', '模型', '算力', '行业观察']),
    ('配图Prompt', ['封面', '内页图', 'prompt', '提示词', '配图']),
    ('选题库', ['选题', '文章', '公众号']),
]


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


def slugify(name):
    clean = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+', '-', name).strip('-')
    return clean or 'untitled'


def derive_tags(text):
    tags = ['OpenClaw']
    for tag, needles in TOPIC_RULES:
        if any(n in text for n in needles) and tag not in tags:
            tags.append(tag)
    return tags[:4]


def list_markdown_outputs(day):
    results = []
    for p in WORKSPACE.glob('*.md'):
        if p.name in READONLY_NAMES:
            continue
        try:
            stat = p.stat()
        except FileNotFoundError:
            continue
        modified = dt.datetime.utcfromtimestamp(stat.st_mtime).date()
        if modified == day:
            results.append(p)
    return sorted(results)


def split_memory_sections(prev_memory):
    sections = []
    for heading in [
        '河南省各地级市2026年重点工作收集任务完成',
        'OpenClaw / AI 行业观察类文章配图 prompt 工作流',
        'Get笔记纳入记忆系统（2026-03-13 00:15 UTC）',
    ]:
        sec = extract_section(prev_memory, heading)
        if sec:
            sections.append((heading, sec))
    return sections


def build_note_content(target_day, title, body, extra_lines=None):
    lines = [
        f'# {title}',
        '',
        f'- 汇总日期：{dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}',
        f'- 覆盖日期：{target_day.isoformat()}',
    ]
    if extra_lines:
        lines.extend(extra_lines)
    lines.extend(['', body.strip(), ''])
    return '\n'.join(lines)


def build_topic_notes(target_day):
    day_str = target_day.isoformat()
    prev_memory = read_text(MEMORY_DIR / f'{day_str}.md')
    notes = []
    for heading, sec in split_memory_sections(prev_memory):
        title = f'OpenClaw 主题总结｜{day_str}｜{heading}'
        content = build_note_content(target_day, title, sec, ['- 类型：主题拆分'])
        tags = derive_tags(title + '\n' + sec)
        notes.append({'kind': 'plain_text', 'title': title, 'content': content, 'tags': tags})

    md_outputs = list_markdown_outputs(target_day)
    if md_outputs:
        outputs_lines = [f'- `{p.name}`' for p in md_outputs[:20]]
        body = '## 当日产出文件\n' + '\n'.join(outputs_lines)
        title = f'OpenClaw 产出清单｜{day_str}'
        content = build_note_content(target_day, title, body, ['- 类型：产出索引'])
        tags = derive_tags(title + '\n' + body)
        notes.append({'kind': 'plain_text', 'title': title, 'content': content, 'tags': tags})

    return notes


def normalize_url(url):
    return url.strip()


def enqueue_link(url, source='manual', note=''):
    LINK_INBOX.parent.mkdir(parents=True, exist_ok=True)
    item = {
        'url': normalize_url(url),
        'source': source,
        'note': note,
        'createdAt': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'id': hashlib.sha1(normalize_url(url).encode('utf-8')).hexdigest()[:16],
    }
    with LINK_INBOX.open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
    return item


def load_link_items(target_day, state):
    if not LINK_INBOX.exists():
        return []
    synced_ids = set(state.get('syncedLinkIds', []))
    items = []
    for line in LINK_INBOX.read_text(errors='ignore').splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        created = item.get('createdAt', '')[:10]
        if created != target_day.isoformat():
            continue
        if item.get('id') in synced_ids:
            continue
        items.append(item)
    return items


def post_json(api_key, client_id, path, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        API_BASE + path,
        data=body,
        headers={
            'Authorization': api_key,
            'X-Client-ID': client_id,
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def poll_task(api_key, client_id, task_id):
    for _ in range(8):
        raw = post_json(api_key, client_id, '/open/api/v1/resource/note/task/progress', {'task_id': task_id})
        parsed = json.loads(raw)
        if not parsed.get('success'):
            raise RuntimeError(f'task poll failed: {raw}')
        status = ((parsed.get('data') or {}).get('status'))
        if status == 'success':
            return raw
        if status == 'failed':
            raise RuntimeError(f'task failed: {raw}')
    raise RuntimeError(f'task timeout: {task_id}')


def save_plain_note(api_key, client_id, title, content, tags):
    raw = post_json(api_key, client_id, '/open/api/v1/resource/note/save', {
        'title': title,
        'content': content,
        'note_type': 'plain_text',
        'tags': tags,
        'parent_id': 0,
    })
    parsed = json.loads(raw)
    if not parsed.get('success'):
        raise RuntimeError(f'getnote save failed: {raw}')
    return raw


def save_link_note(api_key, client_id, url, tags, title=None):
    raw = post_json(api_key, client_id, '/open/api/v1/resource/note/save', {
        'title': title or url,
        'note_type': 'link',
        'link_url': url,
        'tags': tags,
        'parent_id': 0,
    })
    parsed = json.loads(raw)
    if not parsed.get('success'):
        raise RuntimeError(f'getnote link save failed: {raw}')
    task_id = ((parsed.get('data') or {}).get('task_id'))
    if task_id:
        return poll_task(api_key, client_id, task_id)
    return raw


def sync_day(target_day):
    api_key, client_id = load_getnote_config()
    state = load_state()
    day_key = target_day.isoformat()
    day_state = (state.get('days') or {}).get(day_key, {})
    synced_titles = set(day_state.get('syncedTitles', []))
    synced_link_ids = set(state.get('syncedLinkIds', []))

    notes = build_topic_notes(target_day)
    link_items = load_link_items(target_day, state)
    results = []

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for note in notes:
        if note['title'] in synced_titles:
            continue
        raw = save_plain_note(api_key, client_id, note['title'], note['content'], note['tags'])
        safe = slugify(note['title'])
        (OUT_DIR / f'{day_key}-{safe}.json').write_text(raw + '\n')
        synced_titles.add(note['title'])
        results.append(f"note:{note['title']}")

    for item in link_items:
        tags = sorted(set(['Get笔记导入', '链接收藏'] + derive_tags((item.get('note') or '') + item['url'])))
        raw = save_link_note(api_key, client_id, item['url'], tags, title=item['note'] or item['url'])
        (OUT_DIR / f"{day_key}-link-{item['id']}.json").write_text(raw + '\n')
        synced_link_ids.add(item['id'])
        results.append(f"link:{item['url']}")

    state.setdefault('days', {})[day_key] = {
        'syncedTitles': sorted(synced_titles),
        'lastSyncedAt': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    state['lastSyncedDay'] = day_key
    if notes:
        state['lastNoteTitle'] = notes[-1]['title']
    state['lastSyncedAt'] = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    state['syncedLinkIds'] = sorted(synced_link_ids)
    save_state(state)
    return results


def main(argv):
    if len(argv) >= 3 and argv[1] == 'enqueue-link':
        item = enqueue_link(argv[2], source='cli', note=' '.join(argv[3:]).strip())
        print(f"queued: {item['url']}")
        return 0

    now = dt.datetime.utcnow()
    target_day = now.date() - dt.timedelta(days=1)
    results = sync_day(target_day)
    if not results:
        print(f'skip: no new items for {target_day.isoformat()}')
        return 0
    print('ok: synced')
    for r in results:
        print(r)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore')
        print(f'http error: {exc.code} {detail}', file=sys.stderr)
        raise
    except Exception as exc:
        print(f'error: {exc}', file=sys.stderr)
        raise
