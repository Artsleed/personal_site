// @ts-check
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
  adapter: vercel(),
  redirects: {
    // The old Now page (Letterboxd diary + music) was retired when the site
    // moved to the room concept - its content now lives on /films and /music.
    '/now': '/films',
  },
});
