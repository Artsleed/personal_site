import type { APIRoute } from 'astro';

export const prerender = false;

const RSS_URL = 'https://letterboxd.com/Artsleed/rss/';
const FILM_COUNT = 5;

interface Film {
  title: string;
  link: string;
  // A data: URI, not the original CDN url - Letterboxd's poster CDN doesn't
  // send CORS headers, which would otherwise taint the WebGL texture the
  // desk scene paints it onto. Fetching and re-encoding it server-side
  // sidesteps that entirely (data: URIs are always same-origin-safe).
  thumb: string | null;
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
      blocks.map(async (block) => {
        const title = extractTag(block, 'title');
        const link = extractTag(block, 'link');
        const imageUrl = extractImageUrl(block);
        const thumb = imageUrl ? await toDataUri(imageUrl) : null;
        return { title, link, thumb };
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
