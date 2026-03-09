#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

P_DEFAULT = 'margin:1.5em 8px;letter-spacing:0.08em;color:#3f3f3f;'
H1_STYLE = 'display:table;padding:0 1em;border-bottom:2px solid #0F4C81;margin:2em auto 1em;color:#3f3f3f;font-size:calc(16px * 1.2);font-weight:bold;text-align:center;margin-top:0 !important;'
SUBTITLE_P = 'margin:1.2em 8px;letter-spacing:0.08em;color:#3f3f3f;'
H2_STYLE = 'display:table;padding:0 0.2em;margin:4em auto 2em;color:#fff;background:#0F4C81;font-size:calc(16px * 1.2);font-weight:bold;text-align:center;'
BLOCKQUOTE_STYLE = 'font-style:normal;padding:1em;border-left:4px solid #0F4C81;border-radius:6px;color:#3f3f3f;background:#f7f7f7;margin:1.2em 0;'
HR_STYLE = 'border:none;border-top:1px solid #e5e5e5;margin:2em 0;'
UL_STYLE = 'list-style:circle;padding-left:1em;margin-left:0;color:#3f3f3f;'
LI_STYLE = 'display:block;margin:0.2em 8px;color:#3f3f3f;'
BODY_STYLE = 'padding:24px;background:#ffffff;max-width:860px;margin:0 auto;font-family:-apple-system-font,BlinkMacSystemFont,Helvetica Neue,PingFang SC,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;font-size:16px;line-height:1.8;text-align:left;color:#3f3f3f;'
SECTION_STYLE = 'font-family:-apple-system-font,BlinkMacSystemFont,Helvetica Neue,PingFang SC,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;font-size:16px;line-height:1.8;text-align:left;color:#3f3f3f;'


def strip_single_punctuation_lines(html: str) -> str:
    pattern = re.compile(r'<p[^>]*>\s*([。！？；，、,.!?;:：…]+)\s*</p>', re.I)
    return pattern.sub('', html)


def normalize_author(html: str, author: str) -> str:
    author_re = re.compile(r'<p[^>]*>\s*(?:<strong[^>]*>)?作者[:：]\s*([^<]+?)(?:</strong>)?\s*</p>', re.I)
    replacement = f'<p style="{SUBTITLE_P}"><strong style="color:#0F4C81;font-weight:bold;">作者：{author}</strong></p>'
    if author_re.search(html):
        return author_re.sub(replacement, html, count=1)
    h1_close = re.search(r'</h1>', html, re.I)
    if h1_close:
        idx = h1_close.end()
        return html[:idx] + replacement + html[idx:]
    return html


def inject_subtitle(html: str, subtitle: str) -> str:
    if not subtitle:
        return html
    if '副标题：' in html:
        return html
    p = f'<p style="{SUBTITLE_P}"><strong style="color:#0F4C81;font-weight:bold;">副标题：{subtitle}</strong></p>'
    h1_close = re.search(r'</h1>', html, re.I)
    if h1_close:
        idx = h1_close.end()
        return html[:idx] + p + html[idx:]
    return html


def restyle_core(html: str) -> str:
    html = re.sub(r'<h1[^>]*>', f'<h1 style="{H1_STYLE}">', html, count=1, flags=re.I)
    html = re.sub(r'<h2[^>]*>', f'<h2 style="{H2_STYLE}">', html, flags=re.I)
    html = re.sub(r'<blockquote[^>]*>', f'<blockquote style="{BLOCKQUOTE_STYLE}">', html, flags=re.I)
    html = re.sub(r'<p(?![^>]*style=)[^>]*>', f'<p style="{P_DEFAULT}">', html, flags=re.I)
    html = re.sub(r'<hr[^>]*>', f'<hr style="{HR_STYLE}" />', html, flags=re.I)
    html = re.sub(r'<ul[^>]*>', f'<ul style="{UL_STYLE}">', html, flags=re.I)
    html = re.sub(r'<li[^>]*>', f'<li style="{LI_STYLE}">', html, flags=re.I)
    html = re.sub(r'<strong>([^<]+)</strong>', r'<strong style="color:#0F4C81;font-weight:bold;">\1</strong>', html)
    html = re.sub(r'<p style="([^"]*)">\s*</p>', '', html)
    return html


def rebuild_document(content: str, title: str) -> str:
    return f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
</head>
<body style="{BODY_STYLE}">
<div id="output">
<section style="{SECTION_STYLE}">
{content}
</section>
</div>
</body>
</html>
'''


def extract_main_content(html: str) -> str:
    m = re.search(r'<div id="output">\s*(.*?)\s*</div>\s*</body>', html, re.I | re.S)
    if m:
        inner = m.group(1)
        sec = re.search(r'<section[^>]*>(.*)</section>', inner, re.I | re.S)
        return sec.group(1) if sec else inner
    body = re.search(r'<body[^>]*>(.*)</body>', html, re.I | re.S)
    return body.group(1) if body else html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_html')
    ap.add_argument('--output', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--author', default='余炜勋')
    ap.add_argument('--subtitle', default='')
    args = ap.parse_args()

    raw = Path(args.input_html).read_text(encoding='utf-8')
    content = extract_main_content(raw)
    content = strip_single_punctuation_lines(content)
    content = restyle_core(content)
    content = inject_subtitle(content, args.subtitle)
    content = normalize_author(content, args.author)
    content = strip_single_punctuation_lines(content)
    final_html = rebuild_document(content, args.title)
    Path(args.output).write_text(final_html, encoding='utf-8')


if __name__ == '__main__':
    main()
