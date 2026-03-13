#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import pathlib
import sys
import time
import urllib.error

from getnote_daily_sync import READONLY_NAMES, WORKSPACE, derive_tags, load_getnote_config, save_plain_note

IMPORT_STATE_PATH = WORKSPACE / 'memory' / 'getnote-bulk-import-state.json'
IMPORT_REPORT_DIR = WORKSPACE / 'reports' / 'getnote-bulk-import'
ALLOWED_DIR_PREFIXES = ('articles/', 'docs/', 'intel/', 'tmp/', 'memory/')
EXTRA_ALLOWED = {
    'article.md', 'findings.md', 'progress.md', 'task_plan.md', 'wechat_article.md', '河南省各地级市2026年重点工作部署汇总.md'
}
SKIP_MEMORY_PREFIXES = ('memory/2026-03-13.md',)


def relpath(p: pathlib.Path) -> str:
    return p.relative_to(WORKSPACE).as_posix()


def load_import_state():
    if IMPORT_STATE_PATH.exists():
        return json.loads(IMPORT_STATE_PATH.read_text())
    return {}


def save_import_state(state):
    IMPORT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMPORT_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')


def should_import(p: pathlib.Path) -> bool:
    rp = relpath(p)
    if p.name in READONLY_NAMES:
        return False
    if rp in EXTRA_ALLOWED:
        return True
    if rp.startswith(SKIP_MEMORY_PREFIXES):
        return False
    return rp.startswith(ALLOWED_DIR_PREFIXES)


def list_candidates():
    files = []
    for p in WORKSPACE.rglob('*.md'):
        if p.is_file() and should_import(p):
            files.append(p)
    return sorted(files)


def checksum(text: str) -> str:
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def title_for(path_str: str) -> str:
    return f'历史文档归档｜{path_str}'


def content_for(path_str: str, text: str) -> str:
    return '\n'.join([
        f'# 历史文档归档｜{path_str}',
        '',
        f'- 导入时间：{dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}',
        f'- 原始路径：`{path_str}`',
        '- 类型：服务器历史 Markdown 归档',
        '',
        text.strip(),
        ''
    ])


def build_tags(path_str: str, text: str):
    base_tags = ['历史归档', 'Markdown导入']
    for tag in derive_tags(path_str + '\n' + text):
        if tag not in base_tags:
            base_tags.append(tag)
    return base_tags[:4]


def main(argv):
    limit = int(argv[1]) if len(argv) > 1 else 3
    delay = float(argv[2]) if len(argv) > 2 else 70.0
    api_key, client_id = load_getnote_config()
    state = load_import_state()
    imported = state.get('imported', {})
    report = []
    count = 0

    IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for p in list_candidates():
        if count >= limit:
            break
        path_str = relpath(p)
        text = p.read_text(errors='ignore').strip()
        if not text:
            continue
        sha = checksum(text)
        if imported.get(path_str) == sha:
            continue
        title = title_for(path_str)
        content = content_for(path_str, text)
        tags = build_tags(path_str, text)
        try:
            raw = save_plain_note(api_key, client_id, title, content, tags)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='ignore')
            if exc.code == 429:
                print(f'rate-limited on {path_str}')
                state['imported'] = imported
                state['lastRunAt'] = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                state['lastError'] = f'429 on {path_str}: {detail}'
                save_import_state(state)
                return 3
            raise
        IMPORT_REPORT_DIR.joinpath(path_str.replace('/', '__') + '.json').write_text(raw + '\n')
        imported[path_str] = sha
        report.append(path_str)
        count += 1
        if count < limit:
            time.sleep(delay)

    state['imported'] = imported
    state['lastRunAt'] = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    if report:
        state['lastImported'] = report
    save_import_state(state)

    if not report:
        print('skip: no new markdown files to import')
        return 0

    print('ok: imported markdown files')
    for item in report:
        print(item)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
