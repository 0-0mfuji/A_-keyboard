"""keyboard_v5 case v7: low, 4 deg front-down wedge, 34 mm trackball with SEIBOKU.

Run headless:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd hardware/freecad/build_case_v7.py

Inputs (KiCad 10 STEP exports, see hardware/step-export/kicad/):
  keyboard-v5-left.step / keyboard-v5-right.step   (J3 jumper header excluded)
  seiboku-pmw3610.step                              (J1 pin header excluded)
Outputs:
  hardware/freecad/case_v7.FCStd       whole assembly in desk frame (bottom on z=0)
  hardware/step-export/case-v7-*.step/.stl    printable parts in desk frame
  hardware/freecad/case_v7_report.txt  heights and interference results

Geometry is built in the PCB frame (PCB bottom z=0, top 1.51, plate 5.01..6.51,
KiCad x, y flipped), then rotated so the tilted case bottom lies on the desk.
"""
import math
import os
import re

import FreeCAD as App
import Mesh
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
KSTEP = os.path.join(ROOT, "hardware", "step-export", "kicad")
EXPORT = os.path.join(ROOT, "hardware", "step-export")
OUT = os.path.join(HERE, "case_v7.FCStd")
REPORT = os.path.join(HERE, "case_v7_report.txt")

V = App.Vector

# --- case --------------------------------------------------------------------
TILT_DEG = 4.0          # front-down wedge (bottom plane vs PCB)
Z_RIM = 8.5             # bezel top, PCB frame (plate top 6.51)
DECK = 2.5
SHELL = 2.5
FLOOR = 1.5
PCB_CLEAR = 0.5
UNDER_PCB = 6.3         # hot-swap sockets 2.0 + 401230 LiPo 4.0 + 0.3
OUTER_OFFSET = 5.0
MIN_OUTER = 4.5
SMOOTH_R = 30.0
TAUBIN_POINTS = 120
TAUBIN_ITERS = 150
EDGE_R = 3.0            # rounding of top and bottom outer edges

# --- trackball ---------------------------------------------------------------
BALL_R = 17.0
BALL_XY = (248.0, -104.0)
CUP_GAP = 1.0           # ball -> spherical pocket
CUP_R = 22.5
CERAMIC_D = 3.0         # ZrO2 support balls
CERAMIC_PRESS = 0.05    # pocket = D - press (press fit)
CERAMIC_ELEV = -40.0
CERAMIC_AZ = (90.0, 210.0, 330.0)
# PMW3610 + LM18-LSI stack (PixArt datasheet Fig.4, SEIBOKU README)
LENS_REF_TO_BALL = 2.4  # Z, lens reference plane -> tracking surface
PCB_TO_LENS_REF = 3.4   # lens-side PCB surface -> lens reference plane
LENS_THICK = 4.0        # lens-side PCB surface -> lowest lens point
SENSOR_BELOW = 1.65     # sensor body beyond the sensor-side PCB surface
SEIBOKU_T = 1.51        # as exported by KiCad
CUP_UNDER_GAP = 4.4     # lens-side PCB surface -> underside of cup
SENSOR_BOTTOM_CLEAR = 0.3
SEIBOKU_HOLES = [(sx * 13.0, sy * 8.0) for sx in (-1, 1) for sy in (-1, 1)]
SEIBOKU_OPTICAL = (147.69, -96.5)   # STEP coords of the optical centre
# ball cover (cocot36plus / cocot46plus style ring), held by magnets
COVER_BASE_R = 24.8     # seam radius on the deck
COVER_RECESS = 1.2      # cover base sits this deep in the deck -> flush seam
COVER_EQ_R = 17.4       # inner cylinder around the equator (cocot: R17.41, 0.4 mm gap)
COVER_EQ_TOP = 1.2      # inner cylinder ends this far above the equator
COVER_LIP_R = 16.75     # narrowest inner radius (opening 33.5 < 34; cocot: 33.6)
COVER_LIP_Z = 3.9       # lip height above the equator (0.2 mm from the ball)
COVER_TOP_Z = 4.4       # cover top above the equator -> ball shows 12.6 mm (cocot: ~12.7)
MAGNET_D = 6.0          # DAISO "超強力マグネットミニ" 6 x 3 mm
MAGNET_T = 3.0
MAGNET_FIT = 0.1        # pocket clearance (glue in)
MAGNET_R = 21.1         # pitch radius of the magnet pairs
MAGNET_AZ = (210.0, 270.0, 330.0)   # south side, away from the keys

MOUNT = {
    "left": [(21.15, 38.6075), (82.65, 96.0075), (148.25, 26.3075)],
    "right": [(304.9068, 60.1075), (231.1068, 72.4075), (181.9068, 35.5075)],
}
XIAO = {"left": (148.6125, 11.6075), "right": (180.045, 11.6075)}
SWITCH = {"left": (157.0, 30.4875, 90.0), "right": (173.0, 30.5, -90.0)}
USB_W = 14.0
USB_Z0 = 0.3
BATTERY = {"left": (122.0, -33.0), "right": (205.0, -36.0)}   # 401230 proxy centres

T = math.tan(math.radians(TILT_DEG))
LOG = []


def log(msg):
    print(msg)
    LOG.append(msg)


# --- plane helpers (PCB frame) ---------------------------------------------------
Y_FRONT = None           # set from the PCB outlines
D_FRONT = UNDER_PCB + FLOOR


def z_bottom(y):
    return -D_FRONT - (y - Y_FRONT) * T


def below_plane(offset=0.0):
    """Solid filling everything below the bottom plane raised by `offset` (normal dir)."""
    box = Part.makeBox(2000, 2000, 400, V(-1000, -1000, -400))
    box.rotate(V(0, Y_FRONT, 0), V(1, 0, 0), -TILT_DEG)
    n = V(0, T, 1)
    n.normalize()
    box.translate(V(0, 0, -D_FRONT) + n * offset)
    return box


# --- 2D outline helpers ------------------------------------------------------------
def outer_face(shape):
    shape = shape.removeSplitter()
    return Part.Face(max(shape.Faces, key=lambda f: f.Area).OuterWire)


def disk(x, y, r):
    return Part.Face(Part.Wire([Part.makeCircle(r, V(x, y, 0))]))


def prism(face, z0, z1):
    f = face.copy()
    f.translate(V(0, 0, z0 - f.BoundBox.ZMin))
    return f.extrude(V(0, 0, z1 - z0))


def cylinder(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def rounded_box(cx, cy, z0, sx, sy, sz, r):
    b = Part.makeBox(sx, sy, sz, V(cx - sx / 2, cy - sy / 2, z0))
    vert = [e for e in b.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99]
    return b.makeFillet(r, vert) if r > 0 else b


def smooth_bspline_face(face, step=5.0):
    wire = face.OuterWire
    ref = face.BoundBox
    for st in (step, step * 0.8, step * 0.6, step * 1.2):
        n = max(24, int(wire.Length / st))
        pts = wire.discretize(Number=n + 1)[:-1]
        pts = [p for i, p in enumerate(pts) if p.distanceToPoint(pts[i - 1]) > st * 0.3]
        bs = Part.BSplineCurve()
        bs.interpolate(pts, PeriodicFlag=True)
        out = Part.Face(Part.Wire([bs.toShape()]))
        bb = out.BoundBox
        if max(abs(bb.XMin - ref.XMin), abs(bb.XMax - ref.XMax),
               abs(bb.YMin - ref.YMin), abs(bb.YMax - ref.YMax)) < 1.0 and out.isValid():
            return out
    raise RuntimeError("B-spline smoothing diverged")


def taubin_smooth_face(face, n=TAUBIN_POINTS, iters=TAUBIN_ITERS, lam=0.5, mu=-0.53):
    pts = [(p.x, p.y) for p in face.OuterWire.discretize(Number=n + 1)[:-1]]
    for _ in range(iters):
        for f in (lam, mu):
            pts = [(x + f * ((pts[i - 1][0] + pts[(i + 1) % n][0]) / 2 - x),
                    y + f * ((pts[i - 1][1] + pts[(i + 1) % n][1]) / 2 - y))
                   for i, (x, y) in enumerate(pts)]
    out = [V(x, y, 0) for x, y in pts]
    return Part.Face(Part.makePolygon(out + out[:1]))


def smooth_outline(side, face):
    keep = face.makeOffset2D(MIN_OUTER, join=0)
    grown = face.makeOffset2D(OUTER_OFFSET + SMOOTH_R, join=0)
    if side == "right":
        pod = CUP_R + SHELL + 1.5
        keep = keep.fuse(disk(*BALL_XY, pod))
        grown = grown.fuse(disk(*BALL_XY, pod + SMOOTH_R))
    closed = outer_face(outer_face(grown).makeOffset2D(-SMOOTH_R, join=0))
    soft = taubin_smooth_face(closed)
    grow = 0.0
    for w in keep.Wires:
        for p in w.discretize(Distance=1.0):
            if not soft.isInside(p, 1e-4, True):
                grow = max(grow, soft.OuterWire.distToShape(Part.Vertex(p))[0])
    if grow:
        soft = outer_face(soft.makeOffset2D(grow + 0.1, join=0))
    return smooth_bspline_face(soft)


def frustum(c0, size0, c1, size1, axis):
    side = V(-axis.y, axis.x, 0)

    def rect(c, size):
        w, h = size[0] / 2, size[1] / 2
        up = V(0, 0, 1)
        pts = [c + side * w + up * h, c - side * w + up * h,
               c - side * w - up * h, c + side * w - up * h]
        return Part.makePolygon(pts + pts[:1])
    return Part.makeLoft([rect(c0, size0), rect(c1, size1)], True, True)


# --- parts that KiCad has no model for -----------------------------------------------
def xiao_proxy(side):
    x, ky = XIAO[side]
    y = -ky
    body = Part.makeBox(17.8, 21.0, 1.2, V(x - 8.9, y - 10.4, 1.51))
    can = Part.makeBox(12.0, 12.0, 1.6, V(x - 6.0, y - 8.0, 2.71))
    usb_end = -(ky - 10.55)            # USB end of the courtyard (back edge)
    usb = Part.makeBox(8.94, 7.35, 3.26, V(x - 4.47, usb_end - 6.15, 2.71))
    return body.fuse([can, usb])


def switch_proxy(side):
    x, ky, rot = SWITCH[side]
    body = Part.makeBox(6.7, 2.6, 1.4, V(-3.35, -1.3, 1.51))
    lever = Part.makeBox(1.5, 1.6, 1.0, V(-0.75, -2.9, 1.71))   # KiCad local +y
    s = body.fuse(lever)
    s.rotate(V(0, 0, 0), V(0, 0, 1), rot)   # lever ends up at the board edge
    s.translate(V(x, -ky, 0))
    return s


def battery_proxy(side):
    x, y = BATTERY[side]
    return Part.makeBox(30.0, 12.0, 4.0, V(x - 15.0, y - 6.0, -2.3 - 4.0))


def keycap_proxies(side):
    s = open(os.path.join(ROOT, "hardware", "keyboard_v5", side, "keyboard.kicad_pcb")).read()
    caps = []
    for u, body in re.findall(r'\n\t\(footprint "Keyboard:MX_Hotswap_([\d.]+)u"(.*?)\n\t\)', s, re.S):
        x, y, rot = re.search(r'\(at ([-\d.]+) ([-\d.]+)( [-\d.]+)?\)', body).groups()
        w = float(u) * 19.05 - 0.9
        cap = Part.makeBox(w, 18.15, 13.5, V(-w / 2, -18.15 / 2, 11.5))   # z 11.5..25
        cap.rotate(V(0, 0, 0), V(0, 0, 1), float(rot or 0))
        cap.translate(V(float(x), -float(y), 0))
        caps.append(cap)
    return caps


def pmw3610_and_lens():
    """PMW3610DM-SUDU body + LM18-LSI envelope in SEIBOKU STEP coordinates.
    Sensor on the top (F) side, lens on the bottom (B) side facing the ball."""
    ox, oy = SEIBOKU_OPTICAL
    fx, fy = 144.51, -101.85            # footprint origin (pin 1), rotated 180
    body_x0, body_x1 = fx - 1.425, fx + 14.775
    body = Part.makeBox(body_x1 - body_x0, 9.1, SENSOR_BELOW, V(body_x0, oy - 4.55, SEIBOKU_T))
    leads = Part.makeBox(body_x1 - body_x0, 10.9, SENSOR_BELOW + 0.8,
                         V(body_x0, oy - 5.45, SEIBOKU_T - 0.8))
    in_cutout = Part.makeBox(16.6, 8.2, 2.4, V(141.9, oy - 4.1, -0.89))
    sensor = body.fuse([leads, in_cutout])
    lens = Part.makeBox(16.8, 12.4, PCB_TO_LENS_REF, V(141.8, -102.7, -PCB_TO_LENS_REF))
    dome = cylinder(3.0, ox, oy, -LENS_THICK, -PCB_TO_LENS_REF + 0.01)
    return sensor, lens.fuse(dome)


def place_seiboku(shape, z_lens_side):
    """Flip SEIBOKU lens-side up and centre its optical axis on the ball."""
    s = shape.copy()
    ox, oy = SEIBOKU_OPTICAL
    s.translate(V(-ox, -oy, 0))
    s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    s.translate(V(BALL_XY[0], BALL_XY[1], z_lens_side))
    return s


# --- case ---------------------------------------------------------------------------
def rounded_body(outline):
    r = EDGE_R
    core = prism(outer_face(outline.makeOffset2D(-r, join=0)), -80.0, Z_RIM - r)
    core = core.cut(below_plane(r))
    for tol in (0.01, 0.05, 0.1):
        try:
            return core.makeOffsetShape(r, tol, join=0, fill=False)
        except Exception:
            pass
    raise RuntimeError("rounded body offset failed")


def trackball_geometry(z_c):
    bx, by = BALL_XY
    c = V(bx, by, z_c)
    b = z_c - BALL_R
    z_lens_side = b - LENS_REF_TO_BALL - PCB_TO_LENS_REF
    z_cup_under = z_lens_side + CUP_UNDER_GAP
    z_deck_bot = Z_RIM - DECK
    cup = cylinder(CUP_R, bx, by, z_cup_under, z_deck_bot + 0.01)
    for hx, hy in SEIBOKU_HOLES:
        cup = cup.fuse(cylinder(2.3, bx + hx, by + hy, z_lens_side, z_cup_under + 0.01))
    for az in MAGNET_AZ:               # material around the case-side magnets
        a = math.radians(az)
        cup = cup.fuse(cylinder(MAGNET_D / 2 + 0.8, bx + MAGNET_R * math.cos(a),
                                by + MAGNET_R * math.sin(a), z_cup_under, z_deck_bot + 0.01))
    pocket = Part.makeSphere(BALL_R + CUP_GAP, c)
    return c, z_lens_side, z_cup_under, cup, pocket


def trackball_cuts(z_c, z_lens_side, z_cup_under):
    bx, by = BALL_XY
    c = V(bx, by, z_c)
    cuts = [Part.makeSphere(BALL_R + CUP_GAP, c),
            cylinder(BALL_R + CUP_GAP, bx, by, z_c, z_c + 40),
            rounded_box(bx, by, z_cup_under - 1, 12.0, 9.0, 6, 1.0)]        # optical window
    for hx, hy in SEIBOKU_HOLES:   # M2 self-tapping from the sensor side
        cuts.append(cylinder(0.85, bx + hx, by + hy, z_lens_side - 1, z_cup_under + 4))
    el = math.radians(CERAMIC_ELEV)
    for az in CERAMIC_AZ:
        a = math.radians(az)
        d = V(math.cos(el) * math.cos(a), math.cos(el) * math.sin(a), math.sin(el))
        seat = BALL_R + CERAMIC_D          # pocket floor: ceramic centre at R + d/2
        cuts.append(Part.makeCylinder((CERAMIC_D - CERAMIC_PRESS) / 2, seat - BALL_R + 0.5,
                                      c + d * (BALL_R - 0.5), d))
    cuts.append(cylinder(COVER_BASE_R + 0.2, bx, by, Z_RIM - COVER_RECESS, Z_RIM + 1))   # cover seat
    for az in MAGNET_AZ:               # case-side magnet pockets under the seat
        a = math.radians(az)
        cuts.append(cylinder((MAGNET_D + MAGNET_FIT) / 2, bx + MAGNET_R * math.cos(a),
                             by + MAGNET_R * math.sin(a),
                             Z_RIM - COVER_RECESS - MAGNET_T - MAGNET_FIT, Z_RIM))
    return cuts


def collar(z_c):
    """cocot-style ball cover: low ring hugging the ball equator, lip just above it,
    smooth domed outside rising from a flush deck seam. Held by 3 magnet pairs."""
    bx, by = BALL_XY
    zb = Z_RIM - COVER_RECESS
    rb = COVER_BASE_R
    P = lambda r, dz: V(r, 0, z_c + dz)
    base = zb - z_c
    seam = Z_RIM - z_c
    lr = 0.5                                           # lip round
    top = P(COVER_LIP_R + lr, COVER_TOP_Z)
    outer = Part.BSplineCurve()
    pts = [P(rb, seam), P(rb - 0.2, seam + 0.32 * (COVER_TOP_Z - seam)),
           P(rb - 1.4, -0.8), P(rb - 3.4, 2.0), P(rb - 5.5, 3.75), top]
    tan = [V(0, 0, 1)] + [V(0, 0, 1)] * (len(pts) - 2) + [V(-1, 0, 0)]
    outer.interpolate(Points=pts, Tangents=tan, TangentFlags=[True] + [False] * (len(pts) - 2) + [True])
    s45 = math.sqrt(0.5)
    lip = P(COVER_LIP_R, COVER_TOP_Z - lr)
    edges = [
        Part.LineSegment(P(COVER_EQ_R, base), P(rb, base)).toShape(),
        Part.LineSegment(P(rb, base), P(rb, seam)).toShape(),
        outer.toShape(),
        Part.Arc(top, P(COVER_LIP_R + lr - lr * s45, COVER_TOP_Z - lr + lr * s45), lip).toShape(),
        Part.LineSegment(lip, P(COVER_LIP_R, COVER_LIP_Z)).toShape() if COVER_TOP_Z - lr > COVER_LIP_Z + 1e-6 else None,
        Part.LineSegment(P(COVER_LIP_R, min(COVER_LIP_Z, COVER_TOP_Z - lr)), P(COVER_EQ_R, COVER_EQ_TOP)).toShape(),
        Part.LineSegment(P(COVER_EQ_R, COVER_EQ_TOP), P(COVER_EQ_R, base)).toShape(),
    ]
    body = Part.Face(Part.Wire([e for e in edges if e is not None])).revolve(V(0, 0, 0), V(0, 0, 1), 360)
    body = Part.Solid(Part.Shell(body.Faces)) if body.ShapeType != "Solid" else body
    body.translate(V(bx, by, 0))
    for az in MAGNET_AZ:               # cover-side magnet pockets, from below
        a = math.radians(az)
        body = body.cut(cylinder((MAGNET_D + MAGNET_FIT) / 2, bx + MAGNET_R * math.cos(a),
                                 by + MAGNET_R * math.sin(a), zb - 0.1, zb + MAGNET_T + MAGNET_FIT))
    return body.removeSplitter()


def magnets(z_c):
    bx, by = BALL_XY
    zb = Z_RIM - COVER_RECESS
    out = []
    for az in MAGNET_AZ:
        a = math.radians(az)
        x, y = bx + MAGNET_R * math.cos(a), by + MAGNET_R * math.sin(a)
        out += [cylinder(MAGNET_D / 2, x, y, zb, zb + MAGNET_T),
                cylinder(MAGNET_D / 2, x, y, zb - MAGNET_T, zb)]
    return Part.makeCompound(out)


def build_case(side, face, z_c=None):
    outline = smooth_outline(side, face)
    body = rounded_body(outline)
    floor_cut = below_plane(FLOOR)
    hollow = prism(outline.makeOffset2D(-SHELL, join=0), -80.0, Z_RIM - DECK).cut(floor_cut)
    cavity = prism(outer_face(face.makeOffset2D(PCB_CLEAR, join=0)), -80.0, Z_RIM + 5).cut(floor_cut)
    case = body.cut(hollow).cut(cavity)
    assert case.isValid() and case.Volume < 0.5 * body.Volume, side + " shell boolean failed"

    for x, y in MOUNT[side]:
        boss = cylinder(2.0, x, -y, -40.0, 0.0).cut(cylinder(0.85, x, -y, -7.0, 0.1))
        case = case.fuse(boss.cut(below_plane(0.0)))

    ux = XIAO[side][0]
    case = case.cut(Part.makeBox(USB_W, 16.0, 20.0, V(ux - USB_W / 2, -2.0, USB_Z0)))
    zc_usb, zh = (USB_Z0 + 20.0) / 2, 20.0 - USB_Z0
    case = case.cut(frustum(V(ux, 5.5, zc_usb), (USB_W, zh), V(ux, 13.0, zc_usb), (USB_W + 9.0, zh), V(0, 1, 0)))

    sx, ky, rot = SWITCH[side]
    sdir = 1 if rot > 0 else -1
    lever_x = sx + sdir * 3.1
    case = case.cut(Part.makeBox(16.0, 11.0, 4.5, V(lever_x - 8.0, -ky - 5.5, 0.5)))
    case = case.cut(frustum(V(lever_x + sdir * 1.5, -ky, 2.75), (11.0, 4.5),
                            V(lever_x + sdir * 8.0, -ky, 2.0), (24.0, 9.0), V(sdir, 0, 0)))

    if side == "right":
        _, z_ls, z_cu, cup, _ = trackball_geometry(z_c)
        case = case.fuse(cup)
        for cut in trackball_cuts(z_c, z_ls, z_cu):
            case = case.cut(cut)
        bx, by = BALL_XY
        # floor opening for the PMW3610 body, access holes for the 4 board screws
        case = case.cut(rounded_box(bx + 3.49, by, -60, 18.0, 12.0, 60 + z_ls - SEIBOKU_T, 1.5))
        for hx, hy in SEIBOKU_HOLES:
            case = case.cut(cylinder(2.8, bx + hx, by + hy, -60, z_ls - SEIBOKU_T - 0.01))
    case = case.cut(below_plane(0.0))
    # the 3D offset can leave the top a few 0.01 mm high: trim exactly at the rim
    case = case.cut(Part.makeBox(2000, 2000, 100, V(-1000, -1000, Z_RIM))).removeSplitter()
    return case, outline


# --- main ---------------------------------------------------------------------------
def main():
    global Y_FRONT
    kb = {s: Part.read(os.path.join(KSTEP, "keyboard-v5-%s.step" % s)) for s in ("left", "right")}
    seiboku = Part.read(os.path.join(KSTEP, "seiboku-pmw3610.step"))
    pcb, face = {}, {}
    for s in kb:
        pcb[s] = max(kb[s].Solids, key=lambda x: x.BoundBox.XLength * x.BoundBox.YLength)
        top = max((f for f in pcb[s].Faces if abs(f.BoundBox.ZMin - pcb[s].BoundBox.ZMax) < 1e-3),
                  key=lambda f: f.Area)
        face[s] = Part.Face(top.OuterWire)
        face[s].translate(V(0, 0, -face[s].BoundBox.ZMin))
    Y_FRONT = min(face[s].BoundBox.YMin for s in face)

    # ball height: PMW3610 body bottom sits SENSOR_BOTTOM_CLEAR above the tilted bottom
    sensor_front_y = BALL_XY[1] - 5.45
    stack = LENS_REF_TO_BALL + PCB_TO_LENS_REF + SEIBOKU_T + SENSOR_BELOW
    z_c = z_bottom(sensor_front_y) + SENSOR_BOTTOM_CLEAR + stack + BALL_R
    log("tilt %.1f deg, bottom plane: %.2f below PCB at the front, %.2f at the back"
        % (TILT_DEG, D_FRONT, -z_bottom(max(face[s].BoundBox.YMax for s in face) + 5)))
    log("ball centre z=%.2f (PCB frame), top z=%.2f" % (z_c, z_c + BALL_R))

    doc = App.newDocument("case_v7")
    parts = {}
    for side in ("left", "right"):
        case, outline = build_case(side, face[side], z_c if side == "right" else None)
        parts["case_" + side] = case
        parts["keyboard_" + side] = kb[side]
        parts["xiao_" + side] = xiao_proxy(side)
        parts["power_switch_" + side] = switch_proxy(side)
        parts["battery_401230_" + side] = battery_proxy(side)
        parts["keycaps_" + side] = Part.makeCompound(keycap_proxies(side))
    _, z_ls, _, _, _ = trackball_geometry(z_c)
    sensor, lens = pmw3610_and_lens()
    parts["seiboku_board"] = place_seiboku(seiboku, z_ls)
    parts["pmw3610"] = place_seiboku(sensor, z_ls)
    parts["lm18_lens_envelope"] = place_seiboku(lens, z_ls)
    parts["trackball_34mm"] = Part.makeSphere(BALL_R, V(BALL_XY[0], BALL_XY[1], z_c))
    parts["trackball_collar"] = collar(z_c)
    parts["magnets_6x3"] = magnets(z_c)
    ceramics = []
    el = math.radians(CERAMIC_ELEV)
    for az in CERAMIC_AZ:
        a = math.radians(az)
        d = V(math.cos(el) * math.cos(a), math.cos(el) * math.sin(a), math.sin(el))
        ceramics.append(Part.makeSphere(CERAMIC_D / 2, V(BALL_XY[0], BALL_XY[1], z_c) + d * (BALL_R + CERAMIC_D / 2)))
    parts["ceramic_balls"] = Part.makeCompound(ceramics)

    # --- checks (PCB frame) ---
    def overlap(a, b, name):
        hits = []
        for s in (b.Solids if hasattr(b, "Solids") and b.Solids else [b]):
            if s.BoundBox.intersect(a.BoundBox):
                v = a.common(s).Volume
                if v > 0.01:
                    hits.append((round(v, 2), [round(q, 1) for q in s.BoundBox.Center]))
        log("  %-40s %s" % (name, "OK (no interference)" if not hits else "INTERFERENCE %s" % hits[:6]))

    for side in ("left", "right"):
        c = parts["case_" + side]
        log("%s case:" % side)
        for other in ("keyboard_", "xiao_", "power_switch_", "battery_401230_", "keycaps_"):
            overlap(c, parts[other + side], other + side)
    cr = parts["case_right"]
    for other in ("seiboku_board", "pmw3610", "lm18_lens_envelope", "trackball_34mm", "trackball_collar"):
        overlap(cr, parts[other], "case_right vs " + other)
    col = parts["trackball_collar"]
    for other in ("keyboard_right", "keycaps_right", "trackball_34mm", "magnets_6x3"):
        overlap(col, parts[other], "cover vs " + other)
    overlap(cr, parts["magnets_6x3"], "case_right vs magnets_6x3")
    overlap(parts["trackball_34mm"], parts["lm18_lens_envelope"], "ball vs lens")
    overlap(parts["lm18_lens_envelope"], parts["seiboku_board"], "lens vs SEIBOKU parts (expected: board cut-out only)")
    ball = parts["trackball_34mm"]
    log("  ball-to-lens gap %.2f mm, ball-to-ceramic contact gap %.3f mm" % (
        ball.distToShape(parts["lm18_lens_envelope"])[0], ball.distToShape(parts["ceramic_balls"])[0]))
    log("  ball retained: cover lip opening dia %.2f mm (< 34) at %.1f mm above the equator;"
        " ball shows %.1f mm above the cover" % (2 * COVER_LIP_R, COVER_LIP_Z, BALL_R - COVER_TOP_Z))
    log("  collar gap to ball %.2f mm" % ball.distToShape(parts["trackball_collar"])[0])

    # --- to desk frame: rotate so the bottom plane is horizontal, bottom at z=0 ---
    pivot = V(0, Y_FRONT, -D_FRONT)
    for k, s in parts.items():
        s = s.copy()
        s.rotate(pivot, V(1, 0, 0), TILT_DEG)
        s.translate(V(0, 0, D_FRONT))
        parts[k] = s
    for k, s in parts.items():
        o = doc.addObject("Part::Feature", k)
        o.Shape = s
    for side in ("left", "right"):
        bb = parts["case_" + side].optimalBoundingBox()
        c = parts["case_" + side]
        front = c.common(Part.makeBox(400, 3, 60, V(-100, bb.YMin + 3, -1))).optimalBoundingBox().ZMax
        back = c.common(Part.makeBox(400, 3, 60, V(-100, bb.YMax - 6, -1))).optimalBoundingBox().ZMax
        caps = parts["keycaps_" + side].BoundBox
        log("%s: %.1f x %.1f mm, case height front %.1f / back %.1f mm, keycap envelope top %.1f mm"
            % (side, bb.XLength, bb.YLength, front, back, caps.ZMax))
    log("right: ball top %.1f mm above desk, collar top %.1f mm"
        % (parts["trackball_34mm"].BoundBox.ZMax, parts["trackball_collar"].optimalBoundingBox().ZMax))

    for k in ("case_left", "case_right", "trackball_collar"):
        Part.export([doc.getObject(k)], os.path.join(EXPORT, "case-v7-%s.step" % k.replace("case_", "").replace("_", "-")))
        m = parts[k].tessellate(0.05)
        Mesh.Mesh([[m[0][i] for i in t] for t in m[1]]).write(
            os.path.join(EXPORT, "case-v7-%s.stl" % k.replace("case_", "").replace("_", "-")))
    doc.recompute()
    if os.path.exists(OUT):
        os.remove(OUT)
    doc.saveAs(OUT)
    open(REPORT, "w").write("\n".join(LOG) + "\n")


main()
