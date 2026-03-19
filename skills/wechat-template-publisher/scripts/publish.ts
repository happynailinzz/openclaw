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
  s = s.replace(/==(.*?)==/g, '<span style="background:#fde68a;padding:2px 4px;font-weight:700;">$1</span>');
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
  return { html: `<p style="margin:0 0 16px 0;font-size:16px;line-height:1.75;color:#374151;">${renderInline(buf.join(' '))}</p>`, next: i };
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
      parts.push(`<div style="display:flex;align-items:baseline;gap:12px;margin:40px 0 18px 0;padding-bottom:10px;border-bottom:1px solid #e5e7eb;">
        <span style="display:inline-block;font-size:32px;font-weight:900;color:#14b8a6;line-height:1;">${String(sectionNo).padStart(2, '0')}</span>
        <span style="display:inline-block;font-size:20px;font-weight:800;color:#111827;line-height:1.4;">${renderInline(h2[1])}</span>
      </div>`);
      i++;
      continue;
    }

    const h3 = line.match(/^###\s+(.+)$/);
    if (h3) {
      parts.push(`<h3 style="margin:30px 0 14px 0;font-size:18px;font-weight:800;color:#111827;padding-left:12px;border-left:4px solid #14b8a6;">${renderInline(h3[1])}</h3>`);
      i++;
      continue;
    }

    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) {
      parts.push(`<div style="margin:20px 0;"><img src="${escapeHtml(img[2])}" alt="${escapeHtml(img[1])}" style="width:100%;height:auto;display:block;border-radius:8px;" /></div>`);
      i++;
      continue;
    }

    if (line.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      parts.push(`<blockquote style="margin:20px 0;padding:2px 0 2px 15px;border-left:2px solid #e5e7eb;color:#6b7280;font-size:14px;line-height:1.6;">${quoteLines.map(renderInline).join('<br>')}</blockquote>`);
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(`<li style="margin:0 0 10px 0;padding-left:18px;position:relative;"><span style="position:absolute;left:0;color:#14b8a6;font-weight:900;">•</span>${renderInline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
        i++;
      }
      parts.push(`<ul style="margin:0 0 18px 0;padding:0;list-style:none;">${items.join('')}</ul>`);
      continue;
    }

    const para = consumeParagraph(lines, i);
    const html = para.html;
    const plainLen = line.length;
    if (!introDone) {
      parts.push(`<div style="margin:0 0 24px 0;padding:16px 18px;background:#f0fdfa;border:1px solid #d8f4ef;border-radius:12px;">${html.replace('margin:0 0 16px 0;', '')}</div>`);
      introDone = true;
    } else if ((html.includes('<strong>') && plainLen < 120) || line.includes('==')) {
      parts.push(`<div style="margin:24px 0;padding:16px 18px;background:#f0fdfa;border-left:4px solid #14b8a6;border-radius:0 12px 12px 0;">${html.replace('margin:0 0 16px 0;', '')}</div>`);
    } else {
      parts.push(html);
    }
    i = para.next;
  }
  return parts.join('\n');
}

function renderMintTech(meta: Meta, opts: Options): string {
  const sourceHtml = meta.sourceLines.length
    ? `<div style="text-align:right;max-width:48%;">${meta.sourceLines.map(renderInline).join('<br>')}</div>`
    : '';
  const tag = opts.tag ? `<p style="margin:0 0 24px 0;font-size:14px;font-weight:700;color:#14b8a6;text-align:center;border:1px dashed #14b8a6;padding:10px 14px;border-radius:8px;background:#f0fdfa;">${renderInline(opts.tag)}</p>` : '';
  const body = renderBody(meta.bodyLines);

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(meta.title)}</title>
</head>
<body style="margin:0;padding:20px;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;color:#374151;line-height:1.75;">
  <section style="max-width:640px;margin:0 auto;">
    ${tag}
    <h1 style="margin:0 0 10px 0;font-size:30px;font-weight:800;line-height:1.35;color:#111827;">${escapeHtml(meta.title)}</h1>
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:0 0 24px 0;padding-bottom:12px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#6b7280;">
      <span style="color:#14b8a6;font-weight:700;">作者：${escapeHtml(meta.author)}</span>
      ${sourceHtml}
    </div>
    ${body}
  </section>
</body>
</html>`;
}

function renderProductCanyon(meta: Meta, opts: Options): string {
  const sourceHtml = meta.sourceLines.length
    ? `<div style="text-align:right;max-width:48%;color:#94a3b8;">${meta.sourceLines.map(renderInline).join('<br>')}</div>`
    : '';
  const tag = opts.tag ? `<p style="margin:0 0 24px 0;font-size:13px;font-weight:600;color:#3b82f6;text-align:center;padding:8px 16px;background:#1e3a5f;border-radius:6px;">${renderInline(opts.tag)}</p>` : '';
  const body = renderBodyCanyon(meta.bodyLines);

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(meta.title)}</title>
</head>
<body style="margin:0;padding:20px;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;color:#334155;line-height:1.75;">
  <section style="max-width:640px;margin:0 auto;">
    ${tag}
    <h1 style="margin:0 0 10px 0;font-size:30px;font-weight:800;line-height:1.35;color:#0f172a;">${escapeHtml(meta.title)}</h1>
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:0 0 24px 0;padding-bottom:12px;border-bottom:1px solid #e2e8f0;font-size:13px;">
      <span style="color:#3b82f6;font-weight:700;">作者：${escapeHtml(meta.author)}</span>
      ${sourceHtml}
    </div>
    ${body}
  </section>
</body>
</html>`;
}

function renderWarmStory(meta: Meta, opts: Options): string {
  const sourceHtml = meta.sourceLines.length
    ? `<p style="color:#999999;font-size:13px;margin:0;">${meta.sourceLines.map(renderInline).join(' | ')}</p>`
    : '';
  const tag = opts.tag ? `<p style="margin:0 0 24px 0;font-size:14px;font-weight:600;color:#d32f2f;text-align:center;">${renderInline(opts.tag)}</p>` : '';
  const body = renderBodyWarm(meta.bodyLines);

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(meta.title)}</title>
</head>
<body style="margin:0;padding:20px;background:#f5f5f5;font-family:'PingFang SC','Microsoft YaHei',sans-serif;color:#333333;line-height:1.8;">
  <section style="max-width:600px;margin:0 auto;background:#ffffff;padding:30px 20px;">
    <header style="text-align:center;margin-bottom:30px;">
      <h1 style="font-size:24px;color:#333333;line-height:1.4;margin:0 0 10px 0;">${escapeHtml(meta.title)}</h1>
      ${sourceHtml}
    </header>
    ${tag}
    ${body}
  </section>
</body>
</html>`;
}

function renderBodyWarm(lines: string[]): string {
  const parts: string[] = [];
  let i = 0;
  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trim();
    if (!line || line === '---') {
      i++;
      continue;
    }

    const h2 = line.match(/^##\s+(.+)$/);
    if (h2) {
      parts.push(`<p style="font-size:20px;font-weight:bold;color:#d32f2f;margin:35px 0 18px 0;">💡 ${renderInline(h2[1])}</p>`);
      i++;
      continue;
    }

    const h3 = line.match(/^###\s+(.+)$/);
    if (h3) {
      parts.push(`<p style="font-size:17px;font-weight:bold;color:#333333;margin:28px 0 12px 0;">▶ ${renderInline(h3[1])}</p>`);
      i++;
      continue;
    }

    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) {
      parts.push(`<p style="margin:25px 0;"><img src="${escapeHtml(img[2])}" alt="${escapeHtml(img[1])}" style="width:100%;border-radius:6px;display:block;" /></p>`);
      i++;
      continue;
    }

    if (line === '---') {
      parts.push(`<p style="text-align:center;margin:30px 0;color:#dddddd;font-size:14px;">· · ·</p>`);
      i++;
      continue;
    }

    if (line.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      const isQA = quoteLines.some(l => l.match(/^Q:/)) || quoteLines.some(l => l.match(/^A:/));
      if (isQA) {
        const qaHtml = quoteLines.map(l => {
          const isQ = l.match(/^Q:/);
          const isA = l.match(/^A:/);
          const content = l.replace(/^[QA]:\s*/, '');
          if (isQ) return `<p style="margin:0 0 12px 0;color:#3498db;"><strong>Q:</strong> ${renderInline(content)}</p>`;
          if (isA) return `<p style="margin:0 0 12px 0;color:#d32f2f;"><strong>A:</strong> ${renderInline(content)}</p>`;
          return `<p style="margin:0 0 10px 0;">${renderInline(l)}</p>`;
        }).join('');
        parts.push(`<div style="background:#fffdf2;padding:16px;margin:20px 0;border-radius:4px;border-left:3px solid #f1c40f;">${qaHtml}</div>`);
      } else {
        parts.push(`<div style="background:#fffdf2;padding:16px;margin:20px 0;border-radius:4px;border-left:3px solid #f1c40f;color:#555555;">${quoteLines.map(renderInline).join('<br>')}</div>`);
      }
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(`<li style="margin-bottom:8px;">${renderInline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
        i++;
      }
      parts.push(`<ul style="margin:0 0 18px 20px;padding:0;">${items.join('')}</ul>`);
      continue;
    }

    const para = consumeParagraph(lines, i);
    parts.push(para.html);
    i = para.next;
  }
  return parts.join('\n');
}

function renderBodyCanyon(lines: string[]): string {
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
      parts.push(`<div style="display:flex;align-items:center;gap:10px;margin:36px 0 16px 0;padding:12px 16px;background:#1e3a5f;border-radius:8px;">
        <span style="display:inline-block;font-size:20px;font-weight:900;color:#ffffff;min-width:28px;">${String(sectionNo).padStart(2, '0')}</span>
        <span style="display:inline-block;font-size:18px;font-weight:700;color:#ffffff;">${renderInline(h2[1])}</span>
      </div>`);
      i++;
      continue;
    }

    const h3 = line.match(/^###\s+(.+)$/);
    if (h3) {
      parts.push(`<h3 style="margin:28px 0 12px 0;font-size:17px;font-weight:700;color:#0f172a;padding:8px 12px;background:#e2e8f0;border-radius:6px;">${renderInline(h3[1])}</h3>`);
      i++;
      continue;
    }

    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) {
      parts.push(`<div style="margin:18px 0;"><img src="${escapeHtml(img[2])}" alt="${escapeHtml(img[1])}" style="width:100%;height:auto;display:block;border-radius:8px;border:1px solid #e2e8f0;" /></div>`);
      i++;
      continue;
    }

    if (line.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      parts.push(`<blockquote style="margin:18px 0;padding:12px 16px;background:#f1f5f9;border-left:3px solid #3b82f6;border-radius:0 8px 8px 0;color:#475569;font-size:14px;line-height:1.6;">${quoteLines.map(renderInline).join('<br>')}</blockquote>`);
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(`<li style="margin:0 0 8px 0;padding-left:16px;position:relative;color:#334155;"><span style="position:absolute;left:0;color:#3b82f6;font-weight:700;">▸</span>${renderInline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
        i++;
      }
      parts.push(`<ul style="margin:0 0 16px 0;padding:0;list-style:none;">${items.join('')}</ul>`);
      continue;
    }

    const para = consumeParagraph(lines, i);
    const html = para.html;
    const plainLen = line.length;
    if (!introDone) {
      parts.push(`<div style="margin:0 0 22px 0;padding:14px 16px;background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">${html.replace('margin:0 0 16px 0;', '')}</div>`);
      introDone = true;
    } else if ((html.includes('<strong>') && plainLen < 120) || line.includes('==')) {
      parts.push(`<div style="margin:22px 0;padding:14px 16px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;">${html.replace('margin:0 0 16px 0;', '')}</div>`);
    } else {
      parts.push(html);
    }
    i = para.next;
  }
  return parts.join('\n');
}

function render(meta: Meta, opts: Options): string {
  if (opts.template === 'mint-tech') return renderMintTech(meta, opts);
  if (opts.template === 'product-canyon') return renderProductCanyon(meta, opts);
  if (opts.template === 'warm-story') return renderWarmStory(meta, opts);
  throw new Error(`Unsupported template: ${opts.template}. Available: mint-tech, product-canyon, warm-story`);
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
