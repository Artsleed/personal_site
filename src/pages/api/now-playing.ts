import type { APIRoute } from 'astro';

export const prerender = false;

const TOKEN_URL = 'https://accounts.spotify.com/api/token';
const CURRENTLY_PLAYING_URL = 'https://api.spotify.com/v1/me/player/currently-playing';
const RECENTLY_PLAYED_URL = 'https://api.spotify.com/v1/me/player/recently-played?limit=1';

interface SpotifyTrack {
  name: string;
  artists: { name: string }[];
  album: { name: string; images: { url: string }[] };
  external_urls: { spotify: string };
}

function trackToPayload(track: SpotifyTrack, isPlaying: boolean) {
  return {
    isPlaying,
    title: track.name,
    artist: track.artists.map((a) => a.name).join(', '),
    album: track.album.name,
    albumArt: track.album.images[0]?.url ?? null,
    songUrl: track.external_urls.spotify,
  };
}

async function getAccessToken(env: {
  SPOTIFY_CLIENT_ID: string;
  SPOTIFY_CLIENT_SECRET: string;
  SPOTIFY_REFRESH_TOKEN: string;
}) {
  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization:
        'Basic ' + Buffer.from(`${env.SPOTIFY_CLIENT_ID}:${env.SPOTIFY_CLIENT_SECRET}`).toString('base64'),
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: env.SPOTIFY_REFRESH_TOKEN,
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to refresh Spotify access token (${res.status}): ${body}`);
  }

  const data = await res.json();
  return data.access_token as string;
}

export const GET: APIRoute = async () => {
  const env = {
    SPOTIFY_CLIENT_ID: import.meta.env.SPOTIFY_CLIENT_ID as string,
    SPOTIFY_CLIENT_SECRET: import.meta.env.SPOTIFY_CLIENT_SECRET as string,
    SPOTIFY_REFRESH_TOKEN: import.meta.env.SPOTIFY_REFRESH_TOKEN as string,
  };

  const jsonHeaders = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store',
  };

  try {
    const accessToken = await getAccessToken(env);

    const nowRes = await fetch(CURRENTLY_PLAYING_URL, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (nowRes.status === 200) {
      const nowData = await nowRes.json();
      if (nowData?.item) {
        return new Response(
          JSON.stringify(trackToPayload(nowData.item, Boolean(nowData.is_playing))),
          { headers: jsonHeaders }
        );
      }
    }

    const recentRes = await fetch(RECENTLY_PLAYED_URL, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (recentRes.ok) {
      const recentData = await recentRes.json();
      const track = recentData.items?.[0]?.track;
      if (track) {
        return new Response(JSON.stringify(trackToPayload(track, false)), { headers: jsonHeaders });
      }
    }

    return new Response(JSON.stringify({ isPlaying: false }), { headers: jsonHeaders });
  } catch {
    return new Response(JSON.stringify({ error: 'Could not load Spotify status' }), {
      status: 502,
      headers: jsonHeaders,
    });
  }
};
