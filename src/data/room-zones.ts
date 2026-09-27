// Zone data for the homepage room, ported from room-handoff/design/hotspots.json
// and room-handoff/prototype/index.html. All px values are in the room's
// fixed 1440x900 artboard space - see RoomHome.astro for how that space is
// scaled to fit the viewport.

export interface RoomZone {
  id: string;
  /** Nav row label */
  navLabel: string;
  /** Card title (Instrument Serif, large) */
  title: string;
  /** Short object name shown as the card eyebrow and in the hotspot's aria-label, e.g. "the corkboard" */
  object: string;
  /** Full page this zone links to */
  route: string;
  /** aria-label for the hotspot button, e.g. "Projects, the corkboard" */
  ariaLabel: string;
  hotspot: { x: number; y: number; w: number; h: number };
  label: {
    text: string;
    left: number;
    top: number;
    arrowPath: string;
  };
  /** Card teaser copy, shown below the title */
  body: string;
  /** Card CTA button label, e.g. "All projects" (arrow added in markup) */
  cta: string;
  /**
   * Which per-zone card shape/material accent to use (see RoomHome.astro's
   * [data-shape] rules) - cards are sized/accented per object rather than
   * one fixed box for all six, without going as far as a literal silhouette
   * cutout (content length varies too much for that to stay robust).
   */
  shape: 'cork' | 'desk' | 'frame' | 'cabinet' | 'shelf' | 'frame-thin';
}

export const roomZones: RoomZone[] = [
  {
    id: 'projects',
    navLabel: 'Projects',
    title: 'Projects',
    object: 'the corkboard',
    route: '/projects',
    ariaLabel: 'Projects, the corkboard',
    hotspot: { x: 559, y: 225, w: 249, h: 157 },
    label: {
      text: 'projects',
      left: 560,
      top: 172,
      arrowPath: 'M618.0 202.0 Q655.2 202.2 682.0 228.0 M673.4 225.2 L682.0 228.0 L678.9 219.6',
    },
    body: 'Every sticky note is a project. Pull one off the board to read the build log.',
    cta: 'All projects',
    shape: 'cork',
  },
  {
    id: 'blog',
    navLabel: 'Writing',
    title: 'Writing',
    object: 'the desk',
    route: '/blog',
    ariaLabel: 'Writing, the desk',
    hotspot: { x: 549, y: 388, w: 285, h: 274 },
    label: {
      text: 'writing',
      left: 668,
      top: 622,
      arrowPath: 'M700.0 620.0 Q690.0 577.6 712.0 540.0 M711.3 549.0 L712.0 540.0 L704.5 545.0',
    },
    body: 'Build logs, notes and half-finished thoughts from the desk.',
    cta: 'All writing',
    shape: 'desk',
  },
  {
    id: 'films',
    navLabel: 'Films',
    title: 'Films',
    object: 'the posters',
    route: '/films',
    ariaLabel: 'Films, the posters',
    hotspot: { x: 1106, y: 162, w: 264, h: 309 },
    label: {
      text: "films I've watched",
      left: 1096,
      top: 116,
      arrowPath: 'M1236.0 146.0 Q1263.6 162.8 1272.0 194.0 M1266.1 187.2 L1272.0 194.0 L1273.7 185.2',
    },
    body: "Pulled live from Letterboxd: the last few things I watched.",
    cta: 'Letterboxd diary',
    shape: 'frame',
  },
  {
    id: 'music',
    navLabel: 'On rotation',
    title: 'On rotation',
    object: 'the record player',
    route: '/music',
    ariaLabel: 'On rotation, the record player',
    hotspot: { x: 981, y: 440, w: 300, h: 366 },
    label: {
      text: 'on rotation',
      left: 1196,
      top: 770,
      arrowPath: 'M1226.0 766.0 Q1162.8 718.2 1150.0 640.0 M1155.2 647.4 L1150.0 640.0 L1147.4 648.6',
    },
    body: "What's on the turntable right now, via Spotify.",
    cta: 'Recently played',
    shape: 'cabinet',
  },
  {
    id: 'about',
    navLabel: 'About',
    title: 'About',
    object: 'the bookshelf',
    route: '/about',
    ariaLabel: 'About, the bookshelf',
    hotspot: { x: 258, y: 198, w: 208, h: 532 },
    label: {
      text: 'about me',
      left: 296,
      top: 768,
      arrowPath: 'M326.0 764.0 Q325.4 730.6 348.0 706.0 M345.4 714.6 L348.0 706.0 L339.6 709.3',
    },
    body: "Second-year Computer Engineering student at Queen's. I work at the Canadian Labour Congress on how AI is changing work, and spend the rest of my time climbing, tinkering with hardware and watching films.",
    cta: 'More about me',
    shape: 'shelf',
  },
  {
    id: 'resume',
    navLabel: 'Resume',
    title: 'Resume',
    object: 'the frame',
    route: '/resume',
    ariaLabel: 'Resume, the frame',
    hotspot: { x: 122, y: 198, w: 148, h: 251 },
    label: {
      text: 'resume',
      left: 118,
      top: 520,
      arrowPath: 'M150.0 518.0 Q152.6 475.2 184.0 446.0 M180.7 454.4 L184.0 446.0 L175.4 448.7',
    },
    body: "One page, kept current. It gets its own lit corner so I can't forget to update it.",
    cta: 'View resume',
    shape: 'frame-thin',
  },
];
