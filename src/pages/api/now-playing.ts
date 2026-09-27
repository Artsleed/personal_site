import type { APIRoute } from 'astro';
import { fetchNowPlaying } from '../../lib/spotify';

export const prerender = false;

// Fetched client-side by RoomHome.astro (the On rotation card, on page load
// and again whenever that card opens - "now playing" goes stale within
// minutes). music.astro imports fetchNowPlaying directly instead of calling
// this route, since it renders server-side and a self-HTTP-call would be a
// redundant round-trip.
export const GET: APIRoute = async () => {
  const jsonHeaders = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store',
  };

  try {
    const track = await fetchNowPlaying();
    return new Response(JSON.stringify(track ?? { isPlaying: false }), { headers: jsonHeaders });
  } catch {
    return new Response(JSON.stringify({ error: 'Could not load Spotify status' }), {
      status: 502,
      headers: jsonHeaders,
    });
  }
};
