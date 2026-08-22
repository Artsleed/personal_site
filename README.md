# personal_site

Nathaniel Felsky-Deelstra's personal site. Astro 6, no UI framework, plain CSS with custom properties. Deployed on Vercel — pushing to `main` on GitHub triggers an auto-deploy, no manual steps needed.

## Commands

Run from the project root:

| Command                | Action                                                     |
| :---------------------- | :---------------------------------------------------------- |
| `npm install`            | Install dependencies                                         |
| `npm run dev`            | Start the local dev server at `localhost:4321`                |
| `npm run build`          | Build the production site (also a good pre-push sanity check) |
| `npm run preview`        | Preview the production build locally                          |
| `npm run new-post -- "Title" "description"`    | Scaffold a new blog post                     |
| `npm run new-project -- "Title" "description"` | Scaffold a new project write-up              |

## Adding a blog post

```sh
npm run new-post -- "My Post Title" "A one-sentence description for the listing card."
```

This creates `src/content/blog/my-post-title.md` with the frontmatter already filled in (title, today's date, description) and a starter body. Open the file, replace the body with your actual post (plain Markdown), then `npm run dev` to preview it at `/blog/my-post-title`.

The `description` argument is optional — if you skip it, it's filled with a `TODO: add a description.` placeholder so it's obvious you still need to write one (it shows on the blog listing card).

To backdate a post or fix the title after the fact, just edit the frontmatter directly — there's nothing magic about the generated file.

## Adding a project

Same idea, different collection:

```sh
npm run new-project -- "Project Title" "What it does, in one sentence."
```

Creates `src/content/projects/project-title.md`. The projects page lays these out in a 4-column grid, so shorter titles/descriptions read best.

## Frontmatter reference

Both collections (`src/content/blog/`, `src/content/projects/`) use the same schema, defined in `src/content.config.ts`:

```yaml
---
title: "Post Title"       # string, required
date: 2026-08-22           # YYYY-MM-DD, required — controls sort order (newest first)
description: "..."         # string, required — shown on the listing card
---
```

The Markdown body below the frontmatter becomes the post/project's content.

## Project structure

```
src/
├── components/       # shared Astro components (TerminalWindow, etc.)
├── content/
│   ├── blog/          # blog posts (.md)
│   └── projects/      # project write-ups (.md)
├── content.config.ts  # content collection schemas
├── layouts/
│   └── Layout.astro   # site chrome: nav, footer, global scripts
├── pages/             # routes (index, about, now, blog, projects, resume, + dynamic [slug] pages)
├── scripts/           # client-side JS (reveal-on-scroll, etc.)
└── styles/
    └── global.css     # design tokens, shared utility classes (.kicker, .full-bleed, .typewriter, ...)
```

`scripts/` at the project root (not `src/scripts/`) holds Node-side tooling: `new-content.mjs` (the scaffolding script above) and `spotify-auth.mjs` (one-off auth helper for the Now page's Spotify integration).
