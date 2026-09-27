import math, json

F, CX, CY, EYE = 737.0, 720.0, 360.0, 1.45
D, HW, H = 4.2, 1.8, 2.6
CAM = (0.0, EYE, 0.0)

def pr(x, y, z):
    return (CX + F * x / z, CY - F * (y - EYE) / z)

def hx(h):
    h = h.lstrip('#'); return [int(h[i:i+2], 16) for i in (0, 2, 4)]
def shade(h, f):
    r = hx(h)
    r = [v + (255 - v) * f for v in r] if f >= 0 else [v * (1 + f) for v in r]
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in r)

out, groups, cur = [], {}, [None]
def track(pts):
    if cur[0]: groups.setdefault(cur[0], []).extend(pts)
def spoly(pts, fill, extra=''):
    track(pts)
    out.append('<polygon points="%s" fill="%s"%s></polygon>' % (' '.join('%.1f,%.1f' % p for p in pts), fill, extra))
def poly3(pts3, fill, extra=''):
    spoly([pr(*p) for p in pts3], fill, extra)

def box(x0, y0, z0, dx, dy, dz, col):
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    faces = [
        ((0, 1, 0), [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)], shade(col, 0.16)),
        ((0, -1, 0), [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)], shade(col, -0.4)),
        ((0, 0, -1), [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)], col),
        ((-1, 0, 0), [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)], shade(col, -0.2)),
        ((1, 0, 0), [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)], shade(col, -0.2)),
    ]
    for n, pts, c in faces:
        p = pts[0]
        if n[0]*(CAM[0]-p[0]) + n[1]*(CAM[1]-p[1]) + n[2]*(CAM[2]-p[2]) > 0:
            poly3(pts, c)

def front(x0, ytop, z):
    """affine group for a plane facing the camera: local units = cm, y down"""
    e, f = pr(x0, ytop, z); k = F / z / 100
    return 'translate(%.1f %.1f) scale(%.4f)' % (e, f, k)
def bevel_svg(x0, y0, x1, y1, b, fill, lt, dk):
    """recessed panel in a camera-facing local plane (cm): lit top/left bevel, shaded bottom/right"""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"></rect>' % (x0, y0, x1 - x0, y1 - y0, fill) +
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"></polygon>' % (x0, y0, x1, y0, x1 - b, y0 + b, x0 + b, y0 + b, dk) +
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"></polygon>' % (x0, y0, x0 + b, y0 + b, x0 + b, y1 - b, x0, y1, dk) +
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"></polygon>' % (x0, y1, x0 + b, y1 - b, x1 - b, y1 - b, x1, y1, lt) +
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"></polygon>' % (x1, y0, x1, y1, x1 - b, y1 - b, x1 - b, y0 + b, lt))
def side_bevel(xw, z0, z1, y0, y1, b, fill, lt, dk):
    """recessed panel on a side-wall-parallel plane (x = xw), z across, y up"""
    side(xw, [(z0, y0), (z1, y0), (z1, y1), (z0, y1)], fill)
    side(xw - 0.0005, [(z0, y1), (z1, y1), (z1 - b, y1 - b), (z0 + b, y1 - b)], dk)     # top edge in shadow
    side(xw - 0.0005, [(z0, y0), (z0 + b, y0 + b), (z0 + b, y1 - b), (z0, y1)], dk)     # near edge
    side(xw - 0.0005, [(z0, y0), (z1, y0), (z1 - b, y0 + b), (z0 + b, y0 + b)], lt)     # bottom edge catches light
    side(xw - 0.0005, [(z1, y0), (z1, y1), (z1 - b, y1 - b), (z1 - b, y0 + b)], lt)     # far edge
def g(t, body): out.append('<g transform="%s">%s</g>' % (t, body))

def side(xw, pts, fill, extra=''):   # pts in (z, y) on wall plane x = xw
    poly3([(xw, y, z) for z, y in pts], fill, extra)
def side_rect(xw, z0, z1, y0, y1, fill, extra=''):
    side(xw, [(z0,y0),(z1,y0),(z1,y1),(z0,y1)], fill, extra)
def side_circle(xw, zc, yc, r, fill):
    side(xw, [(zc + r*math.cos(t*math.pi/12), yc + r*math.sin(t*math.pi/12)) for t in range(24)], fill)
def top_circle(y, xc, zc, r, fill, extra=''):
    poly3([(xc + r*math.cos(t*math.pi/16), y, zc + r*math.sin(t*math.pi/16)) for t in range(32)], fill, extra)

NEAR = 1.0
# ---------- shell ----------
poly3([(-HW,H,NEAR),(HW,H,NEAR),(HW,H,D),(-HW,H,D)], '#141a22')                  # ceiling
import random
random.seed(7)
WOODS = ['#3d281a', '#452d1c', '#4c3220', '#37241a', '#41291a', '#503523', '#3a2517']
poly3([(-HW,0,NEAR),(HW,0,NEAR),(HW,0,D),(-HW,0,D)], '#2a1a10')                  # floor base (gaps)
BW = 0.15
nb_ = int(round(2 * HW / BW))
for i in range(nb_):
    x0 = -HW + i * BW; x1 = x0 + BW
    z = NEAR - random.uniform(0, 1.2)
    while z < D:
        z1 = min(D, z + random.uniform(0.9, 1.9))
        za = max(z, NEAR)
        if z1 > za:
            poly3([(x0,0,za),(x1,0,za),(x1,0,z1),(x0,0,z1)], random.choice(WOODS), ' class="board"')
            # grain streak
            gx = x0 + random.uniform(0.04, 0.11)
            a, b = pr(gx, 0.0005, max(za, NEAR) + 0.05), pr(gx + random.uniform(-0.01, 0.01), 0.0005, z1 - 0.05)
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="grain"></line>' % (*a, *b))
        z = z1
poly3([(-HW,0,D),(HW,0,D),(HW,H,D),(-HW,H,D)], '#26323f')                         # back wall
poly3([(-HW,0,NEAR),(-HW,0,D),(-HW,H,D),(-HW,H,NEAR)], '#1e2833')               # left wall
poly3([(HW,0,NEAR),(HW,0,D),(HW,H,D),(HW,H,NEAR)], '#212c38')                   # right wall
# corner seams + baseboards
for a, b in [((-HW,0,D),(-HW,H,D)), ((HW,0,D),(HW,H,D))]:
    p, q = pr(*a), pr(*b)
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="seam"></line>' % (*p, *q))
poly3([(-HW,0,D-0.01),(HW,0,D-0.01),(HW,0.1,D-0.01),(-HW,0.1,D-0.01)], '#303d4b')
side(-HW+0.005, [(NEAR,0),(D,0),(D,0.1),(NEAR,0.1)], '#29343f')
side(HW-0.005, [(NEAR,0),(D,0),(D,0.1),(NEAR,0.1)], '#2b3643')
# crown molding where walls meet the ceiling
poly3([(-HW,H-0.07,D-0.01),(HW,H-0.07,D-0.01),(HW,H,D-0.01),(-HW,H,D-0.01)], '#2e3a48')
side(-HW+0.005, [(NEAR,H-0.07),(D,H-0.07),(D,H),(NEAR,H)], '#27323e')
side(HW-0.005, [(NEAR,H-0.07),(D,H-0.07),(D,H),(NEAR,H)], '#29343f')
for a_, b_ in [((-HW,H-0.07,D-0.011),(HW,H-0.07,D-0.011))]:
    p_, q_ = pr(*a_), pr(*b_)
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="seam"></line>' % (*p_, *q_))
# rug + window spill
poly3([(-1.25,0.003,2.5),(1.05,0.003,2.5),(1.05,0.003,3.5),(-1.25,0.003,3.5)], '#29343f')
poly3([(-1.13,0.004,2.6),(0.93,0.004,2.6),(0.93,0.004,3.4),(-1.13,0.004,3.4)], '#6b3d2c')
poly3([(-1.08,0.005,2.65),(0.88,0.005,2.65),(0.88,0.005,3.35),(-1.08,0.005,3.35)], '#243039')
poly3([(-0.98,0.006,2.75),(0.78,0.006,2.75),(0.78,0.006,3.25),(-0.98,0.006,3.25)], 'none', ' class="rugline"')
poly3([(-0.1,0.006,2.84),(0.18,0.006,3.0),(-0.1,0.006,3.16),(-0.38,0.006,3.0)], 'none', ' class="rugline"')
for i in range(47):
    fx = -1.23 + i * 0.049
    a_, b_ = pr(fx, 0.004, 2.5), pr(fx, 0.004, 2.46)
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="fringe"></line>' % (*a_, *b_))
def contact(x0, x1, z0, z1, k=1.0):
    for e, o in [(0.1, 0.1), (0.05, 0.14), (0.015, 0.18)]:
        poly3([(x0-e,0.007,z0-e),(x1+e,0.007,z0-e),(x1+e,0.007,z1+e),(x0-e,0.007,z1+e)], '#000000', ' opacity="%.2f"' % (o * k))
contact(-0.8, 0.52, 3.62, 4.2, 0.9)          # desk
contact(-1.8, -1.48, 2.95, 4.05)             # bookcase
contact(1.35, 1.8, 2.4, 3.7)                 # cabinet
poly3([(0.7,0.005,4.15),(1.6,0.005,4.15),(1.4,0.005,3.1),(0.3,0.005,3.1)], '#8fb4e0', ' opacity="0.05"')

def curtains():
    """two gathered rust-linen panels: shaded pleats that flare toward the hem, header tape, rings (window-local cm)"""
    svg = ''
    for x0, w, n in [(-20, 22, 5), (80, 26, 6)]:
        # soft shadow the panel casts on the wall
        svg += '<rect x="%.1f" y="-6" width="%.1f" height="136" rx="3" fill="#000000" opacity="0.16"></rect>' % (x0 + 1.5, w)
        pw, cx = w / n, x0 + w / 2
        for i in range(n):
            xa, xb = x0 + i * pw, x0 + (i + 1) * pw
            fa, fb = cx + (xa - cx) * 1.1, cx + (xb - cx) * 1.1           # flare at the hem
            hem = 136 + (2.2 if i % 2 else -0.8)
            grad = 'url(#pleatA)' if i % 2 == 0 else 'url(#pleatB)'
            svg += ('<path d="M%.1f -7 L%.2f -7 C%.2f 40 %.2f 90 %.2f %.1f Q%.2f %.1f %.2f %.1f C%.2f 90 %.2f 40 %.1f -7 Z" fill="%s"></path>' %
                    (xa, xb + 0.2, xb + 0.2, fb + 0.2, fb + 0.2, hem, (fa + fb) / 2, hem + 2.6, fa, hem, fa, xa, xa, grad))
            svg += ('<path d="M%.2f -7 C%.2f 40 %.2f 90 %.2f %.1f" fill="none" class="pleatline"></path>' % (xb, xb, fb, fb, hem))
        # header tape + hem band
        svg += '<rect x="%.1f" y="-7.2" width="%.1f" height="4" fill="#5a3223" opacity="0.9"></rect>' % (x0, w)
        svg += '<rect x="%.1f" y="-3.4" width="%.1f" height="0.5" fill="#000000" opacity="0.25"></rect>' % (x0, w)
        for i in range(n + 1):
            svg += '<circle cx="%.1f" cy="-8.6" r="1.25" fill="none" class="ring"></circle>' % (x0 + i * pw)
    return svg

def window_view():
    """night view: gradient sky, stars, crescent moon with halo, wisps of cloud, layered skyline, treeline"""
    rng = random.Random(21)
    v = '<rect x="4" y="4" width="78" height="113" fill="url(#sky)"></rect>'
    for _ in range(34):
        x_, y_ = rng.uniform(5, 81), rng.uniform(5, 70)
        v += '<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#dfe6f2" opacity="%.2f"></circle>' % (x_, y_, rng.uniform(0.25, 0.7), rng.uniform(0.35, 0.95))
    v += '<circle cx="60" cy="24" r="20" fill="url(#moonglow)"></circle>'
    v += '<path d="M60,17 A7,7 0 1 1 60,31 A5.6,7 0 1 0 60,17 Z" fill="#ece5cf"></path>'
    for cx_, cy_, rx_, ry_, o in [(30, 30, 16, 1.6, 0.18), (44, 34, 11, 1.2, 0.14), (70, 44, 13, 1.4, 0.12), (18, 52, 10, 1.1, 0.1)]:
        v += '<ellipse cx="%d" cy="%d" rx="%d" ry="%.1f" fill="#8aa0c4" opacity="%.2f"></ellipse>' % (cx_, cy_, rx_, ry_, o)
    # far skyline
    x_ = 4.0
    far = ''
    while x_ < 82:
        w_ = rng.uniform(3, 7); h_ = rng.uniform(6, 16)
        far += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"></rect>' % (x_, 92 - h_, min(w_ + 0.2, 82 - x_), 117 - (92 - h_))
        x_ += w_
    v += '<g fill="#14223a">%s</g>' % far
    v += '<rect x="21" y="62" width="1.4" height="20" fill="#14223a"></rect><circle cx="21.7" cy="61.6" r="0.7" fill="#ff5a4a"></circle>'
    v += '<circle cx="21.7" cy="61.6" r="2.4" fill="#ff5a4a" opacity="0.18"></circle>'
    # nearer blocks with lit windows
    x_ = 3.0
    mid, lit = '', ''
    while x_ < 82:
        w_ = rng.uniform(7, 13); top = rng.uniform(80, 92)
        mid += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"></rect>' % (max(x_, 4), top, min(w_, 82 - max(x_, 4)), 117 - top)
        yy = top + 2.5
        while yy < 110:
            xx = x_ + 1.4
            while xx < x_ + w_ - 1.6:
                r_ = rng.random()
                if r_ < 0.2:
                    lit += '<rect x="%.1f" y="%.1f" width="1.3" height="1.7" fill="%s" opacity="%.2f"></rect>' % (xx, yy, rng.choice(['#e8a45c', '#f2c27a', '#f5d9a0', '#9fc3e8']), rng.uniform(0.6, 1))
                xx += 2.6
            yy += 3.6
        x_ += w_ + rng.uniform(0.5, 2)
    v += '<g fill="#0b1422">%s</g>' % mid + lit
    # treeline + streetlight glow
    v += '<circle cx="66" cy="114" r="10" fill="url(#streetglow)"></circle>'
    tree = 'M4,117 L4,108 '
    x_ = 4.0
    while x_ < 82:
        r_ = rng.uniform(2.5, 5)
        tree += 'Q%.1f,%.1f %.1f,%.1f ' % (x_ + r_, 108 - rng.uniform(3, 8), min(82, x_ + 2 * r_), 108 - rng.uniform(0, 2))
        x_ += 2 * r_
    tree += 'L82,117 Z'
    v += '<path d="%s" fill="#060b13"></path>' % tree
    # faint reflections on the glass
    v += '<polygon points="8,4 20,4 6,40 4,40 4,14" fill="#ffffff" opacity="0.035"></polygon>'
    v += '<polygon points="48,62 56,62 46,90 45,90 45,70" fill="#ffffff" opacity="0.03"></polygon>'
    return v

# ---------- back wall: window ----------
g(front(0.72, 2.18, D - 0.005),
  window_view()
  # frame: outer casing, inner shadow, mullions with a lit edge, meeting-rail latch, sill
  + '<path d="M0,0 H86 V121 H0 Z M4,4 V117 H82 V4 Z" fill="#3b4a5b" fill-rule="evenodd"></path>'
  + '<rect x="-3" y="-3" width="92" height="3" fill="#44546a"></rect><rect x="-3" y="0" width="3" height="121" fill="#44546a"></rect><rect x="86" y="0" width="3" height="121" fill="#35434f"></rect>'
  + '<rect x="4" y="4" width="78" height="1.2" fill="#000000" opacity="0.35"></rect><rect x="4" y="4" width="1.2" height="113" fill="#000000" opacity="0.25"></rect>'
  + '<rect x="41" y="4" width="4" height="113" fill="#3b4a5b"></rect><rect x="41" y="4" width="0.7" height="113" fill="#51637a"></rect>'
  + '<rect x="4" y="58" width="78" height="4" fill="#3b4a5b"></rect><rect x="4" y="58" width="78" height="0.7" fill="#51637a"></rect>'
  + '<rect x="39.5" y="56.6" width="7" height="2" rx="0.6" fill="#8d949b"></rect>'
  + '<rect x="-6" y="121" width="98" height="4" fill="#4a5a6e"></rect><rect x="-6" y="121" width="98" height="0.8" fill="#5d6f86"></rect><rect x="-4" y="125" width="94" height="1.6" fill="#2c3744"></rect>'
  + curtains() + '<rect x="-24" y="-11" width="130" height="2.2" rx="1.1" fill="#6b5a3e"></rect><rect x="-24" y="-11" width="130" height="0.6" fill="#9a8762"></rect><circle cx="-24" cy="-9.9" r="2.4" fill="#8a7550"></circle><circle cx="106" cy="-9.9" r="2.4" fill="#8a7550"></circle>'
  + '<rect x="-14" y="-12" width="1.4" height="5" fill="#6b5a3e"></rect><rect x="96" y="-12" width="1.4" height="5" fill="#6b5a3e"></rect>')

# ---------- back wall: corkboard (PROJECTS) ----------
cur[0] = 'projects'
Zc = D - 0.02
notes = [(10,9,'#d9b45a','mirror mk1',-4),(40,15,'#9fb58f','roboboat',3),(70,7,'#e8894a','helmet',-2),
         (100,13,'#d49a8f','this site',4),(126,34,'#9bb7c9','next?',-3),(24,52,'#d9b45a','',2),(62,48,'#9fb58f','',-3)]
nb = ''
for x, y, col, txt, rot in notes:
    cx, cy = x + 10, y + 10
    nb += '<g transform="rotate(%d %d %d)"><rect x="%d" y="%d" width="20" height="20" fill="%s"></rect>' % (rot, cx, cy, x, y, col)
    nb += '<rect x="%.1f" y="%d" width="12" height="0.7" fill="#00000030"></rect><rect x="%.1f" y="%d" width="9" height="0.7" fill="#00000030"></rect>' % (x+2, y+13, x+2, y+15.5)
    nb += '<circle cx="%d" cy="%.1f" r="1.3" fill="#b8453a"></circle></g>' % (cx, y + 2)
g(front(-0.87, 2.17, Zc),
  '<rect x="0" y="0" width="132" height="80" fill="#5e432e"></rect>'
  '<rect x="3.5" y="3.5" width="125" height="73" fill="#8d6b4a"></rect>'
  '<g transform="translate(1 0) scale(0.84 0.86)">' + nb +
  '<polyline points="20,11 50,17 80,9 110,15 136,36" fill="none" class="thread"></polyline></g>')
groups.setdefault('projects', []).extend([pr(-0.87, 2.17, Zc), pr(0.45, 1.37, Zc)])
cur[0] = None

# ---------- desk (WRITING): ALEX desk, dark grey, 132 x 58 x 76 ----------
cur[0] = 'blog'
DG = '#46494c'
ST = '#34373a'
DX0, DX1, DZ0, DZ1 = -0.8, 0.52, 3.62, 4.2
# steel frame: back legs, back + side stretchers low down, then front legs
for lx in (DX0 + 0.01, DX1 - 0.04):
    box(lx, 0, DZ1 - 0.05, 0.03, 0.6, 0.03, ST)
box(DX0 + 0.04, 0.12, DZ1 - 0.045, DX1 - DX0 - 0.08, 0.02, 0.02, ST)          # back stretcher
for lx in (DX0 + 0.015, DX1 - 0.035):
    box(lx, 0.12, DZ0 + 0.04, 0.02, 0.02, DZ1 - DZ0 - 0.09, ST)            # side stretchers
for lx in (DX0 + 0.01, DX1 - 0.04):
    box(lx, 0, DZ0 + 0.01, 0.03, 0.6, 0.03, ST)                            # front legs
box(DX0, 0.585, DZ0, DX1 - DX0, 0.015, DZ1 - DZ0, ST)                      # steel rim under the box
box(DX0, 0.6, DZ0, DX1 - DX0, 0.16, DZ1 - DZ0, DG)                         # drawer box + top
g(front(DX0, 0.76, DZ0 - 0.001),
  '<rect x="0" y="2.2" width="132" height="0.4" fill="#2d3033"></rect>'
  '<rect x="1" y="3.4" width="64.6" height="11.8" fill="none" class="alexline"></rect>'
  '<rect x="66.4" y="3.4" width="64.6" height="11.8" fill="none" class="alexline"></rect>'
  + ''.join('<path d="M%.1f,3.4 C%.1f,3.4 %.1f,6.4 %.1f,6.4 L%.1f,6.4 C%.1f,6.4 %.1f,3.4 %.1f,3.4 Z" fill="#1c1e20"></path>' %
            (c - 13, c - 9, c - 8, c - 4, c + 4, c + 8, c + 9, c + 13) for c in (33.3, 98.7)))
# lift-up lid with cable slot at the back of the top
poly3([(-0.35, 0.7605, 3.96), (0.3, 0.7605, 3.96), (0.3, 0.7605, 4.17), (-0.35, 0.7605, 4.17)], 'none', ' class="lidline"')
poly3([(-0.2, 0.7606, 4.12), (0.15, 0.7606, 4.12), (0.15, 0.7606, 4.14), (-0.2, 0.7606, 4.14)], '#45484c')
# monitor
box(-0.24, 0.76, 3.95, 0.2, 0.012, 0.14, '#23262a')
box(-0.16, 0.772, 4.06, 0.04, 0.16, 0.02, '#23262a')
box(-0.44, 0.9, 4.08, 0.6, 0.35, 0.025, '#1a1c1f')
g(front(-0.425, 1.24, 4.079),
  '<rect x="0" y="0" width="57" height="32" fill="#12202e"></rect>'
  '<rect x="0" y="0" width="10" height="32" fill="#0e1a26"></rect>'
  + ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="1.1" fill="%s"></rect>' % r for r in
            [(2,3,5,'#6f8aa6'),(2,5.5,6,'#6f8aa6'),(2,8,4,'#6f8aa6'),
             (13,3,10,'#e8894a'),(13,6,28,'#6f8aa6'),(16,9,20,'#6f8aa6'),(16,12,14,'#9fb58f'),(19,15,24,'#6f8aa6'),(16,18,9,'#d9b45a'),(13,21,18,'#6f8aa6'),(13,24,30,'#6f8aa6'),(16,27,12,'#9fb58f')]))
# keyboard, mouse, notebook, mug
box(-0.36, 0.76, 3.72, 0.42, 0.015, 0.13, '#8e97a1')
box(0.1, 0.76, 3.7, 0.06, 0.02, 0.1, '#8e97a1')
poly3([(-0.76, 0.7605, 3.7), (-0.54, 0.7605, 3.7), (-0.54, 0.7605, 3.98), (-0.76, 0.7605, 3.98)], '#b8733f')
box(-0.72, 0.76, 4.02, 0.08, 0.1, 0.08, '#c9c1b2')
# banker's lamp: green glass shade, brass stem and base, turned ~25 degrees toward the room
LZ = 3.92
LTH = math.radians(-35)   # shade turned to face the monitor
def rot_mat(xo, yt, zo, ax, az):
    p0 = pr(xo, yt, zo); px = pr(xo + 0.01 * ax, yt, zo + 0.01 * az); py = pr(xo, yt - 0.01, zo)
    return 'matrix(%.4f,%.4f,%.4f,%.4f,%.1f,%.1f)' % (px[0]-p0[0], px[1]-p0[1], py[0]-p0[0], py[1]-p0[1], p0[0], p0[1])
LCX = 0.335
LX0, LZ0 = LCX - 0.18 * math.cos(LTH), LZ - 0.18 * math.sin(LTH)
# visible end cap of the half-cylinder shade (drawn first, sits at the shade's near end)
g(rot_mat(LX0 + 0.36 * math.cos(LTH), 1.16, LZ0 + 0.36 * math.sin(LTH), -math.sin(LTH), math.cos(LTH)),
  '<path d="M-5.5,11 C-5.5,3 -3,0 0,0 C3,0 5.5,3 5.5,11 Z" fill="#0f3f28"></path>'
  '<rect x="-5.5" y="10.2" width="11" height="1.3" fill="#a9822f"></rect>')
g(rot_mat(LX0, 1.16, LZ0, math.cos(LTH), math.sin(LTH)),
  '<rect x="8" y="33" width="20" height="7" rx="3" fill="#a9822f"></rect>'
  '<rect x="9" y="33" width="18" height="1.4" rx="0.7" fill="#e3c26d"></rect>'
  '<rect x="16.8" y="9" width="2.4" height="25" fill="#b8903f"></rect>'
  '<rect x="17.5" y="9" width="0.7" height="25" fill="#e3c26d"></rect>'
  '<line x1="27" y1="11.5" x2="27" y2="21" class="chain"></line><circle cx="27" cy="21.6" r="0.9" fill="#e3c26d"></circle>'
  '<path d="M0.5,11 C0.5,3.5 6,0 18,0 C30,0 35.5,3.5 35.5,11 Z" fill="#17583a"></path>'
  '<path d="M4,6.5 C7,3 12,2 18,2 C24,2 29,3 32,6.5" fill="none" class="glint"></path>'
  '<rect x="0" y="10.2" width="36" height="1.3" fill="#c9a24a"></rect>'
  '<ellipse cx="18" cy="11.9" rx="15.5" ry="1.3" fill="#ffe0b0"></ellipse>')
groups['blog'] += [pr(LX0, 1.16, LZ0), pr(LCX + 0.18, 0.76, LZ), pr(-0.44, 1.25, 4.08)]
LAMP = pr(0.335, 1.03, LZ)
cur[0] = None

# ---------- executive chair: pulled out and swivelled toward the room ----------
def obox(cx, cz, yaw, lx0, lx1, y0, y1, lz0, lz1, col):
    c, s_ = math.cos(yaw), math.sin(yaw)
    def W(lx, lz): return (cx + lx * c - lz * s_, cz + lx * s_ + lz * c)
    def P3(lx, y, lz):
        x, z = W(lx, lz); return (x, y, z)
    faces = [
        ((0,1,0), [P3(lx0,y1,lz0),P3(lx1,y1,lz0),P3(lx1,y1,lz1),P3(lx0,y1,lz1)], shade(col, 0.18)),
        ((0,-1,0), [P3(lx0,y0,lz0),P3(lx1,y0,lz0),P3(lx1,y0,lz1),P3(lx0,y0,lz1)], shade(col, -0.4)),
    ]
    for nl, pts, f in [((0,-1), [(lx0,lz0),(lx1,lz0)], 0.0), ((0,1), [(lx1,lz1),(lx0,lz1)], -0.25),
                       ((-1,0), [(lx0,lz1),(lx0,lz0)], -0.12), ((1,0), [(lx1,lz0),(lx1,lz1)], -0.12)]:
        n = (nl[0]*c - nl[1]*s_, 0, nl[0]*s_ + nl[1]*c)
        (a1, b1), (a2, b2) = pts
        faces.append((n, [P3(a1,y0,b1),P3(a2,y0,b2),P3(a2,y1,b2),P3(a1,y1,b1)], shade(col, f)))
    for n, pts, colr in faces:
        p = pts[0]
        if n[0]*(CAM[0]-p[0]) + n[1]*(CAM[1]-p[1]) + n[2]*(CAM[2]-p[2]) > 0:
            poly3(pts, colr)
# ---------- left wall: traditional bookcase (ABOUT) ----------
cur[0] = 'about'
XL = -HW
WD = '#3f3228'   # same wood as the cabinet
Z0, Z1, DP, TOP = 2.95, 4.05, 0.32, 2.0
side_rect(XL + 0.004, Z0, Z1, 0, TOP, '#1c1611')                         # inside back
box(XL, 0, Z1 - 0.025, DP, TOP, 0.025, WD)                               # far side
box(XL, 0, Z0, DP + 0.01, 0.08, Z1 - Z0, shade(WD, -0.1))                # plinth
BOOKC = ['#7a4f3a','#4f6a74','#b08d57','#5b5566','#3f5a4a','#8a6f55','#6e3b34','#2f4658','#9c8a64','#54433a','#8a4a3a','#44584f']
rnd = random.Random(11)
levels = [0.08, 0.48, 0.88, 1.28]
for li, ys in enumerate(levels):
    if li:
        box(XL, ys - 0.025, Z0 + 0.02, DP, 0.025, Z1 - Z0 - 0.045, WD)
    z = Z1 - 0.03
    items = []
    while z > Z0 + 0.06:
        r = rnd.random()
        if r < 0.08 and li != 0:
            z -= rnd.uniform(0.08, 0.14); continue          # gap
        if r < 0.16 and z - 0.3 > Z0 + 0.04:
            # flat stack
            yy = ys
            for _ in range(rnd.randint(2, 4)):
                h = rnd.uniform(0.03, 0.05)
                items.append((XL + 0.03, yy, z - 0.26, 0.22, h, 0.24, rnd.choice(BOOKC))); yy += h
            z -= 0.3; continue
        th, h = rnd.uniform(0.022, 0.05), rnd.uniform(0.2, 0.33)
        if z - th < Z0 + 0.03: break
        items.append((XL + 0.02 + rnd.uniform(0, 0.03), ys, z - th, rnd.uniform(0.19, 0.24), h, th, rnd.choice(BOOKC)))
        z -= th + 0.004
    for x0, y0, z0, dx, dy, dz, col in items:
        box(x0, y0, z0, dx, dy, dz, col)
# top shelf: frame, plant, a few books
box(XL, 1.655, Z0 + 0.02, DP, 0.025, Z1 - Z0 - 0.045, WD)
for zz, th, h, col in [(3.95, 0.04, 0.26, '#6e3b34'), (3.905, 0.035, 0.24, '#2f4658'), (3.865, 0.045, 0.27, '#9c8a64')]:
    box(XL + 0.03, 1.68, zz - th, 0.2, h, th, col)
box(XL + 0.06, 1.68, 3.4, 0.02, 0.2, 0.26, '#2b2724')
side(XL + 0.082, [(3.42, 1.70), (3.64, 1.70), (3.64, 1.86), (3.42, 1.86)], '#9fb3c4')
side(XL + 0.083, [(3.42, 1.70), (3.64, 1.70), (3.56, 1.80), (3.51, 1.75), (3.46, 1.78)], '#5b6b5e')
box(XL + 0.08, 1.68, 3.06, 0.13, 0.11, 0.13, '#8a5a44')
px, py = pr(XL + 0.145, 1.8, 3.125)
s = F / 3.125 / 100
for dx, dy, r, rot in [(-3,-2,4,-35),(3,-3,4,25),(0,-6,3.5,0),(5,0,3,55),(-5,1,3,-65)]:
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" transform="rotate(%d %.1f %.1f)" fill="#56765e"></ellipse>' % (px+dx*s, py+dy*s, r*s, r*s*0.45, rot, px+dx*s, py+dy*s))
box(XL, TOP, Z0 - 0.03, DP + 0.04, 0.06, Z1 - Z0 + 0.03, shade(WD, 0.05))  # crown
box(XL, 0, Z0, DP, TOP, 0.025, shade(WD, 0.06))                          # near side
FC = shade(WD, 0.06)
grain = ''.join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="wgrain"></line>' % (gx, gy0, gx + 0.4, gy1)
                for gx, gy0, gy1 in [(9, 18, 90), (13.5, 20, 88), (19, 17, 91), (23.5, 22, 89), (10, 110, 180), (15, 108, 182), (21, 112, 179), (24.5, 109, 181)])
g(front(XL, TOP, Z0 - 0.001),
  '<rect x="0" y="0" width="32" height="3" fill="#00000040"></rect>'
  + bevel_svg(4.5, 14, 27.5, 94, 2.2, shade(FC, -0.1), shade(FC, 0.14), shade(FC, -0.35))
  + bevel_svg(4.5, 104, 27.5, 184, 2.2, shade(FC, -0.1), shade(FC, 0.14), shade(FC, -0.35))
  + '<rect x="7.2" y="16.7" width="17.6" height="74.6" fill="none" class="wline"></rect>'
  + '<rect x="7.2" y="106.7" width="17.6" height="74.6" fill="none" class="wline"></rect>'
  + grain
  + '<rect x="0" y="99" width="32" height="0.6" fill="%s"></rect>' % shade(FC, 0.1)
  + '<rect x="0" y="192" width="32" height="8" fill="%s"></rect>' % shade(FC, -0.15))
cur[0] = None
# ---------- chair: beside the bookcase, turned away; smooth sampled outlines ----------
CHX, CHZ, YAW = -0.74, 3.3, math.radians(155)
_c, _s = math.cos(YAW), math.sin(YAW)
_h = pr(CHX, 0.0, CHZ)
out.append('<ellipse cx="%.1f" cy="%.1f" rx="95" ry="20" fill="url(#cshadow)"></ellipse>' % _h)
def CP(lx, y, lz):
    return pr(CHX + lx * _c - lz * _s, y, CHZ + lx * _s + lz * _c)
def rrect(a0, a1, b0, b1, rb, rt, n=7):
    """rounded rect outline (a across, b along), bottom radius rb, top radius rt"""
    pts = []
    for cx_, cy_, r, t0 in [(a1 - rb, b0 + rb, rb, -90), (a1 - rt, b1 - rt, rt, 0), (a0 + rt, b1 - rt, rt, 90), (a0 + rb, b0 + rb, rb, 180)]:
        for k in range(n + 1):
            t = math.radians(t0 + 90 * k / n)
            pts.append((cx_ + r * math.cos(t), cy_ + r * math.sin(t)))
    return pts
def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p_ in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p_) <= 0: lo.pop()
        lo.append(p_)
    for p_ in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p_) <= 0: up.pop()
        up.append(p_)
    return lo[:-1] + up[:-1]
def spath(pts, fill, extra=''):
    out.append('<path d="M%s Z" fill="%s"%s></path>' % (' L'.join('%.1f %.1f' % q for q in pts), fill, extra))
def seg(a, b, cls):
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"></line>' % (*a, *b, cls))
# five-star base (far legs first), casters, hub, gas lift
hub = pr(CHX, 0.09, CHZ)
legs = [(0.3 * math.cos(math.radians(100 + i * 72)), 0.3 * math.sin(math.radians(100 + i * 72))) for i in range(5)]
for ex, ez in sorted(legs, key=lambda e: -e[1]):
    end = pr(CHX + ex, 0.065, CHZ + ez)
    cx_, cy_ = pr(CHX + ex, 0.035, CHZ + ez)
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="8" ry="7" fill="#0d0e10"></ellipse><path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" class="caster"></path><circle cx="%.1f" cy="%.1f" r="1.6" fill="#2a2d31"></circle>' % (cx_, cy_, cx_ - 5.5, cy_ - 2, cx_, cy_ - 8, cx_ + 5.5, cy_ - 2, cx_, cy_))
    seg(hub, end, 'cleg')
    seg(hub, end, 'clegh')
out.append('<ellipse cx="%.1f" cy="%.1f" rx="14" ry="7" fill="#26292d"></ellipse>' % hub)
seg(pr(CHX, 0.1, CHZ), pr(CHX, 0.2, CHZ), 'cshroud')
seg(pr(CHX, 0.2, CHZ), pr(CHX, 0.41, CHZ), 'cgas')
seg(pr(CHX, 0.2, CHZ), pr(CHX, 0.41, CHZ), 'cgash')
spath([CP(a_, 0.4, b_) for a_, b_ in rrect(-0.13, 0.13, -0.1, 0.14, 0.04, 0.04)], '#141517')
def arm(lx):
    pts = [CP(lx, 0.4, 0.1), CP(lx, 0.6, 0.085), CP(lx, 0.635, -0.12)]
    out.append('<polyline points="%s" fill="none" class="carm"></polyline>' % ' '.join('%.1f,%.1f' % q for q in pts))
    ol = rrect(lx - 0.037, lx + 0.037, -0.2, 0.1, 0.035, 0.035, 5)
    body = hull([CP(a_, 0.63, b_) for a_, b_ in ol] + [CP(a_, 0.69, b_) for a_, b_ in ol])
    spath(body, '#101113')
    spath([CP(a_, 0.69, b_ * 0.96) for a_, b_ in ol], 'url(#pad)')
arm(0.285)
seat = rrect(-0.265, 0.265, -0.27, 0.2, 0.09, 0.07)
spath(hull([CP(a_, 0.43, b_) for a_, b_ in seat] + [CP(a_, 0.555, b_) for a_, b_ in seat]), '#111214')
spath([CP(a_, 0.555, b_ * 0.97) for a_, b_ in seat], 'url(#leather)')
arm(-0.285)
# back: gently tapered, rounded shoulders, slight recline; front shell then the rear panel
def back_pts(lz_off, scale=1.0):
    pts = []
    for u, v in rrect(-0.25, 0.25, 0.5, 1.2, 0.05, 0.11, 9):
        t = (v - 0.5) / 0.7
        hw = 0.215 + 0.035 * math.sin(math.pi * min(1, t * 1.25))
        uu = u / 0.25 * hw * scale
        vv = 0.85 + (v - 0.85) * scale
        pts.append(CP(uu, vv, 0.2 + lz_off + t * 0.07))
    return pts
spath(hull(back_pts(0.03) + back_pts(0.1)), '#0e0f11')
spath(back_pts(0.1), 'url(#leather)')
out.append('<path d="M%s Z" fill="none" class="cstitch"></path>' % ' L'.join('%.1f %.1f' % q for q in back_pts(0.101, 0.92)))
s0, s1, sm = CP(-0.235, 0.98, 0.3), CP(0.235, 0.98, 0.3), CP(0, 0.965, 0.3)
out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" class="cseam"></path>' % (s0[0], s0[1], sm[0], sm[1] + 4, s1[0], s1[1]))

# ---------- left wall: resume, with its own picture light ----------
cur[0] = 'resume'
box(XL, 1.2, 2.25, 0.03, 0.64, 0.46, '#171b20')                          # frame
side_rect(XL + 0.032, 2.28, 2.68, 1.24, 1.8, '#e6e0d3')                  # paper
side_rect(XL + 0.033, 2.33, 2.52, 1.7, 1.74, '#2a3440')                  # name bar
side_rect(XL + 0.033, 2.33, 2.44, 1.66, 1.675, '#b8733f')
for i, (yy, w) in enumerate([(1.6,.3),(1.57,.25),(1.52,.3),(1.49,.2),(1.44,.3),(1.41,.27),(1.36,.18),(1.31,.29),(1.28,.22)]):
    side_rect(XL + 0.033, 2.33, 2.33 + w, yy, yy + 0.012, '#9a9384')
box(XL, 1.92, 2.4, 0.14, 0.03, 0.16, '#2a2f36')                          # picture light
box(XL + 0.1, 1.9, 2.3, 0.05, 0.025, 0.36, '#3a414a')
cur[0] = None
POOL = pr(XL + 0.03, 1.72, 2.48)

# ---------- right wall: framed posters (FILMS) ----------
cur[0] = 'films'
XR = HW - 0.005
def framed(z0, z1, y0, y1, art):
    box(XR - 0.03, y0, z0, 0.03, y1 - y0, z1 - z0, '#121315')             # slim black frame, 3 cm deep
    xf = XR - 0.031
    side_rect(xf, z0 + 0.018, z1 - 0.018, y0 + 0.018, y1 - 0.018, '#e7e2d7')  # white mat
    side_rect(xf - 0.0005, z0 + 0.052, z1 - 0.052, y0 + 0.06, y1 - 0.052, '#b9b3a6')  # mat bevel edge
    art(xf - 0.001, z0 + 0.056, z1 - 0.056, y0 + 0.064, y1 - 0.056)
    side(xf - 0.003, [(z0 + 0.02, y1 - 0.02), (z0 + 0.2, y1 - 0.02), (z0 + 0.02, y1 - 0.3)], '#ffffff', ' opacity="0.05"')  # glass glint
def art_a(x, z0, z1, y0, y1):
    side_rect(x, z0, z1, y0, y1, '#1f3040')
    side_rect(x - 0.0005, z0, z1, y0, y0 + (y1 - y0) * 0.38, '#152331')
    side_circle(x - 0.0005, (z0 + z1) / 2, y0 + (y1 - y0) * 0.62, 0.075, '#ee8a45')
    side_rect(x - 0.0008, z0 + 0.04, z0 + 0.24, y0 + 0.09, y0 + 0.11, '#d8cbb3')
    side_rect(x - 0.0008, z0 + 0.04, z0 + 0.16, y0 + 0.06, y0 + 0.07, '#7d8a97')
def art_b(x, z0, z1, y0, y1):
    side_rect(x, z0, z1, y0, y1, '#d6c9ae')
    side(x - 0.0005, [(z0 + 0.04, y0 + 0.18), ((z0 + z1) / 2 - 0.02, y1 - 0.1), (z1 - 0.04, y0 + 0.18)], '#2f4658')
    side(x - 0.0008, [(z0 + 0.12, y0 + 0.18), (z0 + 0.25, y0 + 0.42), (z1 - 0.04, y0 + 0.18)], '#b8453a')
    side_rect(x - 0.0008, z0 + 0.04, z0 + 0.26, y0 + 0.09, y0 + 0.11, '#1f2a36')
    side_rect(x - 0.0008, z0 + 0.04, z0 + 0.16, y0 + 0.06, y0 + 0.07, '#6b6150')
framed(2.06, 2.64, 1.16, 1.98, art_a)
framed(2.76, 3.3, 1.2, 1.96, art_b)
cur[0] = None

# ---------- right wall: cabinet, turntable, bookshelf speaker (MUSIC) ----------
cur[0] = 'music'
WAL = '#4a2f1e'
for fx, fz in [(1.72, 3.62), (1.72, 2.44), (1.37, 3.62), (1.37, 2.44)]:
    box(fx, 0, fz, 0.045, 0.07, 0.045, '#2b2119')                  # cabinet feet, inset at each corner
box(1.35, 0.07, 2.4, 0.45, 0.51, 1.3, '#3f3228')
CF = shade('#3f3228', -0.2)                                              # cabinet front colour
side(1.3495, [(2.4,0.07),(3.7,0.07),(3.7,0.105),(2.4,0.105)], shade(CF, -0.35))   # recessed toe kick
side(1.3495, [(2.4,0.555),(3.7,0.555),(3.7,0.58),(2.4,0.58)], shade(CF, 0.12))     # top lip
for z0, z1 in [(2.45, 3.03), (3.07, 3.65)]:
    side(1.349, [(z0,0.12),(z1,0.12),(z1,0.54),(z0,0.54)], shade(CF, 0.05))
    side(1.349, [(z0,0.12),(z1,0.12),(z1,0.54),(z0,0.54)], 'none', ' class="drawer"')
    side_bevel(1.3485, z0 + 0.06, z1 - 0.06, 0.18, 0.48, 0.018, shade(CF, -0.08), shade(CF, 0.2), shade(CF, -0.4))
# brass bar pulls with little standoffs
for pz in (2.995, 3.105):
    side(1.347, [(pz, 0.27), (pz + 0.012, 0.27), (pz + 0.012, 0.4), (pz, 0.4)], '#b89a6a')
    side(1.3465, [(pz + 0.003, 0.3), (pz + 0.006, 0.3), (pz + 0.006, 0.37), (pz + 0.003, 0.37)], '#e0c78f')
# near end panel of the cabinet (faces the camera)
g(front(1.35, 0.58, 2.399),
  bevel_svg(5, 6, 40, 42, 1.8, shade('#3f3228', -0.08), shade('#3f3228', 0.16), shade('#3f3228', -0.35))
  + '<rect x="0" y="47.5" width="45" height="3.5" fill="%s"></rect>' % shade('#3f3228', -0.4)
  + '<rect x="0" y="0" width="45" height="2" fill="%s"></rect>' % shade('#3f3228', 0.1))
def side_ring(xw, zc, yc, r, cls, a0=0, a1=360, n=36):
    pts = [(zc + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), yc + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    q = [pr(xw, y_, z_) for z_, y_ in pts]
    out.append('<polyline points="%s" fill="none" class="%s"></polyline>' % (' '.join('%.1f,%.1f' % t for t in q), cls))
# bookshelf speaker on isolation pads: walnut box, black baffle, framed woofer, tweeter with waveguide, flared port
for pz in (3.25, 3.46):
    box(1.47, 0.58, pz, 0.26, 0.012, 0.03, '#141414')
SY0 = 0.592
box(1.46, SY0, 3.22, 0.3, 0.44, 0.28, WAL)
side_rect(1.4592, 3.232, 3.488, SY0 + 0.012, SY0 + 0.428, '#232427')          # baffle bevel
side_rect(1.459, 3.24, 3.48, SY0 + 0.02, SY0 + 0.42, '#17181a')               # baffle
WY, TY = SY0 + 0.165, SY0 + 0.345
side_circle(1.4585, 3.36, WY, 0.108, '#232427')                              # woofer frame
for k in range(4):
    ang = math.radians(45 + 90 * k)
    side_circle(1.4575, 3.36 + 0.099 * math.cos(ang), WY + 0.099 * math.sin(ang), 0.005, '#6b7077')
side_circle(1.458, 3.36, WY, 0.094, '#2c2d30')                                # rubber surround
side_ring(1.4572, 3.36, WY, 0.088, 'spkhl', 60, 170, 14)                      # surround sheen
side_circle(1.457, 3.36, WY, 0.078, '#101113')                                # cone
side_ring(1.4565, 3.36, WY, 0.056, 'spkring')
side_circle(1.4562, 3.36, WY, 0.028, '#26272a')                               # dust cap
side_circle(1.456, 3.352, WY + 0.01, 0.008, '#3a3c40')                       # cap highlight
side_circle(1.4585, 3.36, TY, 0.052, '#232427')                               # tweeter faceplate
for k in range(2):
    ang = math.radians(90 + 180 * k)
    side_circle(1.4575, 3.36 + 0.044 * math.cos(ang), TY + 0.044 * math.sin(ang), 0.004, '#6b7077')
side_circle(1.458, 3.36, TY, 0.038, '#1a1b1d')                                # waveguide
side_ring(1.4572, 3.36, TY, 0.03, 'spkring')
side_circle(1.457, 3.36, TY, 0.019, '#7a8087')                                # dome
side_circle(1.4565, 3.354, TY + 0.006, 0.006, '#c0c5ca')                      # dome glint
side_rect(1.458, 3.3, 3.42, SY0 + 0.035, SY0 + 0.062, '#2a2b2e')              # port flare
side_rect(1.4575, 3.308, 3.412, SY0 + 0.041, SY0 + 0.056, '#040405')          # port
# turntable: walnut plinth on feet with a brushed trim strip
for fx, fz in [(1.72, 2.97), (1.72, 2.57), (1.44, 2.97), (1.44, 2.57)]:
    box(fx, 0.58, fz, 0.035, 0.016, 0.035, '#161616')
box(1.42, 0.596, 2.55, 0.34, 0.074, 0.46, WAL)
side_rect(1.4195, 2.55, 3.01, 0.652, 0.66, '#8d949b')                        # aluminium trim
PCX, PCZ = 1.575, 2.745
top_circle(0.672, PCX, PCZ, 0.152, '#5b6168')                                # platter side
top_circle(0.684, PCX, PCZ, 0.152, '#a3aab1')                                # platter rim
for k in range(40):                                                          # strobe dots
    ang = math.radians(k * 9)
    top_circle(0.6845, PCX + 0.149 * math.cos(ang), PCZ + 0.149 * math.sin(ang), 0.0025, '#5b6168')
top_circle(0.686, PCX, PCZ, 0.146, '#0b0b0d')                                # record
for rr_ in (0.135, 0.122, 0.108, 0.094, 0.08, 0.066):
    top_circle(0.687, PCX, PCZ, rr_, 'none', ' class="groove"')
sheen = [(PCX + r_ * math.cos(math.radians(a_)), 0.6872, PCZ + r_ * math.sin(math.radians(a_))) for r_, a_ in
         [(0.05, 200), (0.143, 196), (0.143, 222), (0.05, 232)]]
poly3(sheen, '#ffffff', ' opacity="0.07"')
sheen2 = [(PCX + r_ * math.cos(math.radians(a_)), 0.6872, PCZ + r_ * math.sin(math.radians(a_))) for r_, a_ in
          [(0.05, 20), (0.143, 16), (0.143, 38), (0.05, 48)]]
poly3(sheen2, '#ffffff', ' opacity="0.04"')
top_circle(0.688, PCX, PCZ, 0.045, '#ee8a45')                                # label
top_circle(0.6885, PCX, PCZ, 0.033, 'none', ' class="labelring"')
top_circle(0.689, PCX, PCZ, 0.006, '#dddddd')                                # spindle
# controls: start/stop, 33/45, power light, pitch fader
top_circle(0.671, 1.452, 2.585, 0.016, '#2a2b2e')
top_circle(0.675, 1.452, 2.585, 0.012, '#c9ccd1')
top_circle(0.671, 1.46, 2.63, 0.004, '#ff8a3d')
out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="url(#glow)" style="mix-blend-mode:screen"></circle>' % pr(1.46, 0.671, 2.63))
box(1.44, 0.67, 2.93, 0.02, 0.006, 0.02, '#8d949b')
box(1.44, 0.67, 2.958, 0.02, 0.006, 0.02, '#8d949b')
poly3([(1.5, 0.6705, 2.978), (1.64, 0.6705, 2.978), (1.64, 0.6705, 2.988), (1.5, 0.6705, 2.988)], '#0d0d0e')
box(1.566, 0.67, 2.972, 0.014, 0.01, 0.022, '#c9ccd1')
# dust-cover hinges at the back
for hz in (2.62, 2.92):
    box(1.745, 0.67, hz, 0.015, 0.025, 0.04, '#141414')
# tonearm: armboard, bearing, anti-skate, cue lever, rest, counterweight, S-arm, headshell + cartridge
top_circle(0.6705, 1.7, 2.95, 0.045, '#1c1d20')
top_circle(0.671, 1.7, 2.95, 0.028, '#3a3c40')
top_circle(0.672, 1.655, 2.985, 0.009, '#a3aab1')                            # anti-skate dial
box(1.73, 0.67, 2.885, 0.012, 0.03, 0.012, '#a3aab1')                         # cue lever post
box(1.715, 0.7, 2.885, 0.04, 0.006, 0.01, '#c9ccd1')                          # cue lever
box(1.694, 0.67, 2.82, 0.01, 0.035, 0.01, '#a3aab1')                          # arm rest
box(1.692, 0.671, 2.942, 0.016, 0.04, 0.016, '#a3aab1')                       # bearing post
box(1.705, 0.7, 2.962, 0.04, 0.03, 0.034, '#c3c9cf')                          # counterweight
box(1.725, 0.698, 2.962, 0.005, 0.034, 0.034, '#8d949b')
arm = [pr(1.7, 0.712, 2.95), pr(1.66, 0.711, 2.935), pr(1.6, 0.709, 2.912), pr(1.545, 0.705, 2.885), pr(1.505, 0.7, 2.86)]
out.append('<polyline points="%s" fill="none" class="tonearm"></polyline>' % ' '.join('%.1f,%.1f' % q for q in arm))
out.append('<polyline points="%s" fill="none" class="tonearmhl"></polyline>' % ' '.join('%.1f,%.1f' % q for q in arm))
poly3([(1.472, 0.698, 2.838), (1.506, 0.698, 2.848), (1.5, 0.698, 2.874), (1.466, 0.698, 2.864)], '#d0d4d8')   # headshell
box(1.474, 0.689, 2.845, 0.022, 0.009, 0.02, '#1a1a1a')                       # cartridge
a_, b_ = pr(1.47, 0.699, 2.85), pr(1.458, 0.703, 2.842)
out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="fingerlift"></line>' % (*a_, *b_))
cur[0] = None

# glows
lx, ly = LAMP
out.append('<ellipse cx="%.1f" cy="%.1f" rx="330" ry="230" fill="url(#glow)" style="mix-blend-mode:screen"></ellipse>' % (lx, ly - 30))
out.append('<ellipse cx="%.1f" cy="%.1f" rx="130" ry="36" fill="url(#glow)" style="mix-blend-mode:screen"></ellipse>' % (lx - 30, ly + 22))
# soft pool of light from the picture lamp onto the resume
out.append('<ellipse cx="%.1f" cy="%.1f" rx="70" ry="120" fill="url(#pool)" style="mix-blend-mode:screen"></ellipse>' % POOL)

out.append('<rect x="0" y="0" width="1440" height="900" fill="url(#vig)"></rect>')
svg_body = '\n'.join(out)

def bbox(pts, pad=8):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = max(0, min(xs) - pad), max(0, min(ys) - pad)
    x1, y1 = min(1440, max(xs) + pad), min(900, max(ys) + pad)
    return (round(x0), round(y0), round(x1 - x0), round(y1 - y0))
spots = {k: bbox(v) for k, v in groups.items()}
print(spots)
open('/tmp/claude-0/-home-claude/4bdfed87-4ff7-5d7b-a1e9-ccf0df0d2804/scratchpad/svg_body.txt', 'w').write(svg_body)
json.dump({'spots': spots, 'anchors': {
  'projects': pr(-0.2, 2.17, Zc), 'blog': pr(-0.6, 0.76, 3.62), 'about': pr(XL + 0.25, 1.45, 3.1),
  'resume': pr(XL + 0.03, 1.84, 2.25), 'films': pr(XR, 1.96, 2.36), 'music': pr(1.35, 0.58, 2.4)}},
  open('/tmp/claude-0/-home-claude/4bdfed87-4ff7-5d7b-a1e9-ccf0df0d2804/scratchpad/geo.json', 'w'))
print(json.load(open('/tmp/claude-0/-home-claude/4bdfed87-4ff7-5d7b-a1e9-ccf0df0d2804/scratchpad/geo.json'))['anchors'])
