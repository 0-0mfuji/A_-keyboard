"""Rounded case for keyboard_v5 PCBs with a 34 mm trackball on the right half.

Run headless:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd hardware/freecad/build_rounded_case.py

Reads the PCB / plate solids from keyboard_v5_assembly.FCStd and writes
case_v6_rounded.FCStd plus STEP/STL files to hardware/step-export/.

Z reference (same as the assembly): PCB 0..1.51, plate 5.01..6.51.
"""
import math
import os

import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "keyboard_v5_assembly.FCStd")
OUT = os.path.join(HERE, "case_v6_rounded.FCStd")
EXPORT = os.path.join(HERE, "..", "step-export")

V = App.Vector

# --- case parameters -------------------------------------------------------
Z_BOTTOM = -17.0        # case underside
FLOOR = 2.0
Z_FLOOR = Z_BOTTOM + FLOOR
Z_RIM = 8.5             # top of the bezel (plate top is 6.51)
DECK = 2.5              # top skin thickness around the keys / trackball
SHELL = 2.5             # side wall thickness
PCB_CLEAR = 0.5         # PCB outline -> cavity
OUTER_OFFSET = 5.0      # PCB outline -> outside of case
SMOOTH_R = 30.0         # closing radius that fills notches in the silhouette
TAUBIN_POINTS = 120     # ~5 mm samples: the filter removes waves under ~60 mm
TAUBIN_ITERS = 150
MIN_OUTER = 4.5         # minimum PCB outline -> outside distance after smoothing
FILLET_TOP = 3.0

# --- trackball / PMW3610 (SEIBOKU breakout) ---------------------------------
BALL_D = 34.0
BALL_R = BALL_D / 2
BALL_XY = V(248.0, -104.0, 0)       # right of the right-hand thumb cluster
SENSOR_BOARD_T = 1.6
LENS_HEIGHT = 4.0                   # board top -> lens reference plane (SEIBOKU README)
LENS_TO_BALL = 2.4                  # PMW3610 lens -> tracking surface
Z_SENSOR_TOP = -10.4                # sensor board top surface
Z_BALL = Z_SENSOR_TOP + LENS_HEIGHT + LENS_TO_BALL + BALL_R   # ball centre
CUP_GAP = 1.0                       # ball -> spherical pocket
CUP_R = 21.0                        # outer radius of the ball cup
Z_CUP_BOTTOM = Z_SENSOR_TOP + 1.9
BEARING_D = 3.0                     # static ZrO2 / steel support balls
BEARING_ELEV = -40.0                # degrees below the ball equator
BEARING_AZ = (30.0, 150.0, 270.0)
BEZEL_R = 23.0
Z_BEZEL = 11.0
SENSOR_HOLES = [(sx * 13.0, sy * 8.0) for sx in (-1, 1) for sy in (-1, 1)]

# PCB mounting holes (KiCad coords, y flipped for FreeCAD)
MOUNT = {
    "left": [(21.15, 38.6075), (82.65, 96.0075), (148.25, 26.3075)],
    "right": [(304.9068, 60.1075), (231.1068, 72.4075), (181.9068, 35.5075)],
}
USB_X = {"left": 148.6125, "right": 180.045}
USB_W = 14.0            # notch width for the USB-C plug overmold
USB_Z0 = 0.3            # notch floor
# MSK12C02 slide switch: lever exits the inner side wall
SWITCH = {"left": (160.1, -30.49, +1), "right": (169.9, -30.5, -1)}


def pcb_face(keyboard_shape):
    pcb = max(keyboard_shape.Solids, key=lambda s: s.BoundBox.XLength * s.BoundBox.YLength)
    top = max((f for f in pcb.Faces if abs(f.BoundBox.ZMin - pcb.BoundBox.ZMax) < 1e-3),
              key=lambda f: f.Area)
    face = Part.Face(top.OuterWire)
    face.translate(V(0, 0, -face.BoundBox.ZMin))
    return pcb, face


def outer_face(shape):
    shape = shape.removeSplitter()
    faces = shape.Faces
    face = max(faces, key=lambda f: f.Area)
    return Part.Face(face.OuterWire)


def smooth_bspline_face(face, step=5.0):
    """Replace a many-edge outline by one periodic B-spline (clean fillets)."""
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
    """Taubin (lambda/mu) smoothing: irons out column stagger without shrinking."""
    pts = [(p.x, p.y) for p in face.OuterWire.discretize(Number=n + 1)[:-1]]
    for _ in range(iters):
        for f in (lam, mu):
            pts = [(x + f * ((pts[i - 1][0] + pts[(i + 1) % n][0]) / 2 - x),
                    y + f * ((pts[i - 1][1] + pts[(i + 1) % n][1]) / 2 - y))
                   for i, (x, y) in enumerate(pts)]
    out = [V(x, y, 0) for x, y in pts]
    return Part.Face(Part.makePolygon(out + out[:1]))


def smooth_outline(side, face):
    """Soft, low-step silhouette that still keeps MIN_OUTER around the PCB."""
    keep = face.makeOffset2D(MIN_OUTER, join=0)
    grown = face.makeOffset2D(OUTER_OFFSET + SMOOTH_R, join=0)
    if side == "right":
        keep = keep.fuse(disk(BALL_XY, CUP_R + SHELL + 1.5))
        grown = grown.fuse(disk(BALL_XY, CUP_R + SHELL + 1.5 + SMOOTH_R))
    closed = outer_face(outer_face(grown).makeOffset2D(-SMOOTH_R, join=0))
    soft = taubin_smooth_face(closed)
    # push the filtered outline back out wherever it cut into the keep-out band
    grow = 0.0
    for w in keep.Wires:
        for p in w.discretize(Distance=1.0):
            if not soft.isInside(p, 1e-4, True):
                grow = max(grow, soft.OuterWire.distToShape(Part.Vertex(p))[0])
    if grow:
        soft = outer_face(soft.makeOffset2D(grow + 0.1, join=0))
    return smooth_bspline_face(soft)


def rounded_body(outline):
    """Extruded outline with round top/bottom edges (3D offset of an inset prism)."""
    r = FILLET_TOP
    core = prism(outer_face(outline.makeOffset2D(-r, join=0)), Z_BOTTOM + r, Z_RIM - r)
    for tol in (0.01, 0.05, 0.1):
        try:
            return core.makeOffsetShape(r, tol, join=0, fill=False)
        except Exception:
            pass
    raise RuntimeError("rounded body offset failed")


def disk(center, r):
    return Part.Face(Part.Wire([Part.makeCircle(r, V(center.x, center.y, 0))]))


def prism(face, z0, z1):
    f = face.copy()
    f.translate(V(0, 0, z0))
    return f.extrude(V(0, 0, z1 - z0))


def rounded_box(cx, cy, z0, sx, sy, sz, r):
    b = Part.makeBox(sx, sy, sz, V(cx - sx / 2, cy - sy / 2, z0))
    vert = [e for e in b.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99]
    return b.makeFillet(r, vert) if r > 0 else b


def frustum(c0, size0, c1, size1, axis):
    """Ruled loft between two rectangles normal to a horizontal axis.
    size = (width across the axis in XY, height in Z)."""
    side = V(-axis.y, axis.x, 0)
    def rect(c, size):
        w, h = size[0] / 2, size[1] / 2
        up = V(0, 0, 1)
        pts = [c + side * w + up * h, c - side * w + up * h,
               c - side * w - up * h, c + side * w - up * h]
        return Part.makePolygon(pts + pts[:1])
    return Part.makeLoft([rect(c0, size0), rect(c1, size1)], True, True)


def cylinder(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def trackball_cup():
    c = BALL_XY
    ball_c = V(c.x, c.y, Z_BALL)
    cup = cylinder(CUP_R, c.x, c.y, Z_CUP_BOTTOM, Z_RIM - DECK + 0.01)
    # hang the sensor board from the cup so the lens stays aligned to the ball
    for hx, hy in SENSOR_HOLES:
        cup = cup.fuse(cylinder(2.3, c.x + hx, c.y + hy, Z_SENSOR_TOP, Z_CUP_BOTTOM + 0.01))
    cup = cup.cut(Part.makeSphere(BALL_R + CUP_GAP, ball_c))
    cup = cup.cut(cylinder(BALL_R + CUP_GAP, c.x, c.y, Z_BALL, Z_BALL + 30))
    # lens window
    cup = cup.cut(rounded_box(c.x, c.y, Z_CUP_BOTTOM - 1, 13.0, 13.0, 12, 1.0))
    # 2x4 header on the -x side of the SEIBOKU board
    cup = cup.cut(Part.makeBox(6.5, 11.0, 9.0, V(c.x - 15.0, c.y - 5.5, Z_CUP_BOTTOM - 1)))
    for hx, hy in SENSOR_HOLES:   # M2 self-tapping, screwed from below
        cup = cup.cut(cylinder(0.85, c.x + hx, c.y + hy, Z_SENSOR_TOP - 1, Z_CUP_BOTTOM + 5))
    # support-ball pockets, axis through the ball centre
    for az in BEARING_AZ:
        el = math.radians(BEARING_ELEV)
        d = V(math.cos(el) * math.cos(math.radians(az)),
              math.cos(el) * math.sin(math.radians(az)),
              math.sin(el))
        start = ball_c + d * (BALL_R - 0.5)
        cup = cup.cut(Part.makeCylinder(BEARING_D / 2 + 0.03, 4.0, start, d))
    return cup


def bezel_ring():
    c = BALL_XY
    ring = cylinder(BEZEL_R, c.x, c.y, Z_RIM - 0.5, Z_BEZEL).cut(
        cylinder(BALL_R + CUP_GAP, c.x, c.y, Z_RIM - 1, Z_BEZEL + 1))
    top = [e for e in ring.Edges if abs(e.BoundBox.ZMin - Z_BEZEL) < 1e-6]
    return ring.makeFillet(1.2, top)


def build_case(side, keyboard_shape):
    pcb, face = pcb_face(keyboard_shape)
    outline = smooth_outline(side, face)
    body = rounded_body(outline)

    hollow = prism(outline.makeOffset2D(-SHELL, join=0), Z_FLOOR, Z_RIM - DECK)
    cavity_face = outer_face(face.makeOffset2D(PCB_CLEAR, join=0))
    cavity = prism(cavity_face, Z_FLOOR, Z_RIM + 5)
    case = body.cut(hollow).cut(cavity)
    assert case.isValid() and 0.05 * body.Volume < case.Volume < 0.5 * body.Volume, \
        "%s shell boolean failed" % side

    # PCB standoffs, M2 self-tapping screws (0603 parts sit 2.2 mm from the hole)
    for x, y in MOUNT[side]:
        boss = cylinder(2.0, x, -y, Z_FLOOR - 0.01, 0.0)
        boss = boss.cut(cylinder(0.85, x, -y, -7.0, 0.1))
        case = case.fuse(boss)

    # USB-C (XIAO) on the back wall: open-top notch
    ux = USB_X[side]
    case = case.cut(Part.makeBox(USB_W, 16.0, 20.0, V(ux - USB_W / 2, -2.0, USB_Z0)))
    # flared mouth so wide / thick plug overmolds still seat
    zc, zh = (USB_Z0 + 20.0) / 2, 20.0 - USB_Z0
    case = case.cut(frustum(V(ux, 5.5, zc), (USB_W, zh),
                            V(ux, 13.0, zc), (USB_W + 9.0, zh), V(0, 1, 0)))

    # power switch window
    sx, sy, sdir = SWITCH[side]
    case = case.cut(Part.makeBox(16.0, 11.0, 4.5, V(sx - 8.0, sy - 5.5, 0.5)))
    # outer finger chamfer: window grows ~45 deg sideways toward the outside
    case = case.cut(frustum(V(sx + sdir * 1.5, sy, 2.75), (11.0, 4.5),
                            V(sx + sdir * 8.0, sy, 2.0), (24.0, 9.0), V(sdir, 0, 0)))

    if side == "right":
        case = case.fuse(trackball_cup()).fuse(bezel_ring())
        c = BALL_XY
        case = case.cut(cylinder(BALL_R + CUP_GAP, c.x, c.y, Z_BALL, Z_BALL + 30))
        case = case.cut(Part.makeSphere(BALL_R + CUP_GAP, V(c.x, c.y, Z_BALL)))
        for hx, hy in SENSOR_HOLES:   # screwdriver access from underneath
            case = case.cut(cylinder(2.6, c.x + hx, c.y + hy, Z_BOTTOM - 1, Z_FLOOR + 0.01))

    case = case.removeSplitter()
    return case, pcb, outline


def sensor_proxy():
    c = BALL_XY
    board = rounded_box(c.x, c.y, Z_SENSOR_TOP - SENSOR_BOARD_T, 30.0, 20.0, SENSOR_BOARD_T, 2.0)
    for hx, hy in SENSOR_HOLES:
        board = board.cut(cylinder(1.1, c.x + hx, c.y + hy, Z_SENSOR_TOP - 3, Z_SENSOR_TOP + 1))
    lens = rounded_box(c.x, c.y, Z_SENSOR_TOP, 10.0, 10.0, LENS_HEIGHT, 1.0)
    chip = Part.makeBox(9.0, 9.0, 2.0, V(c.x - 4.5, c.y - 4.5, Z_SENSOR_TOP - SENSOR_BOARD_T - 2.0))
    header = Part.makeBox(5.08, 10.16, 8.5, V(c.x - 14.27, c.y - 5.3, Z_SENSOR_TOP))
    return board.fuse([lens, chip, header])


def main():
    src = App.openDocument(SRC)
    if os.path.exists(OUT):
        os.remove(OUT)
    doc = App.newDocument("case_v6_rounded")
    report = []
    for side in ("left", "right"):
        kb = src.getObject("keyboard_" + side).Shape
        case, pcb, outline = build_case(side, kb)
        assert case.isValid(), side + " case invalid"
        doc.addObject("Part::Feature", "case_" + side).Shape = case
        doc.addObject("Part::Feature", "pcb_" + side).Shape = pcb
        doc.addObject("Part::Feature", "plate_" + side).Shape = src.getObject("plate_" + side).Shape
        # interference against every PCB-assembly solid
        hits = []
        for s in kb.Solids:
            if s.BoundBox.intersect(case.BoundBox):
                v = case.common(s).Volume
                if v > 0.01:
                    hits.append((round(v, 2), [round(x, 1) for x in (s.BoundBox.Center.x, s.BoundBox.Center.y, s.BoundBox.Center.z)]))
        bb = case.BoundBox
        report.append("%s: %.1f x %.1f x %.1f mm, volume %.0f mm3, interference %s" % (
            side, bb.XLength, bb.YLength, bb.ZLength, case.Volume, hits or "none"))
        Part.export([doc.getObject("case_" + side)], os.path.join(EXPORT, "case-rounded-%s.step" % side))
        mesh = case.tessellate(0.05)
        import Mesh
        Mesh.Mesh([[mesh[0][i] for i in tri] for tri in mesh[1]]).write(
            os.path.join(EXPORT, "case-rounded-%s.stl" % side))

    ball = Part.makeSphere(BALL_R, V(BALL_XY.x, BALL_XY.y, Z_BALL))
    doc.addObject("Part::Feature", "trackball_34mm").Shape = ball
    doc.addObject("Part::Feature", "pmw3610_seiboku").Shape = sensor_proxy()
    case_r = doc.getObject("case_right").Shape
    report.append("ball vs case: %.3f mm3, sensor vs case: %.3f mm3" % (
        case_r.common(ball).Volume, case_r.common(doc.getObject("pmw3610_seiboku").Shape).Volume))
    report.append("ball centre z=%.2f, top z=%.2f, bottom z=%.2f" % (
        Z_BALL, Z_BALL + BALL_R, Z_BALL - BALL_R))
    doc.recompute()
    doc.saveAs(OUT)
    print("\n".join(report))


main()
