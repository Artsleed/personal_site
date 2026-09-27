// Shared by /api/now-playing.ts (fetched client-side by RoomHome.astro for
// the On rotation card) and music.astro (imports this directly and renders
// server-side, avoiding a redundant HTTP round-trip to its own API route).

const TOKEN_URL = 'https://accounts.spotify.com/api/token';
const CURRENTLY_PLAYING_URL = 'https://api.spotify.com/v1/me/player/currently-playing';
const RECENTLY_PLAYED_URL = 'https://api.spotify.com/v1/me/player/recently-played?limit=1';

export interface NowPlaying {
  isPlaying: boolean;
  title: string;
  artist: string;
  album: string;
  albumArt: string | null;
  songUrl: string;
}

interface SpotifyTrack {
  name: string;
  artists: { name: string }[];
  album: { name: string; images: { url: string }[] };
  external_urls: { spotify: string };
}

function trackToPayload(track: SpotifyTrack, isPlaying: boolean): NowPlaying {
  return {
    isPlaying,
    title: track.name,
    artist: track.artists.map((a) => a.name).join(', '),
    album: track.album.name,
    albumArt: track.album.images[0]?.url ?? null,
    songUrl: track.external_urls.spotify,
  };
}

async function getAccessToken(): Promise<string> {
  const clientId = import.meta.env.SPOTIFY_CLIENT_ID as string;
  const clientSecret = import.meta.env.SPOTIFY_CLIENT_SECRET as string;
  const refreshToken = import.meta.env.SPOTIFY_REFRESH_TOKEN as string;

  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to refresh Spotify access token (${res.status}): ${body}`);
  }

  const data = await res.json();
  return data.access_token as string;
}

// Returns null when nothing playing/recent (not an error - a quiet
// Spotify account), throws only on a real failure (bad credentials, network).
export async function fetchNowPlaying(): Promise<NowPlaying | null> {
  const accessToken = await getAccessToken();

  const nowRes = await fetch(CURRENTLY_PLAYING_URL, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (nowRes.status === 200) {
    const nowData = await nowRes.json();
    if (nowData?.item) {
      return trackToPayload(nowData.item, Boolean(nowData.is_playing));
    }
  }

  const recentRes = await fetch(RECENTLY_PLAYED_URL, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (recentRes.ok) {
    const recentData = await recentRes.json();
    const track = recentData.items?.[0]?.track;
    if (track) return trackToPayload(track, false);
  }

  return null;
}
