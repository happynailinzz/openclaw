---
name: wechat-template-publisher
description: Generate WeChat Official Account HTML from a markdown file using fixed template-driven layouts, then optionally publish to the already configured WeChat draft box. Use when the user wants a specific visual template replicated from a sample and markdown-to-html CSS themes are not enough.
---

# WeChat Template Publisher

Use this skill when the user wants `markdown -> fixed template HTML -> WeChat draft`.

## What This Skill Solves

`baoyu-markdown-to-html` is good for general conversion, but it cannot reliably recreate sample layouts that depend on custom HTML structure. This skill owns the HTML skeleton directly.

Current supported template:

- `mint-tech` - mint-green tech article layout with top tag, big numbered sections, highlight boxes, and quote blocks

## Scripts

Use these scripts from this skill directory:

- `scripts/publish.ts` - render markdown into template HTML, optionally publish to WeChat draft

## Usage

Render only:

```bash
bun scripts/publish.ts article.md --template mint-tech
```

Render and publish:

```bash
bun scripts/publish.ts article.md --template mint-tech --publish --cover cover.png
```

Optional flags:

- `--template <name>` default: `mint-tech`
- `--output <path>` custom html output path
- `--tag <text>` top tag text
- `--author <name>` override author, default `余炜勋`
- `--cover <path>` cover image for WeChat publish
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
