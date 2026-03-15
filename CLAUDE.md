# CLAUDE.md — AI Assistant Guide for jovanepires.github.io

This file documents the codebase structure, conventions, and workflows for AI assistants working on this repository.

## Project Overview

Personal professional blog and portfolio site for **Jovane Pires** (Data Engineer & Software Engineer). The tagline is "Mais que um arquivo pessoal, um backup" — a place to document and share technical knowledge.

- **Live site**: https://jovanepires.com
- **Stack**: Hugo (static site generator) + GitHub Pages
- **Theme**: [Hugo Winston Theme](https://github.com/zerostaticthemes/hugo-winston-theme) (managed as a git submodule)
- **Primary language**: Portuguese (pt-br)

---

## Repository Structure

```
.
├── .github/workflows/hugo.yaml   # CI/CD: GitHub Actions build & deploy
├── archetypes/                   # Hugo content templates (new post scaffolds)
│   ├── default.md
│   ├── pages.md
│   └── posts.md
├── content/                      # All site content (Markdown)
│   ├── _index.md                 # Homepage content
│   ├── pages/
│   │   └── sobre.md              # About/Bio page
│   └── posts/
│       └── _index.md             # Blog index
├── data/
│   ├── author.json               # Author metadata
│   └── social.json               # Social media links
├── old/                          # Archived old blog posts (not published)
├── static/                       # Static assets (images, favicon)
│   ├── favicon.png
│   └── images/
├── themes/
│   └── hugo-winston-theme/       # Git submodule — do not edit directly
├── config.toml                   # Hugo main configuration
├── CNAME                         # Custom domain (jovanepires.com)
└── robots.txt                    # SEO robots configuration
```

---

## Technology Stack

| Tool | Version / Details |
|------|-------------------|
| Hugo | v0.125.4 Extended (required for SCSS compilation) |
| Theme | hugo-winston-theme (Zerostatic) |
| Deployment | GitHub Actions → GitHub Pages |
| Markup | Markdown (Goldmark processor, unsafe HTML enabled) |
| Styles | SCSS compiled via Hugo Pipes |
| Analytics | Google Analytics (UA-41937971-1) |

---

## Local Development

### Prerequisites

- Hugo Extended v0.125.4+ (the `extended` variant is required for SCSS)
- Dart Sass (for SCSS compilation)

### Running locally

```bash
# Serve site with live reload
hugo server

# Build production site
hugo --gc --minify
```

### Theme submodule

The theme is tracked as a git submodule. When cloning:

```bash
git clone --recurse-submodules <repo-url>

# Or if already cloned:
git submodule update --init --recursive
```

**Do not edit files inside `themes/hugo-winston-theme/` directly.** Override theme layouts by creating files with the same path under the root `layouts/` directory (Hugo's theme override mechanism).

---

## Content Authoring

### Creating a new blog post

```bash
hugo new posts/my-post-title.md
```

This uses the archetype at `archetypes/posts.md`, which scaffolds:
```yaml
---
title: ""
date: {{ .Date }}
description: ""
image: ""
draft: true
---
```

Set `draft: false` when the post is ready to publish.

### Creating a new page

```bash
hugo new pages/my-page.md
```

Uses `archetypes/pages.md`. Pages can be added to the site menu via the `menu` frontmatter key.

### Content conventions

- **Language**: Write content in Portuguese (pt-br) unless the topic is clearly English-targeted
- **Frontmatter format**: YAML (between `---` delimiters)
- **Images**: Place in `static/images/` and reference as `/images/filename.ext`
- **Drafts**: New content starts as `draft: true`; flip to `false` to publish
- **Posts** go in `content/posts/`, **standalone pages** go in `content/pages/`

### Frontmatter reference

For posts:
```yaml
---
title: "Post title"
date: 2024-01-15T10:00:00-03:00
description: "Brief description for SEO and listing pages"
image: "/images/my-image.jpg"
draft: false
tags: ["tag1", "tag2"]
---
```

For pages:
```yaml
---
title: "Page Title"
date: 2024-01-15
url: /my-page/
image: "/images/my-image.jpg"
menu:
  main:
    name: "Menu Label"
    weight: 40
---
```

---

## Configuration

Main config is at `config.toml`. Key sections:

```toml
baseURL = "https://jovanepires.com/"
languageCode = "pt-br"

[params]
  # Color scheme (orange accent)
  primary_color = "#E86425"

[menu]
  # Navigation menu items
  [[menu.main]]
    name = "Home"
    url = "/"
    weight = 10
```

**Data files** (`data/`):
- `author.json` — Name, bio, avatar path
- `social.json` — Social media URLs (GitHub, LinkedIn with UTM tracking)

---

## Deployment

Deployment is fully automated via `.github/workflows/hugo.yaml`:

1. **Trigger**: Push to `main` branch (or manual `workflow_dispatch`)
2. **Build**: Hugo Extended with `--gc --minify`
3. **Deploy**: GitHub Pages artifact upload

**To deploy**: merge or push to `main`. No manual steps required.

### Branch strategy

- `main` — production branch, triggers deployment
- Feature/AI branches — use `claude/<description>` naming convention
- Never push directly to `main` without review

---

## Key Conventions for AI Assistants

### What to do

- Keep new content in Portuguese unless the topic demands English
- Use the archetype templates when creating new content (`hugo new ...`)
- Place images in `static/images/` and reference with absolute paths (`/images/...`)
- Respect the existing TOML config format — do not convert to YAML
- When overriding theme layouts, create files in the root `layouts/` directory, not inside `themes/`
- Commit with clear, descriptive messages (mix of Portuguese or English is acceptable, matching existing history)

### What to avoid

- Do not edit files inside `themes/hugo-winston-theme/` — it is a git submodule
- Do not set `draft: false` on new posts without explicit instruction
- Do not change `baseURL` or `googleAnalytics` values
- Do not add new dependencies or change the build tool versions without confirmation
- Do not delete files from `old/` — they are intentionally archived
- Do not touch `CNAME`, `robots.txt`, or `googled89e98794302c399.html`

### Styling

- Theme styles live in the submodule (`themes/hugo-winston-theme/assets/scss/`)
- To add custom CSS, create `assets/scss/` at the root level and import it via a layout override
- Primary accent color: `#E86425` (orange)

---

## Author Information

- **Name**: Jovane Pires
- **Role**: Data Engineer & Software Engineer
- **Location**: Brazil
- **GitHub**: [@jovanepires](https://github.com/jovanepires?utm_source=jovanepires.com)
- **LinkedIn**: [jovanepires](https://www.linkedin.com/in/jovanepires/?utm_source=jovanepires.com)
- **About page**: `content/pages/sobre.md`

---

## SEO & Analytics

- Custom domain via `CNAME` (jovanepires.com)
- Google Analytics ID: `UA-41937971-1` (configured in `config.toml`)
- Sitemap reference: `sitemaps.xml`
- Robots: permissive `robots.txt`
- Google Search Console verification: `googled89e98794302c399.html`
