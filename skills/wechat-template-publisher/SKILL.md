---
name: wechat-template-publisher
description: Generate WeChat Official Account HTML from a markdown file using fixed template-driven layouts, then optionally publish to the already configured WeChat draft box. Use when the user wants a specific visual template replicated from a sample and markdown-to-html CSS themes are not enough.
---

# WeChat Template Publisher

Use this skill when the user wants `markdown -> fixed template HTML -> WeChat draft`.

## What This Skill Solves

`baoyu-markdown-to-html` is good for general conversion, but it cannot reliably recreate sample layouts that depend on custom HTML structure. This skill owns the HTML skeleton directly.

## Available Templates

| Name | Description | Status |
|------|-------------|--------|
| `mint-tech` | 薄荷绿科技风：纯色背景、左侧色条、数字章节、圆角卡片 | ✅ Stable |
| `product-canyon` | 产品大峡谷风：深蓝主色、浅灰背景、白字强调 | ✅ Stable |
| `warm-story` | 暖色品牌故事风：红色竖线章节、黄色Q&A框、居中标题、分割线 | ✅ Stable |

## WeChat Compatibility Rules (IMPORTANT)

After testing, WeChat draft box **only reliably preserves**:

- ✅ Pure solid background colors (`background:#f0fdfa`)
- ✅ Border colors and widths (`border:1px solid #d8f4ef`)
- ✅ Border radius (`border-radius:12px`)
- ✅ Padding and margin
- ✅ Text colors (`color:#14b8a6`)
- ✅ Left border strips (`border-left:4px solid #14b8a6`)
- ✅ Basic flex layouts (limited)
- ✅ Tables with borders and cell background
- ✅ Inline `<strong>`, `<code>`, `<a>`

**Do NOT use** (will be stripped):

- ❌ CSS `<style>` blocks and class selectors
- ❌ Gradients (`linear-gradient(...)`)
- ❌ Box shadows (`box-shadow`)
- ❌ Complex pseudo-elements (`::before`, `::after`)
- ❌ CSS custom properties (`var(--...)`)
- ❌ Advanced flex/grid layouts

**Rule**: All styles must be inline `style="..."` on elements. No external CSS.

## Scripts

Use these scripts from this skill directory:

- `scripts/publish.ts` - render markdown into template HTML, optionally publish to WeChat draft

## Usage

Render only (default template is `mint-tech`):

```bash
bun scripts/publish.ts article.md
```

Specify template:

```bash
bun scripts/publish.ts article.md --template mint-tech
```

Render and publish to WeChat draft:

```bash
bun scripts/publish.ts article.md --publish --cover cover.png
```

Optional flags:

- `--template <name>` template name (default: `mint-tech`)
- `--output <path>` custom html output path
- `--tag <text>` top tag text (shown at article top)
- `--author <name>` override author, default `余炜勋`
- `--cover <path>` cover image for WeChat publish (required with `--publish`)
- `--publish` publish generated html to WeChat draft

## Markdown Conventions

Use ordinary markdown. The renderer maps structure into the fixed template.

- `# Title` -> article title
- leading blockquote lines like `> 作者：...` / `> 来源：...` -> meta area
- `## Heading` -> numbered section block (`01`, `02`, ...)
- `### Heading` -> sub-title
- normal paragraphs -> body paragraphs
- `- item` -> bullet list
- `> quote` (non-meta) -> quote block
- `![alt](src)` -> image block

## Notes

- This skill is template-first, not generic.
- When the user wants a new style, add a new template in code rather than trying to bend CSS around a generic converter.
- For WeChat publishing, this skill delegates to the existing `baoyu-post-to-wechat` API script and reuses existing credentials.
