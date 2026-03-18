#!/usr/bin/env bun
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const DEFAULT_AUTHOR = '余炜勋';
const WECHAT_API = path.join(process.env.HOME || '/root', '.agents/skills/baoyu-post-to-wechat/scripts/wechat-api.ts');

type Options = {
  input: string;
  template: string;
  output?: string;
  tag?: string;
  author?: string;
  cover?: string;
  publish?: boolean;
};

type Meta = {
  title: string;
  author: string;
  sourceLines: string[];
  bodyLines: string[];
};

function parseArgs(argv: string[]): Options {
  if (argv.length === 0) {
    throw new Error('Usage: bun publish.ts <markdown-file> [--template mint-tech] [--output file.html] [--tag text] [--author name] [--cover cover.png] [--publish]');
  }
  const opts: Options = { input: argv[0], template: 'mint-tech' };
  for (let i = 1; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--template' && argv[i + 1]) opts.template = argv[++i];
    else if (arg === '--output' && argv[i + 1]) opts.output = argv[++i];
    else if (arg === '--tag' && argv[i + 1]) opts.tag = argv[++i];
    else if (arg === '--author' && argv[i + 1]) opts.author = argv[++i];
    else if (arg === '--cover' && argv[i + 1]) opts.cover = argv[++i];
    else if (arg === '--publish') opts.publish = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return opts;
}

function escapeHtml(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderInline(input: string): string {
  let s = escapeHtml(input.trim());
  s = s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_m, alt, src) => `<img src="${escapeHtml(src)}" alt="${escapeHtml(alt)}" />`);
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_m, text, href) => `<a href="${escapeHtml(href)}">${escapeHtml(text)}</a>`);
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/==(.*?)==/g, '<span class="text-underline">$1</span>');
  return s;
}

function parseMarkdown(content: string, overrideAuthor?: string): Meta {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  let idx = 0;
  while (idx < lines.length && !lines[idx].trim()) idx++;
  const titleMatch = lines[idx]?.match(/^#\s+(.+)$/);
  if (!titleMatch) throw new Error('Missing title: first non-empty line must be # Title');
  const title = titleMatch[1].trim();
  idx++;

  const sourceLines: string[] = [];
  let author = overrideAuthor || DEFAULT_AUTHOR;

  while (idx < lines.length) {
    const line = lines[idx].trim();
    if (!line) {
      idx++;
      continue;
    }
    if (line.startsWith('>')) {
      const text = line.replace(/^>\s?/, '').trim();
      if (text.startsWith('作者：')) author = text.replace(/^作者：/, '').trim() || author;
      else sourceLines.push(text);
      idx++;
      continue;
    }
    if (line === '---') {
      idx++;
      continue;
    }
    break;
  }

  return { title, author, sourceLines, bodyLines: lines.slice(idx) };
}

function consumeParagraph(lines: string[], start: number): { html: string; next: number } {
  const buf: string[] = [];
  let i = start;
  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trim();
    if (!line) break;
    if (/^(#{1,3}\s+|>\s?|[-*]\s+|!\[[^\]]*\]\(|---$)/.test(line)) break;
    buf.push(line);
    i++;
  }
  return { html: `<p>${renderInline(buf.join(' '))}</p>`, next: i };
}

function renderBody(lines: string[]): string {
  const parts: string[] = [];
  let i = 0;
  let sectionNo = 0;
  let introDone = false;
  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trim();
    if (!line || line === '---') {
      i++;
      continue;
    }

    const h2 = line.match(/^##\s+(.+)$/);
    if (h2) {
      sectionNo += 1;
      parts.push(`<div class="section-header"><span class="section-num">${String(sectionNo).padStart(2, '0')}</span><span class="section-title">${renderInline(h2[1])}</span></div>`);
      i++;
      continue;
    }

    const h3 = line.match(/^###\s+(.+)$/);
    if (h3) {
      parts.push(`<div class="sub-title">${renderInline(h3[1])}</div>`);
      i++;
      continue;
    }

    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) {
      parts.push(`<div class="image-wrap"><img src="${escapeHtml(img[2])}" alt="${escapeHtml(img[1])}" /></div>`);
      i++;
      continue;
    }

    if (line.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      parts.push(`<div class="quote-text">${quoteLines.map(renderInline).join('<br>')}</div>`);
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(`<li>${renderInline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
        i++;
      }
      parts.push(`<ul>${items.join('')}</ul>`);
      continue;
    }

    const para = consumeParagraph(lines, i);
    const html = para.html;
    const plainLen = line.length;
    if (!introDone) {
      parts.push(`<div class="lead">${html}</div>`);
      introDone = true;
    } else if ((html.includes('<strong>') && plainLen < 120) || html.includes('text-underline')) {
      parts.push(`<div class="highlight-box">${html}</div>`);
    } else {
      parts.push(html);
    }
    i = para.next;
  }
  return parts.join('\n');
}

function renderMintTech(meta: Meta, opts: Options): string {
  const sourceHtml = meta.sourceLines.length
    ? `<div class="meta-source">${meta.sourceLines.map(renderInline).join('<br>')}</div>`
    : '';
  const tag = opts.tag ? `<div class="top-tag">${renderInline(opts.tag)}</div>` : '';
  const body = renderBody(meta.bodyLines);

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(meta.title)}</title>
  <style>
    :root {
      --theme-color: #14b8a6;
      --bg-light: #f0fdfa;
      --text-main: #374151;
      --text-dark: #111827;
      --accent-yellow: #fde68a;
      --border-gray: #e5e7eb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 20px;
      background: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
      color: var(--text-main);
      line-height: 1.75;
      display: flex;
      justify-content: center;
    }
    .art-container { max-width: 640px; width: 100%; }
    .top-tag {
      color: var(--theme-color);
      text-align: center;
      font-weight: 800;
      letter-spacing: .04em;
      border: 1px dashed var(--theme-color);
      padding: 10px 14px;
      border-radius: 10px;
      margin-bottom: 30px;
      background: linear-gradient(180deg, #f7fffd 0%, var(--bg-light) 100%);
      font-size: 14px;
      box-shadow: inset 0 0 0 1px rgba(20,184,166,.06);
    }
    .title {
      font-size: 32px;
      font-weight: 900;
      color: var(--text-dark);
      line-height: 1.32;
      margin: 0 0 12px;
      text-align: left;
      letter-spacing: -.02em;
    }
    .meta-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      color: #6b7280;
      font-size: 13px;
      margin-bottom: 28px;
      padding-bottom: 14px;
      border-bottom: 1px solid #eef2f7;
    }
    .meta-author { color: var(--theme-color); font-weight: 700; }
    .meta-source { text-align: right; max-width: 52%; }
    .lead {
      background: linear-gradient(180deg, #fbfffe 0%, #f6fffd 100%);
      border: 1px solid #d8f4ef;
      border-radius: 14px;
      padding: 18px 20px;
      margin: 0 0 24px;
    }
    .lead p:last-child { margin-bottom: 0; }
    p { margin: 0 0 1.05em; font-size: 16px; }
    .section-header {
      display: flex;
      align-items: baseline;
      margin-top: 50px;
      margin-bottom: 20px;
      position: relative;
    }
    .section-header::after {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      bottom: -10px;
      height: 1px;
      background: linear-gradient(90deg, rgba(20,184,166,.25), rgba(20,184,166,0));
    }
    .section-num {
      font-size: 36px;
      font-family: Arial, Helvetica, sans-serif;
      font-weight: 900;
      color: var(--theme-color);
      margin-right: 14px;
      opacity: .92;
      line-height: 1;
      text-shadow: 0 6px 18px rgba(20,184,166,.12);
    }
    .section-title {
      font-size: 22px;
      font-weight: 900;
      color: var(--text-dark);
      line-height: 1.4;
    }
    .highlight-box {
      background: var(--bg-light);
      padding: 18px 20px;
      border-radius: 14px;
      border-left: 4px solid var(--theme-color);
      margin: 26px 0;
      font-size: 15px;
      box-shadow: 0 10px 24px rgba(20,184,166,.07);
    }
    .highlight-box p:last-child { margin-bottom: 0; }
    strong { color: var(--theme-color); font-weight: 800; }
    .text-underline {
      background: var(--accent-yellow);
      padding: 2px 4px;
      font-weight: 700;
      color: var(--text-dark);
    }
    .sub-title {
      font-size: 18px;
      font-weight: 900;
      margin: 30px 0 14px;
      color: var(--text-dark);
      position: relative;
      padding-left: 12px;
    }
    .sub-title::before {
      content: '';
      position: absolute;
      left: 0;
      top: .25em;
      width: 4px;
      height: 1.1em;
      border-radius: 999px;
      background: var(--theme-color);
    }
    .quote-text {
      border-left: 2px solid var(--border-gray);
      padding: 2px 0 2px 15px;
      color: #6b7280;
      font-size: 14px;
      margin: 22px 0;
    }
    ul { margin: 0 0 1.1em 0; padding: 0; list-style: none; }
    li { margin-bottom: .6em; padding-left: 1.2em; position: relative; }
    li::before { content: '•'; position: absolute; left: 0; color: var(--theme-color); font-weight: 900; }
    a { color: var(--theme-color); text-decoration: underline; }
    code {
      background: #f3f4f6;
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 14px;
    }
    .image-wrap { margin: 22px 0; }
    .image-wrap img { width: 100%; height: auto; border-radius: 10px; display: block; }
  </style>
</head>
<body>
  <div class="art-container">
    ${tag}
    <h1 class="title">${escapeHtml(meta.title)}</h1>
    <div class="meta-row">
      <div class="meta-author">作者：${escapeHtml(meta.author)}</div>
      ${sourceHtml}
    </div>
    ${body}
  </div>
</body>
</html>`;
}

function render(meta: Meta, opts: Options): string {
  if (opts.template !== 'mint-tech') throw new Error(`Unsupported template: ${opts.template}`);
  return renderMintTech(meta, opts);
}

function publishToWechat(htmlPath: string, opts: Options, meta: Meta) {
  if (!opts.cover) throw new Error('--cover is required with --publish');
  const args = [WECHAT_API, htmlPath, '--title', meta.title, '--author', meta.author, '--cover', opts.cover];
  const result = spawnSync('bun', args, { stdio: 'inherit', cwd: process.cwd(), env: process.env });
  if (result.status !== 0) throw new Error(`WeChat publish failed with code ${result.status}`);
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(opts.input);
  const markdown = fs.readFileSync(inputPath, 'utf-8');
  const meta = parseMarkdown(markdown, opts.author);
  const html = render(meta, opts);
  const outputPath = opts.output
    ? path.resolve(opts.output)
    : inputPath.replace(/\.md$/i, `.${opts.template}.html`);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, 'utf-8');
  console.log(JSON.stringify({ title: meta.title, author: meta.author, outputPath, template: opts.template, published: !!opts.publish }, null, 2));
  if (opts.publish) publishToWechat(outputPath, opts, meta);
}

main();
