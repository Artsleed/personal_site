# personal_site

Nathaniel Felsky-Deelstra's personal site. Astro 6, no UI framework, plain CSS with custom properties. Deployed on Vercel — pushing to `main` on GitHub triggers an auto-deploy, no manual steps needed.

The homepage is an illustrated room (`src/components/RoomHome.astro`) — click an object to open a card previewing that section, with a button through to its full page. Every other page shares the room's design tokens and links back to it via the header.

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

Both collections (`src/content/blog/`, `src/content/projects/`) use the same schema, defined in `src/content.config.ts`. Projects have a few extra optional fields (`stack`, `status`, `role`, `started`, `processNote`, `aside`) shown on the project's own page via `SpecHeader.astro`.

```yaml
---
title: "Post Title"       # string, required
date: 2026-08-22           # YYYY-MM-DD, required — controls sort order (newest first)
description: "..."         # string, required — shown on the listing card
---
```

The Markdown body below the frontmatter becomes the post/project's content.

## Live data

- **Films** (`/films`, the room's picture frames, the Films card): pulled from a Letterboxd RSS feed by `src/lib/letterboxd.ts`, used by `src/pages/api/letterboxd.ts` (fetched client-side by the room) and by `films.astro` directly (server-rendered per visit).
- **On rotation** (`/music`, the room's record player card): currently-playing/last-played track from Spotify, via `src/lib/spotify.ts`. Needs `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` and `SPOTIFY_REFRESH_TOKEN` (as env vars locally in `.env`, and in Vercel's project settings for production). If you ever need a fresh refresh token, run `node --env-file=.env scripts/spotify-auth.mjs` and follow the prompts — it runs a one-off local OAuth flow and prints the token to save.

## Project structure

```
src/
├── assets/room/       # room.svg, the homepage illustration (see RoomHome.astro)
├── components/
│   ├── RoomHome.astro   # the homepage room: hotspots, labels, zone cards
│   ├── Panel.astro       # bordered container, used across content pages
│   └── SpecHeader.astro  # stack/status/role/started strip on project pages
├── content/
│   ├── blog/          # blog posts (.md)
│   └── projects/      # project write-ups (.md)
├── content.config.ts  # content collection schemas
├── data/
│   └── room-zones.ts  # the room's 6 zones: hotspot position, label, card copy, route
├── layouts/
│   └── Layout.astro   # site chrome: header (name + "back to the room"), footer, global scripts
├── lib/
│   ├── letterboxd.ts   # fetch + parse the Letterboxd RSS feed
│   └── spotify.ts      # Spotify OAuth + currently-playing/recently-played
├── pages/             # routes: index (the room), about, blog, projects, resume, films,
│                       # music, plain (text-only fallback), + api/ and dynamic [slug] pages
├── scripts/           # client-side JS (reveal-on-scroll, etc.)
└── styles/
    └── global.css     # design tokens, shared utility classes (.kicker, .full-bleed, ...)
```

`scripts/` at the project root (not `src/scripts/`) holds Node-side tooling: `new-content.mjs` (the scaffolding script above) and `spotify-auth.mjs` (the one-off Spotify OAuth helper mentioned above).

See `CLAUDE.md` for the design system, known gotchas, and more detail on how the room works.
