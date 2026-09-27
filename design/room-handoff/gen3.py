import json, math
B = '/tmp/claude-0/-home-claude/4bdfed87-4ff7-5d7b-a1e9-ccf0df0d2804/scratchpad/'
svg_body = open(B + 'svg_body.txt').read()
geo = json.load(open(B + 'geo.json'))
spots = geo['spots']

NAMES = {'projects': ('Projects', 'the corkboard'), 'blog': ('Writing', 'the desk'), 'films': ('Films', 'the posters'),
         'music': ('On rotation', 'the record player'), 'about': ('About', 'the bookshelf'), 'resume': ('Resume', 'the frame')}
ORDER = ['projects', 'blog', 'films', 'music', 'about', 'resume']

buttons = ''
for k in ['blog', 'music', 'films', 'about', 'projects', 'resume']:
    x, y, w, h = spots[k]
    buttons += ('<button class="spot" aria-label="%s, %s" onClick="{{go.%s}}" '
                'style="position: absolute; left: %dpx; top: %dpx; width: %dpx; height: %dpx"></button>\n' % (NAMES[k][0], NAMES[k][1], k, x, y, w, h))

# label: (text, left, top, arrow start, arrow end)
L = {
  'projects': ('projects', 560, 172, (618, 202), (682, 228)),
  'blog':     ('writing', 668, 622, (700, 620), (712, 540)),
  'about':    ('about me', 296, 768, (326, 764), (348, 706)),
  'resume':   ('resume', 118, 520, (150, 518), (184, 446)),
  'films':    ('films I’ve watched', 1096, 116, (1236, 146), (1272, 194)),
  'music':    ('on rotation', 1196, 770, (1226, 766), (1150, 640)),
}
labels_html, arrows = '', ''
for k, (txt, tx, ty, (sx, sy), (ex, ey)) in L.items():
    labels_html += '<div class="hand" style="position: absolute; left: %dpx; top: %dpx">%s</div>\n' % (tx, ty, txt)
    cx, cy = (sx + ex) / 2 + (ey - sy) * 0.2, (sy + ey) / 2 - (ex - sx) * 0.2
    ang = math.atan2(ey - cy, ex - cx)
    h1 = (ex - 9 * math.cos(ang - 0.45), ey - 9 * math.sin(ang - 0.45))
    h2 = (ex - 9 * math.cos(ang + 0.45), ey - 9 * math.sin(ang + 0.45))
    arrows += '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f M%.1f %.1f L%.1f %.1f L%.1f %.1f" class="ink"></path>\n' % (sx, sy, cx, cy, ex, ey, *h1, ex, ey, *h2)

nav = ''.join('<button class="navb" onClick="{{go.%s}}">%s</button>' % (k, NAMES[k][0]) for k in ORDER)

P_ = 'style="margin: 0; font-size: 16px; line-height: 1.55; color: #b5bfca; text-wrap: pretty"'
def item(title, meta):
    return ('<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 16px; padding: 12px 0; border-top: 1px solid #243040">'
            '<span style="font-size: 16px; color: #e3ddd2">%s</span><span style="font-size: 13px; color: #8e9aa6">%s</span></div>') % (title, meta)
def list_(*items):
    return '<div style="display: flex; flex-direction: column">' + ''.join(item(*i) for i in items) + '</div>'
def section(k, body, cta):
    name, obj = NAMES[k]
    return ('<sc-if value="{{is.%s}}" hint-placeholder-val="{{ false }}">\n'
            '<div style="display: flex; flex-direction: column; gap: 20px">\n'
            '<button class="back" onClick="{{back}}">← Back to the room</button>\n'
            '<div style="display: flex; flex-direction: column; gap: 6px"><div class="hand" style="font-size: 26px; color: {{accent}}">%s</div>'
            '<h2 style="margin: 0; font-family: \'Instrument Serif\', Georgia, serif; font-weight: 400; font-size: 56px; line-height: 1; color: #efe8dc">%s</h2></div>\n'
            '%s\n<a href="#" class="cta" style="background: {{accent}}">%s</a>\n</div>\n</sc-if>\n') % (k, obj, name, body, cta)

sections = ''
sections += section('projects', '<p %s>Every sticky note is a project. Pull one off the board to read the build log.</p>' % P_ +
    list_(('Magic mirror mk1', 'Raspberry Pi · woodwork'), ('aQuatonomous sim', 'RoboBoat · simulation'), ('Daft Punk helmet', 'build'), ('This website', 'Astro · Vercel')), 'All projects →')
sections += section('blog', '<p %s>Build logs, notes and half-finished thoughts from the desk.</p>' % P_ +
    list_(('[Latest post title]', '[date]'), ('[Previous post title]', '[date]')), 'All writing →')
sections += section('films', '<p %s>Pulled live from Letterboxd: the last four things I watched.</p>' % P_ +
    '<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">' +
    ''.join('<div style="aspect-ratio: 2 / 3; border-radius: 4px; background: #1c2631; border: 1px dashed #334254; display: flex; align-items: flex-end; padding: 8px; font-size: 11px; color: #7d8a97">[poster]</div>' for _ in range(4)) +
    '</div>', 'Letterboxd diary →')
sections += section('music', '<p %s>What’s on the turntable right now, via Spotify.</p>' % P_ +
    '<div style="display: flex; align-items: center; gap: 14px; padding: 14px; border-radius: 10px; background: #18212b"><div style="width: 56px; height: 56px; border-radius: 4px; background: #243140"></div>'
    '<div style="display: flex; flex-direction: column; gap: 4px"><span style="font-size: 16px; color: #e3ddd2">[Track name]</span><span style="font-size: 13px; color: #8e9aa6">[Artist] · now playing</span></div></div>', 'Recently played →')
sections += section('about', '<p %s>Second-year Computer Engineering student at Queen’s in Kingston. I work at the Canadian Labour Congress on how AI is changing work, and spend the rest of my time climbing, tinkering with hardware and watching films.</p>' % P_, 'More about me →')
sections += section('resume', '<p %s>One page, kept current. It gets its own lit corner so I can’t forget to update it.</p>' % P_, 'Download resume (PDF) →')

props = {
    "accent": {"editor": "color", "default": "#ee8a45", "options": ["#ee8a45", "#e0b04f", "#d86a5a", "#7fb0d8"]},
    "labels": {"editor": "boolean", "default": True},
    "open": {"editor": "enum", "default": "projects", "options": ["none"] + ORDER},
    "$preview": {"width": 1440, "height": 900},
}

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Nathaniel’s room</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Hanken+Grotesk:wght@400;500;600&amp;family=Caveat:wght@500;600&amp;display=swap">
<style>
body{margin:0;background:#0d1217;font-family:'Hanken Grotesk',system-ui,sans-serif;color:#e3ddd2}
a{color:#ee8a45}a:hover{color:#f4a56b}
.board{stroke:#1d120a;stroke-width:0.8}
.grain{stroke:#6a4a30;stroke-width:0.6;opacity:0.45}
.lidline{stroke:#56595d;stroke-width:0.6}
.clegh{stroke:#43484e;stroke-width:3;stroke-linecap:round}
.cgash{stroke:#d7dce0;stroke-width:1.8;stroke-linecap:round}
.cstitch{stroke:#34373c;stroke-width:0.8;stroke-dasharray:2 2}
.ring{stroke:#8a7550;stroke-width:0.5}
.caster{fill:none;stroke:#2b2e33;stroke-width:1.4;stroke-linecap:round}
.fringe{stroke:#8a7d68;stroke-width:1;opacity:0.7}
.leafvein{stroke:#6f9272;stroke-width:0.8;opacity:0.5}
.wgrain{stroke:#2a1a10;stroke-width:0.25;opacity:0.5}
.wline{stroke:#6a4a33;stroke-width:0.35;opacity:0.7}
.spkhl{stroke:#4a4c50;stroke-width:1.2;stroke-linecap:round}
.spkring{stroke:#1e1f22;stroke-width:0.9}
.labelring{stroke:#b8612b;stroke-width:0.6}
.tonearmhl{stroke:#eef1f4;stroke-width:0.8;stroke-linecap:round;stroke-linejoin:round;opacity:0.7}
.fingerlift{stroke:#d0d4d8;stroke-width:1.2;stroke-linecap:round}
.pleatline{stroke:#3e2016;stroke-width:0.35;opacity:0.6}
.cleg{stroke:#2e3135;stroke-width:12;stroke-linecap:round}
.cshroud{stroke:#141517;stroke-width:14;stroke-linecap:round}
.cgas{stroke:#a4abb2;stroke-width:7;stroke-linecap:round}
.carm{fill:none;stroke:#2e3135;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}
.cseam{fill:none;stroke:#0d0e10;stroke-width:1.4}
.alexline{stroke:#5b6166;stroke-width:0.35}
.chain{stroke:#d9b560;stroke-width:0.3}
.glint{stroke:#3f9a6a;stroke-width:0.7}
.seam{stroke:#11171e;stroke-width:1.5}
.rugline{stroke:#3a4756;stroke-width:1.5}
.drawer{stroke:#2a2019;stroke-width:1.5}
.thread{stroke:#e8894a;stroke-width:0.5}
.groove{stroke:#1d1d22;stroke-width:1}
.tonearm{stroke:#c9ccd1;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.arm{stroke:#3a414a;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.bulb{fill:#ffd9a8}
.note{font-family:Caveat,cursive;font-size:4.4px;font-weight:600;fill:#2a2420}
.ink{fill:none;stroke:#cdbfa5;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.hand{font-family:Caveat,'Segoe Print',cursive;font-size:26px;font-weight:500;color:#d8cbb3;line-height:1}
.spot{background:transparent;border:0;padding:0;margin:0;cursor:pointer;border-radius:10px;outline:1.5px dashed transparent;outline-offset:2px;transition:outline-color .15s,background-color .15s}
.spot:hover,.spot:focus-visible{outline-color:rgba(238,138,69,.6);background-color:rgba(238,138,69,.05)}
.navb{all:unset;cursor:pointer;font-size:14px;color:#b5bfca;min-height:44px;display:flex;align-items:center}
.navb:hover,.navb:focus-visible{color:#efe8dc}
.scrim{all:unset;position:absolute;left:0;top:0;width:1440px;height:900px;background:rgba(8,11,15,.62);cursor:pointer}
.back{all:unset;cursor:pointer;font-size:14px;color:#8e9aa6;min-height:44px;display:flex;align-items:center;align-self:flex-start}
.back:hover{color:#e3ddd2}
.cta{display:inline-flex;align-self:flex-start;align-items:center;min-height:48px;padding:0 22px;border-radius:999px;color:#171310;font-weight:600;font-size:15px;text-decoration:none}
.cta:hover{color:#171310;filter:brightness(1.08)}
</style>
</helmet>
<div style="position: relative; width: 1440px; height: 900px; overflow: hidden; background: #0d1217">
<svg width="1440" height="900" viewBox="0 0 1440 900" style="position: absolute; left: 0; top: 0" aria-hidden="true">
<defs>
<radialGradient id="glow"><stop offset="0" style="stop-color: {{accent}}; stop-opacity: 0.4"></stop><stop offset="0.45" style="stop-color: {{accent}}; stop-opacity: 0.11"></stop><stop offset="1" style="stop-color: {{accent}}; stop-opacity: 0"></stop></radialGradient>
<linearGradient id="wash" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color: #ffe2b8; stop-opacity: 0.3"></stop><stop offset="1" style="stop-color: #ffe2b8; stop-opacity: 0"></stop></linearGradient>
<radialGradient id="pool"><stop offset="0" style="stop-color: #ffe2b8; stop-opacity: 0.22"></stop><stop offset="1" style="stop-color: #ffe2b8; stop-opacity: 0"></stop></radialGradient>
<linearGradient id="leather" x1="0" y1="0" x2="1" y2="0.25"><stop offset="0" style="stop-color: #141517"></stop><stop offset="0.3" style="stop-color: #2d3035"></stop><stop offset="0.55" style="stop-color: #1e2024"></stop><stop offset="1" style="stop-color: #121315"></stop></linearGradient>
<linearGradient id="pad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" style="stop-color: #1a1b1e"></stop><stop offset="0.5" style="stop-color: #2c2f34"></stop><stop offset="1" style="stop-color: #17181b"></stop></linearGradient>
<radialGradient id="vig" cx="0.5" cy="0.47" r="0.75"><stop offset="0.55" style="stop-color: #000000; stop-opacity: 0"></stop><stop offset="1" style="stop-color: #000000; stop-opacity: 0.45"></stop></radialGradient>
<radialGradient id="cshadow"><stop offset="0" style="stop-color: #000000; stop-opacity: 0.45"></stop><stop offset="1" style="stop-color: #000000; stop-opacity: 0"></stop></radialGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color: #060d19"></stop><stop offset="0.6" style="stop-color: #0f2140"></stop><stop offset="1" style="stop-color: #1c3155"></stop></linearGradient>
<radialGradient id="moonglow"><stop offset="0" style="stop-color: #e9e3cf; stop-opacity: 0.28"></stop><stop offset="1" style="stop-color: #e9e3cf; stop-opacity: 0"></stop></radialGradient>
<radialGradient id="streetglow"><stop offset="0" style="stop-color: #f2b45c; stop-opacity: 0.35"></stop><stop offset="1" style="stop-color: #f2b45c; stop-opacity: 0"></stop></radialGradient>
<linearGradient id="pleatA" x1="0" y1="0" x2="1" y2="0"><stop offset="0" style="stop-color: #5a3223"></stop><stop offset="0.5" style="stop-color: #9a5c42"></stop><stop offset="1" style="stop-color: #5e3526"></stop></linearGradient>
<linearGradient id="pleatB" x1="0" y1="0" x2="1" y2="0"><stop offset="0" style="stop-color: #663a29"></stop><stop offset="0.45" style="stop-color: #8a5139"></stop><stop offset="1" style="stop-color: #542f21"></stop></linearGradient>
</defs>
''' + svg_body + '''
</svg>
<sc-if value="{{labels}}" hint-placeholder-val="{{ true }}">
<svg width="1440" height="900" viewBox="0 0 1440 900" style="position: absolute; left: 0; top: 0; pointer-events: none" aria-hidden="true">
''' + arrows + '''</svg>
''' + labels_html + '''</sc-if>
''' + buttons + '''<header style="position: absolute; left: 56px; top: 36px; right: 56px; display: flex; justify-content: space-between; align-items: center">
<div style="display: flex; flex-direction: column; gap: 4px"><h1 style="margin: 0; font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; font-size: 40px; line-height: 1; color: #efe8dc">Nathaniel</h1><span style="font-size: 14px; color: #8e9aa6">Come in. Everything on the site lives somewhere in this room.</span></div>
<nav aria-label="Sections" style="display: flex; align-items: center; gap: 24px">''' + nav + '''<a href="#" style="font-size: 14px">Plain version</a></nav>
</header>
<sc-if value="{{open}}" hint-placeholder-val="{{ false }}">
<button class="scrim" aria-label="Back to the room" onClick="{{back}}"></button>
<aside style="position: absolute; left: 944px; top: 110px; width: 408px; padding: 36px 40px 40px; border-radius: 18px; background: #111820; border: 1px solid #263241; box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5)">
''' + sections + '''</aside>
</sc-if>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props=\'''' + json.dumps(props, ensure_ascii=False) + '''\'>
class Component extends DCLogic {
  renderVals() {
    const zones = ['projects', 'blog', 'films', 'music', 'about', 'resume'];
    const start = this.props.open ?? 'none';
    const st = this.state || {};
    const sel = st.sel !== undefined ? st.sel : (start === 'none' ? null : start);
    const go = {}, is = {};
    zones.forEach((z) => {
      go[z] = () => this.setState({ sel: z });
      is[z] = sel === z;
    });
    return {
      accent: this.props.accent ?? '#ee8a45',
      labels: (this.props.labels ?? true) && !sel,
      open: !!sel,
      back: () => this.setState({ sel: null }),
      go, is,
    };
  }
}
</script>
</body>
</html>
'''
open(B + 'room/project/Main.dc.html', 'w').write(html)
print(len(html))
