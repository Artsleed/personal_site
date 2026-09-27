# The Room: handoff for building the site

This is the design handoff for Nathaniel's personal site redesign. It's meant to be read by Claude Code working in the `personal_site` repo (Astro, deployed on Vercel).

The design is finished at desktop size. The job now is to build it into the existing Astro site and hook it up to real data.

---

## 1. The concept

The home page is **Nathaniel's room at night, seen from the doorway**. It's an immersive illustration where you look straight in at the back wall and the side walls angle away from you. Every major section of the site is an object in the room. Clicking an object dims the room and opens a card for that section. The card has a preview and a button to go to the full page.

It should feel like a look into his life, not like a video game. Keep it calm, warm and handmade: the room is a dark, cool blue-grey, lit by an orange desk lamp, with short handwritten labels.

| Zone id | Object in the room | Section | Suggested route | Data source |
|---|---|---|---|---|
| `projects` | Corkboard with sticky notes (back wall) | Projects | `/projects` | Astro content collection |
| `blog` | Dark grey IKEA ALEX desk, monitor, green banker's lamp | Writing | `/blog` | Astro content collection (existing blog) |
| `films` | Two framed posters (right wall) | Films | `/films` | Letterboxd RSS, user `Artsleed` |
| `music` | Cabinet with turntable and bookshelf speaker | On rotation | `/music` | Spotify Web API (now playing / recently played) |
| `about` | Traditional bookcase (left wall) | About | `/about` | Static page (existing) |
| `resume` | Framed page under a picture light (left wall) | Resume | `/resume` | PDF in `public/` |

The room has **no "Now" section any more**. What the old Now page did (the Letterboxd feed, and the music planned for it) now lives in the Films and On rotation sections. The existing `/now` route should be removed or redirected. See the open decisions below.

---

## 2. What's in this package

```
room-handoff/
├─ HANDOFF.md              ← this file
├─ design/
│  ├─ room.svg             ← the finished illustration, 1440×900, self-contained (no labels or UI)
│  ├─ room-preview.png     ← what it looks like
│  ├─ hotspots.json        ← clickable areas, labels, arrow paths and routes for every zone
│  ├─ tokens.css           ← colours, fonts, the look of the UI pieces
│  └─ Main.dc.html         ← the original design file (reference only)
├─ prototype/
│  └─ index.html           ← WORKING reference: room + hotspots + labels + cards + nav, in plain JS
└─ tools/
   ├─ gen2.py              ← draws the room in perspective and outputs the SVG shapes + hotspot boxes
   └─ gen3.py              ← wraps it into the design file (labels, cards, styles)
```

**Start by opening `prototype/index.html` in a browser.** It shows the exact intended behaviour: hover outlines, clicking an object, Esc or clicking outside to close, the nav row, and deep links like `#projects`. Port that behaviour; don't reinvent it.

---

## 3. Visual spec

### Stage and scaling
- The artwork is drawn on a **1440 × 900** canvas. `room.svg` uses `viewBox="0 0 1440 900"`, so it scales cleanly to any size.
- All overlay positions (hotspots, labels, arrows) are in that same 1440 × 900 space. Use `hotspotPct` from `hotspots.json` to position the clickable areas in percentages over the scaled SVG. Alternatively, put the SVG and overlays in one wrapper and scale that as a whole, which is what the prototype does.
- Desktop: the room fills the viewport (`object-fit: cover` behaviour, anchored at the centre). Everything that matters sits in the central ~85%, so some cropping at the edges on wide or tall screens is fine.

### Tokens (also in `design/tokens.css`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#0d1217` | page background |
| `--ink` | `#e3ddd2` | primary text |
| `--ink-strong` | `#efe8dc` | headings |
| `--ink-body` | `#b5bfca` | card body copy |
| `--ink-muted` | `#8e9aa6` | captions, metadata |
| `--accent` | `#ee8a45` | the one accent: buttons, links, the lamp glow (his favourite colour) |
| `--accent-hover` | `#f4a56b` | link hover |
| `--panel` | `#111820` | card background |
| `--panel-line` | `#263241` / `#243040` | card border / row dividers |
| `--hand` | `#d8cbb3` | handwritten labels and their arrows |

**Fonts** (Google Fonts): *Instrument Serif* 400 for his name and card titles, *Hanken Grotesk* 400/500/600 for body and UI, *Caveat* 500 for the handwritten labels and the card eyebrows ("the corkboard"). Load them in the base layout. If they fail to load, everything falls back to a plain serif.

### UI pieces (see the prototype for the exact CSS)
- **Header** (top-left): "Nathaniel" in Instrument Serif at 40px, with the line "Come in. Everything on the site lives somewhere in this room." underneath.
- **Nav row** (top-right): Projects · Writing · Films · On rotation · About · Resume, plus a **Plain version** link. This is the keyboard and screen-reader path through the site; keep it.
- **Hotspots**: invisible `<button>`s over each object, each with `aria-label="Projects, the corkboard"` and so on. On hover or focus they show a 1.5px dashed orange outline with a faint orange tint.
- **Handwritten labels**: Caveat at 26px in `--hand`, with a curved ink arrow pointing to the object (paths are in `hotspots.json`). They're hidden while a card is open.
- **Zone card**: the room dims behind a full-screen scrim (`rgba(8,11,15,.62)`, and clicking it closes the card). The card is 408px wide, sits at the right, and has an 18px radius. Inside, top to bottom: a "← Back to the room" button, the Caveat eyebrow (object name, in accent), the Instrument Serif title at 56px, body copy, a preview (a list, a poster grid or a now-playing row), then an orange pill button ("All projects →" and so on).

---

## 4. Behaviour to build

1. Clicking a hotspot or a nav item opens that zone's card. The URL hash updates (`/#films`), so cards can be linked to and shared.
2. Esc, the scrim, or "Back to the room" closes the card, clears the hash, and returns focus to whatever opened it.
3. Loading `/#music` directly opens that card.
4. Each card's orange button goes to the full page for that section (routes in the table above).
5. **Plain version** goes to a simple text-and-links version of the site (the existing pages restyled with the tokens are enough).
6. Honour `prefers-reduced-motion`. If you add any open/close animation (a quick fade and 8px rise is plenty), turn it off under that setting.
7. Nice to have: a subtle "zoom toward the object" when a card opens (scale the room around the object's centre). Only do this after everything else works.

---

## 5. Data and backend

- **Films (Letterboxd)**: fetch `https://letterboxd.com/artsleed/rss/` on the server. Parse the last four diary entries: title, year, rating, watched date, poster image from the item description. Cache the result (revalidate hourly, or rebuild daily). The card shows four posters. `/films` shows the longer diary.
- **On rotation (Spotify)**: one small serverless endpoint (for example `src/pages/api/now-playing.ts`, rendered on demand on Vercel). It uses the authorization-code flow once to get a **refresh token**, then stores `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` and `SPOTIFY_REFRESH_TOKEN` as Vercel environment variables. The endpoint swaps the refresh token for an access token, calls *currently playing*, and falls back to *recently played*. Cache for 30 to 60 seconds. The card shows the album art, track, artist and "now playing" or "last played".
- **Projects and Writing**: Astro content collections. Projects should follow the existing plan: a technical spec header (stack, hardware, dates, repo link) followed by an editorial write-up of the process. The corkboard card lists the four most recent or pinned projects.
- **Resume**: `public/resume.pdf`, linked from the card as a download.
- **About**: static content (the card copy is already written; see the prototype).

---

## 6. What's placeholder vs real

- **Real, from Nathaniel:** the project names (Magic mirror mk1, aQuatonomous sim, Daft Punk helmet, This website) and the About text (second-year Computer Engineering at Queen's, works at the Canadian Labour Congress on AI and work, climbing, hardware, films).
- **Placeholder, marked with [square brackets] in the prototype:** blog post titles, film posters and the track row. Those get replaced by live data.
- **Illustration stand-ins:** the poster art on the right wall and the page in the resume frame are generic drawings, and the monitor shows fake code. Later options: swap the posters for his actual favourite films (as art, not copyrighted poster images) and show a real resume thumbnail.

---

## 7. Suggested build order

1. **Room component.** Add `src/components/Room.astro`, which inlines `room.svg`, draws the hotspot buttons from `hotspots.json`, and adds the labels and arrows. Make it the home page. *Done when:* it looks identical to `design/room-preview.png` at 1440×900 and scales without distortion.
2. **Zone cards and routing.** Port the prototype's open/close logic, hash deep links, focus handling and Esc. *Done when:* everything in section 4 works from the keyboard alone.
3. **Section pages.** Restyle the existing pages (`/projects`, `/blog`, `/about`, `/resume`) with the tokens, add `/films` and `/music`, and decide what happens to `/now`. Build the Plain version.
4. **Letterboxd feed** into the Films card and page.
5. **Spotify endpoint** into the On rotation card and page.
6. **Small screens** (see below).
7. **Polish:** open/close animation, reduced motion, meta tags and an OG image (a crop of the room works well), Lighthouse pass. Keep the SVG inline. It's about 125 KB raw and about 26 KB gzipped, since it's mostly flat polygons.

---

## 8. Open decisions (ask Nathaniel)

- **Small screens.** The room is designed for desktop. The recommendation is that under about 900px wide, you show a cropped strip of the room as a hero image, then a vertical list of the six zones (object name in Caveat plus section title) that opens the same cards as full-screen sheets. The alternative is a room you can pan horizontally, which is more work and fiddly on touch.
- **What happens to `/now`**: redirect it to `/films`, or keep it as an unlinked page.
- **Separate pages vs cards only**: the plan assumes each card previews a full page. The alternative is making the cards the whole experience.
- **Labels**: they're on by default. There's an argument for showing them only on first visit or on hover.

---

## 9. Changing the art later

The room is generated by the scripts in `tools/`, not drawn by hand, so tweaks are easiest there. `gen2.py` places everything in real-world metres using a simple perspective camera: eye height 1.45 m, room 3.6 m wide × 4.2 m deep × 2.6 m high. It writes the SVG shapes and the hotspot boxes. `gen3.py` wraps them in the design file.

To regenerate:

```
python3 tools/gen2.py && python3 tools/gen3.py
```

Paths at the top of both scripts point at the original workspace; update them. After regenerating, re-export `room.svg` and `hotspots.json`. Alternatively, edit `room.svg` directly for small colour changes.

---

## 10. Kickoff prompt for Claude Code

> Read `room-handoff/HANDOFF.md` and open `room-handoff/prototype/index.html` to see the intended behaviour. Then look at this Astro repo's structure, config and existing pages, and propose a short plan that follows the build order in section 7 of the handoff. Before writing code, ask me about the open decisions in section 8. Start with step 1 (the Room component on the home page) and show me it matches `design/room-preview.png` before moving on.
