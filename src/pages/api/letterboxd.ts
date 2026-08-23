import type { APIRoute } from 'astro';

export const prerender = false;

const RSS_URL = 'https://letterboxd.com/Artsleed/rss/';
const FILM_COUNT = 5;
// Only the first (currently-displayed) poster is worth blocking initial
// page load for - it alone was ~70KB of the ~356KB this endpoint used to
// return. The rest are fetched on demand from /api/poster as the user
// actually cycles to them (see DeskScene.astro), which is the common case
// of "never," not "always."
const EAGER_COUNT = 1;

interface Film {
  title: string;
  link: string;
  // A data: URI (eager films only) or null - Letterboxd's poster CDN sends
  // no CORS headers, which would otherwise taint the WebGL texture the
  // desk scene paints it onto. Fetching and re-encoding it server-side
  // (here, or lazily via /api/poster) sidesteps that entirely.
  thumb: string | null;
  // Original CDN url, present when `thumb` is null, so the client can
  // request it lazily from /api/poster.
  sourceUrl: string | null;
}

function extractTag(block: string, tag: string): string {
  const match = block.match(new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`));
  return match ? match[1].trim() : '';
}

function extractImageUrl(block: string): string | null {
  const match = block.match(/<img[^>]+src="([^"]+)"/);
  return match ? match[1] : null;
}

async function toDataUri(url: string): Promise<string | null> {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const contentType = res.headers.get('content-type') ?? 'image/jpeg';
    const buffer = Buffer.from(await res.arrayBuffer());
    return `data:${contentType};base64,${buffer.toString('base64')}`;
  } catch {
    return null;
  }
}

export const GET: APIRoute = async () => {
  const jsonHeaders = {
    'Content-Type': 'application/json',
    'Cache-Control': 's-maxage=1800, stale-while-revalidate=3600',
  };

  try {
    const res = await fetch(RSS_URL);
    if (!res.ok) throw new Error(`Letterboxd RSS responded ${res.status}`);
    const xml = await res.text();

    const blocks = xml.split('<item>').slice(1, FILM_COUNT + 1);
    const films: Film[] = await Promise.all(
      blocks.map(async (block, i) => {
        const title = extractTag(block, 'title');
        const link = extractTag(block, 'link');
        const imageUrl = extractImageUrl(block);
        if (i < EAGER_COUNT) {
          const thumb = imageUrl ? await toDataUri(imageUrl) : null;
          return { title, link, thumb, sourceUrl: null };
        }
        return { title, link, thumb: null, sourceUrl: imageUrl };
      })
    );

    return new Response(JSON.stringify({ films }), { headers: jsonHeaders });
  } catch {
    return new Response(JSON.stringify({ films: [], error: 'Could not load Letterboxd feed' }), {
      status: 502,
      headers: jsonHeaders,
    });
  }
};
