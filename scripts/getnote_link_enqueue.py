#!/usr/bin/env python3
import re
import sys
from getnote_daily_sync import enqueue_link

URL_RE = re.compile(r'https?://\S+')


def main(argv):
    if len(argv) < 2:
        print('usage: getnote_link_enqueue.py <url-or-text> [note]')
        return 1
    text = ' '.join(argv[1:]).strip()
    m = URL_RE.search(text)
    if not m:
        print('error: no url found')
        return 2
    url = m.group(0).rstrip('.,);]')
    note = text.replace(m.group(0), '').strip()
    enqueue_link(url, source='cli', note=note)
    print(f'queued: {url}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
