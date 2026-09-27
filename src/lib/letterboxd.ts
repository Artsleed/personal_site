// Shared by /api/letterboxd.ts (the JSON endpoint the room's client-side
// script fetches for the frame posters + Films card) and films.astro (which
// imports this directly and renders server-side, avoiding a redundant HTTP
// round-trip to its own API route).

const RSS_URL = 'https://letterboxd.com/Artsleed/rss/';
const FILM_COUNT = 12;

export interface Film {
  title: string;
  year: string;
  rating: number | null;
  watchedDate: string;
  rewatch: boolean;
  poster: string | null;
  link: string;
}

// RSS/XML text nodes come entity-encoded (titles with an "&" or "'" - e.g.
// "Bill &amp; Ted&#039;s Excellent Adventure" - are legitimately encoded
// that way in the feed). extractTag() below is a plain regex slice, not a
// real XML parser, so it pulls that encoding through as literal text -
// decode it here rather than rendering "&amp;" as visible page text.
function decodeEntities(str: string): string {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&#0?39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function extractTag(block: string, tag: string): string {
  const match = block.match(new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`));
  return match ? decodeEntities(match[1].trim()) : '';
}

function extractImageUrl(block: string): string | null {
  const match = block.match(/<img[^>]+src="([^"]+)"/);
  return match ? match[1] : null;
}

export function renderStars(rating: number | null): string {
  if (rating == null) return '';
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  return '★'.repeat(full) + (half ? '½' : '');
}

export async function fetchLetterboxdFilms(): Promise<Film[]> {
  const res = await fetch(RSS_URL);
  if (!res.ok) throw new Error(`Letterboxd RSS responded ${res.status}`);
  const xml = await res.text();

  const blocks = xml.split('<item>').slice(1, FILM_COUNT + 1);
  return blocks.map((block) => {
    const ratingRaw = extractTag(block, 'letterboxd:memberRating');
    return {
      title: extractTag(block, 'letterboxd:filmTitle'),
      year: extractTag(block, 'letterboxd:filmYear'),
      rating: ratingRaw ? Number(ratingRaw) : null,
      watchedDate: extractTag(block, 'letterboxd:watchedDate'),
      rewatch: extractTag(block, 'letterboxd:rewatch') === 'Yes',
      poster: extractImageUrl(block),
      link: extractTag(block, 'link'),
    };
  });
}
