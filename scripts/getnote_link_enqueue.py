#!/usr/bin/env python3
import json
import re
import sys
from getnote_daily_sync import derive_tags, enqueue_link, load_getnote_config, save_link_note

URL_RE = re.compile(r'https?://\S+')


def main(argv):
    if len(argv) < 2:
        print('usage: getnote_link_enqueue.py <url-or-text> [note] [--now]')
        return 1
    immediate = '--now' in argv
    parts = [a for a in argv[1:] if a != '--now']
    text = ' '.join(parts).strip()
    m = URL_RE.search(text)
    if not m:
        print('error: no url found')
        return 2
    url = m.group(0).rstrip('.,);]')
    note = text.replace(m.group(0), '').strip()
    item = enqueue_link(url, source='cli', note=note)
    print(f'queued: {url}')
    if immediate:
        api_key, client_id = load_getnote_config()
        tags = sorted(set(['Get笔记导入', '链接收藏'] + derive_tags((note or '') + url)))
        raw = save_link_note(api_key, client_id, url, tags, title=note or url)
        parsed = json.loads(raw)
        print('saved-now')
        print(json.dumps(parsed, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
