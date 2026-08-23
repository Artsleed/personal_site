import type { APIRoute } from 'astro';

export const prerender = false;

// Letterboxd's own poster CDN hosts - fetching an arbitrary caller-supplied
// URL server-side is an SSRF/open-proxy risk, so only these are allowed.
const ALLOWED_HOSTS = new Set(['a.ltrbxd.com', 'a.ltrbxd.com.']);

const jsonHeaders = {
  'Content-Type': 'application/json',
  'Cache-Control': 's-maxage=86400, stale-while-revalidate=604800',
};

export const GET: APIRoute = async ({ url }) => {
  const target = url.searchParams.get('url');
  if (!target) {
    return new Response(JSON.stringify({ error: 'Missing url' }), { status: 400, headers: jsonHeaders });
  }

  let parsed: URL;
  try {
    parsed = new URL(target);
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid url' }), { status: 400, headers: jsonHeaders });
  }

  if (parsed.protocol !== 'https:' || !ALLOWED_HOSTS.has(parsed.hostname)) {
    return new Response(JSON.stringify({ error: 'Host not allowed' }), { status: 400, headers: jsonHeaders });
  }

  try {
    const res = await fetch(parsed.toString());
    if (!res.ok) throw new Error(`Upstream responded ${res.status}`);
    const contentType = res.headers.get('content-type') ?? 'image/jpeg';
    const buffer = Buffer.from(await res.arrayBuffer());
    const dataUri = `data:${contentType};base64,${buffer.toString('base64')}`;
    return new Response(JSON.stringify({ dataUri }), { headers: jsonHeaders });
  } catch {
    return new Response(JSON.stringify({ error: 'Could not fetch poster' }), { status: 502, headers: jsonHeaders });
  }
};
