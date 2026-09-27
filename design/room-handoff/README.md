# Room design handoff (archived reference)

This is what's still useful from the original design handoff for the homepage room, kept here so it's version-controlled instead of sitting in a Downloads folder. Everything else from that package has already been fully absorbed into the live site and doesn't need to be kept separately:

- `room.svg` was copied into `src/assets/room/room.svg` and hand-edited since (see the comment block at the top of `src/components/RoomHome.astro` for exactly what changed and why).
- `tokens.css`'s palette/fonts are now the site's actual global design tokens (`src/styles/global.css`).
- `prototype/index.html`'s open/close/hash/focus behaviour is fully ported into `RoomHome.astro`.
- `design/Main.dc.html` (the original interactive mockup) was explicitly "reference only" even in the original handoff and is fully superseded by the live site.

## What's kept here, and why

- **`HANDOFF.md`** — the full original spec. Kept mainly because section 8 ("Open decisions") still has the recommended approach for small-screen/mobile layout, which hasn't been built yet — read it before starting that work rather than re-deriving the approach from scratch.
- **`hotspots.json`** — the original hotspot/label/arrow coordinates the current `src/data/room-zones.ts` was transcribed from. `room-zones.ts` is the live source of truth now (and has since been refined against the actual rendered SVG - see `RoomHome.astro`'s comments), so treat this as historical, not authoritative, if the two ever disagree.
- **`room-preview.png`** — the original target image the room was built to match. Useful as a visual reference if the art ever needs revisiting.
- **`gen2.py` / `gen3.py`** — the scripts that generated the room's perspective-projected shapes. **Not a working one-command pipeline as kept here**: both have hardcoded absolute output paths from wherever they were originally run (not this machine), and `gen3.py`'s actual output is an interactive `.dc.html` mockup format, not `room.svg` directly - the real `room.svg` was manually exported/extracted from that at some earlier step not captured by these two scripts alone. Treat them as a reference for the perspective-camera math (see the constants at the top of `gen2.py`: eye height, room dimensions) if you ever want to redo the room's geometry, not as something you can just re-run.
