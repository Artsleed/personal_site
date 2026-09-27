import type { APIRoute } from 'astro';
import { fetchLetterboxdFilms } from '../../lib/letterboxd';

export const prerender = false;

// Fetched client-side by RoomHome.astro (the two frame posters + the Films
// card's poster grid on the homepage). films.astro imports fetchLetterboxdFilms
// directly instead of calling this route, since it renders server-side and
// a self-HTTP-call would be a redundant round-trip. Posters are plain CDN
// URLs, not base64 - a.ltrbxd.com allows direct hotlinking (confirmed), and
// a plain <img> never hits the CORS restriction that made the old three.js
// canvas-texture version need a server-side proxy in the first place.
export const GET: APIRoute = async () => {
  const jsonHeaders = {
    'Content-Type': 'application/json',
    'Cache-Control': 's-maxage=1800, stale-while-revalidate=3600',
  };

  try {
    const films = await fetchLetterboxdFilms();
    return new Response(JSON.stringify({ films }), { headers: jsonHeaders });
  } catch {
    return new Response(JSON.stringify({ films: [], error: 'Could not load Letterboxd feed' }), {
      status: 502,
      headers: jsonHeaders,
    });
  }
};
