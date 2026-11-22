"""NORDGRIP H2 - AutoLevel: parametrisk CAD-modell (CadQuery).

Passivt gravitationsstabiliserad tvåaxlig gimbal för ölburk, buren i bälte.

Koordinatsystem (monterat, buret på höger höft):
  X = ut från höften        (pitch-axeln, kompenserar lutning framåt/bakåt)
  Y = längs bältet          (roll-axeln ligger parallellt med Y genom burkens centrum)
  Z = upp
Origo = pitch-axelns skärning med navplattans framsida. Axlarna korsar varandra
i (X0, 0, 0), dvs. i burkens centrumlinje, PIVOT_H över burkens botten.

Kör:  python3 nordgrip_h2.py [utkatalog]
"""
import json
import math
import sys
from pathlib import Path

import cadquery as cq

# ----------------------------------------------------------------- parametrar
CAN_D = 66.0            # burkdiameter
CUP_ID = 69.0           # invändig diameter
WALL = 3.5              # väggtjocklek burkhållare
CUP_RI = CUP_ID / 2
CUP_RO = CUP_RI + WALL  # 38.0
PIVOT_H = 90.0          # axelhöjd över burkens botten (hållarens innergolv)
RIM_Z = 6.0             # överkant över axlarna
FLOOR_T = 4.0
BASE_RING_H = 18.0      # hel ring nedtill
FRONT_OPEN = 120.0      # öppning framåt (grader) för enhandsgrepp
FIN_TOP = 30.0          # ryggfenans överkant (rollstopp + stöd för 50 cl)

X0 = 75.0               # burkens centrum, avstånd från navplattan
PLATE_T = 5.0
PLATE_Y = 32.0          # halv bredd
PLATE_Z0, PLATE_Z1 = -22.0, 42.0
HUB_D = 38.0
HUB_L = 19.0
B608 = (8.0, 22.0, 7.0)   # d, D, B
B625 = (5.0, 16.0, 5.0)
STOP_POST_Z = 34.5      # en stoppklack ger ±60° i pitch
STOP_POST_D = 8.0
PITCH_STOP = 60.0
ROLL_STOP = 20.0

BAR_X0, BAR_X1 = 20.0, 28.0   # okets tvärbalk
YOKE_H = 11.0                 # halv höjd
ARM_Y0, ARM_Y1 = 44.0, 52.0
PAD_Y = 42.0                  # burkhållarens lagerklack, yttre plan
BUMPER_T = 2.6                # TPU-buffert på tvärbalken -> rollstopp ±20°

BELT_W = 45.0
BELT_SLOT = 47.0
BELT_GAP = 7.0
CLIP_Y = 28.0
CLIP_FRONT_T = 6.0
CLIP_REAR_T = 3.5
KEY_W, KEY_T = 24.0, 4.6

CAP_H = 9.0
BALLAST_D, BALLAST_T = 60.0, 6.0

RHO_PETG = 1.27e-3   # g/mm3
RHO_STEEL = 7.85e-3
FIT = 0.05           # presspassning lager (justera efter skrivare)


def cyl_x(d, x0, x1, y=0.0, z=0.0):
    return (cq.Workplane("YZ").workplane(offset=x0).center(y, z)
            .circle(d / 2).extrude(x1 - x0))


def cyl_y(d, y0, y1, x=0.0, z=0.0):
    # XZ-planets normal är -Y
    return (cq.Workplane("XZ").workplane(offset=-y0).center(x, z)
            .circle(d / 2).extrude(-(y1 - y0)))


def cyl_z(d, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def wedge(a0, a1, r, z0, z1, peak=0.0):
    """Tårtbit kring burkens axel, vinklar i grader från +X. peak>0 ger 45°-topp
    (självbärande fönsteröverkant vid utskrift)."""
    n = 16
    pts = [(0.0, 0.0)] + [
        (r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
         r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    w = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    if peak > 0:
        am = (a0 + a1) / 2
        half = (a1 - a0) / 2
        steps = 8
        for i in range(1, steps + 1):
            f = 1 - i / steps
            pts2 = [(0.0, 0.0)] + [
                (r * math.cos(math.radians(am - half * f + 2 * half * f * k / n)),
                 r * math.sin(math.radians(am - half * f + 2 * half * f * k / n)))
                for k in range(n + 1)]
            if f <= 0.02:
                break
            w = w.union(cq.Workplane("XY").workplane(offset=z1 + peak * (i - 1) / steps)
                        .polyline(pts2).close().extrude(peak / steps))
    return w.translate((X0, 0, 0))


# ------------------------------------------------------------------- delar
def hub_plate():
    p = box(-PLATE_T, 0, -PLATE_Y, PLATE_Y, PLATE_Z0, PLATE_Z1)
    p = p.edges("|X").chamfer(7.0)
    p = p.union(cyl_x(HUB_D, 0, HUB_L))
    p = p.union(cyl_x(HUB_D + 10, 0, 2.5))                       # fot
    p = p.union(cyl_x(STOP_POST_D, 0, BAR_X1 - 1, 0, STOP_POST_Z))
    p = p.union(cyl_x(STOP_POST_D + 8, 0, 3.0, 0, STOP_POST_Z))  # fot till klack
    p = p.cut(cyl_x(B608[1] + FIT, 3.0, HUB_L + 1))              # lagersäte 2x608
    p = p.cut(cyl_x(15.0, -PLATE_T - 1, 3.0))                    # skruvskalle
    for y, z in SCREW_POS:
        p = p.cut(cyl_x(3.4, -PLATE_T - 1, 1, y, z))
        p = p.cut(cq.Workplane("YZ").workplane(offset=0).center(y, z)
                  .circle(3.3).workplane(offset=-1.9).circle(1.7).loft())
    p = p.cut(box(-PLATE_T - 1, 1, -KEY_W / 2 - 0.3, KEY_W / 2 + 0.3, PLATE_Z0 - 1, KEY_Z1 + 0.3)
              ) if KEY_Z1 > PLATE_Z0 else p
    return p


KEY_Z1 = -BELT_SLOT / 2          # låsregelns ovansida = bältesspårets botten
KEY_Z0 = KEY_Z1 - KEY_T - 0.4
CLIP_Z0, CLIP_Z1 = KEY_Z0 - 6.0, BELT_SLOT / 2 + 6.5
SCREW_POS = [(-24, -14), (24, -14), (-24, 22), (24, 22)]
XF = -PLATE_T                     # klämmans framsida
XG0 = XF - CLIP_FRONT_T           # bältesspår fram
XG1 = XG0 - BELT_GAP              # bältesspår bak
XR = XG1 - CLIP_REAR_T            # mot kroppen


def belt_clip():
    c = box(XR, XF, -CLIP_Y, CLIP_Y, CLIP_Z0, CLIP_Z1)
    c = c.edges("|Y").chamfer(2.0)
    c = c.cut(box(XG1, XG0, -CLIP_Y - 1, CLIP_Y + 1, CLIP_Z0 - 1, BELT_SLOT / 2))
    # låsregelns genomgång
    c = c.cut(box(XR - 1, XF + 1, -KEY_W / 2 - 0.3, KEY_W / 2 + 0.3, KEY_Z0, KEY_Z1))
    for y, z in SCREW_POS:                                        # M3 gänginsatser
        c = c.cut(cyl_x(4.0, XF - 5.2, XF + 1, y, z))
    return c


def lock_key():
    k = box(XR - 3.0, XF, -KEY_W / 2, KEY_W / 2, KEY_Z0 + 0.2, KEY_Z1 - 0.2)
    k = k.union(box(XF, XF + 3.0, -KEY_W / 2 - 4, KEY_W / 2 + 4, KEY_Z0 - 4.0, KEY_Z1 - 0.2))
    # snäpphake bakom bakre tungan
    k = k.union(box(XR - 3.0, XR - 0.4, -KEY_W / 2, KEY_W / 2, KEY_Z0 - 1.2, KEY_Z0 + 0.3))
    k = k.cut(box(XR - 4, XG0 - 1, -1.0, 1.0, KEY_Z0 - 2, KEY_Z1))   # fjädrande slits
    return k


def yoke():
    pts = [(BAR_X0, -ARM_Y1 + 6), (BAR_X0 + 6, -ARM_Y1), (X0, -ARM_Y1),
           (X0, -ARM_Y0), (BAR_X1 + 6, -ARM_Y0), (BAR_X1, -ARM_Y0 + 6),
           (BAR_X1, ARM_Y0 - 6), (BAR_X1 + 6, ARM_Y0), (X0, ARM_Y0),
           (X0, ARM_Y1), (BAR_X0 + 6, ARM_Y1), (BAR_X0, ARM_Y1 - 6)]
    y = (cq.Workplane("XY").workplane(offset=-YOKE_H).polyline(pts).close()
         .extrude(2 * YOKE_H))
    for s in (-1, 1):
        y0, y1 = (ARM_Y0, ARM_Y1) if s > 0 else (-ARM_Y1, -ARM_Y0)
        y = y.union(cyl_y(2 * YOKE_H, y0, y1, X0, 0))                  # lagerhus
    y = y.edges("|Y").edges("not %CIRCLE").chamfer(1.2) if False else y
    y = y.cut(cyl_x(8.2, BAR_X0 - 1, BAR_X1 + 1))                      # M8
    y = y.cut(cyl_x(17.0, BAR_X1 - 3.0, BAR_X1 + 1))                   # mutterförsänkning
    for s in (-1, 1):
        if s > 0:
            y = y.cut(cyl_y(B625[1] + FIT, ARM_Y1 - B625[2], ARM_Y1 + 1, X0, 0))
            y = y.cut(cyl_y(10.0, ARM_Y0 - 1, ARM_Y1, X0, 0))
        else:
            y = y.cut(cyl_y(B625[1] + FIT, -ARM_Y1 - 1, -ARM_Y1 + B625[2], X0, 0))
            y = y.cut(cyl_y(10.0, -ARM_Y1, -ARM_Y0 + 1, X0, 0))
    # lättningsfickor i armarna (geometriskt uttryck, sparar material)
    for s in (-1, 1):
        yy = s * (ARM_Y1 - 1.2) if s > 0 else -ARM_Y1 - 0.01
        pocket = box(BAR_X1 + 8, X0 - 14, 0, 1.21, -5.5, 5.5).translate(
            (0, ARM_Y1 - 1.2 if s > 0 else -ARM_Y1 - 0.01, 0))
        y = y.cut(pocket)
    # logotyp, försänkt i lättningsfickornas botten
    try:
        tx = (BAR_X1 + 10 + X0 - 16) / 2
        txt = cq.Workplane("XZ").text("NORDGRIP", 3.7, 0.6, kind="bold", halign="center", valign="center")
        y = y.cut(txt.translate((tx, -ARM_Y1 + 1.2 + 0.6, 0)))
        txt2 = (cq.Workplane("XZ").transformed(rotate=(0, 180, 0))
                .text("NORDGRIP", 3.7, 0.6, kind="bold", halign="center", valign="center"))
        y = y.cut(txt2.translate((tx, ARM_Y1 - 1.2 - 0.6, 0)))
    except Exception as e:  # typsnitt saknas -> hoppa över logotyp
        print("logotyp hoppades över:", e)
    return y


def bumpers():
    b = box(BAR_X1, BAR_X1 + BUMPER_T, -14, 14, YOKE_H - 6, YOKE_H)
    b = b.union(box(BAR_X1, BAR_X1 + BUMPER_T, -14, 14, -YOKE_H, -YOKE_H + 6))
    return b


def stop_sleeve():
    """O-ring/TPU-hylsa på pitchstoppet."""
    return cyl_x(STOP_POST_D + 4, BAR_X0 - 1, BAR_X1 - 1, 0, STOP_POST_Z).cut(
        cyl_x(STOP_POST_D, BAR_X0 - 2, BAR_X1, 0, STOP_POST_Z))


def cup():
    z0 = -PIVOT_H - FLOOR_T
    c = cyl_z(2 * CUP_RO, z0, RIM_Z).translate((X0, 0, 0))
    c = c.faces("<Z").edges().chamfer(2.0)
    # ryggfena
    fin = cyl_z(2 * CUP_RO, RIM_Z, FIN_TOP).translate((X0, 0, 0)).intersect(
        wedge(162, 198, 60, RIM_Z - 1, FIN_TOP + 1))
    c = c.union(fin)
    # lagerklackar ±Y, 45° undertill -> skrivs utan stöd
    for s in (-1, 1):
        pad = (cq.Workplane("XZ").polyline(
            [(-11, 11), (11, 11), (11, -11), (6, -11 - (PAD_Y - CUP_RO + 5)), (-6, -11 - (PAD_Y - CUP_RO + 5)), (-11, -11)])
            .close().extrude(-PAD_Y))                    # 0..PAD_Y i +Y
        pad = pad.cut(box(-12, 12, PAD_Y - 100, CUP_RO - 5.5, -40, 20)) if False else pad
        slope = (cq.Workplane("YZ").polyline(
            [(CUP_RO - 1.0, -11 - (PAD_Y - CUP_RO + 5.5)), (CUP_RO - 1.0, 12), (PAD_Y, 12), (PAD_Y, -11)])
            .close().extrude(24).translate((-12, 0, 0)))
        pad = pad.intersect(slope)
        if s < 0:
            pad = pad.mirror("XZ")
        c = c.union(pad.translate((X0, 0, 0)))
    c = c.cut(cyl_z(CUP_ID, -PIVOT_H, FIN_TOP + 5).translate((X0, 0, 0)))
    # öppen front för enhandsgrepp
    c = c.cut(wedge(-FRONT_OPEN / 2, FRONT_OPEN / 2, 60, -PIVOT_H + BASE_RING_H, FIN_TOP + 5))
    # ventilationsfönster bak
    for a0, a1 in ((116, 160), (200, 244)):
        c = c.cut(wedge(a0, a1, 60, -PIVOT_H + BASE_RING_H, -30, peak=16))
    # gänginsatser M5 för lagertappar
    for s in (-1, 1):
        c = c.cut(cyl_y(6.4, CUP_RI - 1, PAD_Y + 1, X0, 0) if s > 0 else
                  cyl_y(6.4, -PAD_Y - 1, -CUP_RI + 1, X0, 0))
    # dränering/ventilation i golvet + skruvhål för ballastlock
    c = c.cut(cyl_z(24, z0 - 1, -PIVOT_H + 1).translate((X0, 0, 0)))
    for i in range(3):
        a = math.radians(90 + 120 * i + 60)
        c = c.cut(cyl_z(2.6, z0 - 1, -PIVOT_H + 1, X0 + 33.0 * math.cos(a), 33.0 * math.sin(a)))
    return c


def ballast_cap():
    z1 = -PIVOT_H - FLOOR_T
    z0 = z1 - CAP_H
    c = cyl_z(2 * CUP_RO, z0, z1)
    c = c.faces("<Z").edges().chamfer(3.0)
    c = c.cut(cyl_z(BALLAST_D + 1.0, z1 - BALLAST_T - 0.3, z1 + 1))
    c = c.translate((X0, 0, 0))
    for i in range(3):
        a = math.radians(90 + 120 * i + 60)
        x, y = X0 + 33.0 * math.cos(a), 33.0 * math.sin(a)
        c = c.cut(cyl_z(3.4, z0 - 1, z1 + 1, x, y))
        c = c.cut(cyl_z(6.5, z0 - 1, z0 + 3.0, x, y))
    return c


def ballast():
    z1 = -PIVOT_H - FLOOR_T - 0.2
    return cyl_z(BALLAST_D, z1 - BALLAST_T, z1).translate((X0, 0, 0))


def bearing(spec, axis, pos0):
    d, D, B = spec
    if axis == "x":
        return cyl_x(D, pos0, pos0 + B).cut(cyl_x(d, pos0 - 1, pos0 + B + 1))
    y0 = pos0
    return cyl_y(D, y0, y0 + B, X0, 0).cut(cyl_y(d, y0 - 1, y0 + B + 1, X0, 0))


def hardware():
    """Axlar, lager och fästelement (visualisering + stycklista)."""
    parts = {}
    b = bearing(B608, "x", 3.0).union(bearing(B608, "x", 12.0))
    b = b.union(bearing(B625, "y", ARM_Y1 - 5)).union(bearing(B625, "y", -ARM_Y1))
    parts["bearings"] = b
    # pitchaxel: M8x35 låghuvad insexskruv + distanser + låsmutter
    ax = cyl_x(8.0, -3.0, 34.0).union(cyl_x(13.0, -3.0, 2.0))
    ax = ax.union(cyl_x(11.5, 2.0, 3.0)).union(cyl_x(11.5, 10.0, 12.0)).union(cyl_x(11.5, 19.0, 20.0))
    nut = (cq.Workplane("YZ").workplane(offset=BAR_X1 - 3.0).polygon(6, 15.0).extrude(8.0)
           .cut(cyl_x(8.0, 20, 40)))
    ax = ax.union(nut)
    # rolltappar: M5x16 kullrig skruv + distanshylsa 5x8x5
    for s in (-1, 1):
        if s > 0:
            t = cyl_y(5.0, CUP_RO - 2, ARM_Y1).union(cyl_y(9.5, ARM_Y1, ARM_Y1 + 2.7))
            t = t.union(cyl_y(8.0, PAD_Y, ARM_Y1 - 5).cut(cyl_y(5.0, PAD_Y - 1, ARM_Y1)))
        else:
            t = cyl_y(5.0, -ARM_Y1, -CUP_RO + 2).union(cyl_y(9.5, -ARM_Y1 - 2.7, -ARM_Y1))
            t = t.union(cyl_y(8.0, -ARM_Y1 + 5, -PAD_Y).cut(cyl_y(5.0, -ARM_Y1, -PAD_Y + 1)))
        ax = ax.union(t.translate((X0, 0, 0)) if False else _shift_y_part(t))
    parts["axles"] = ax
    return parts


def _shift_y_part(t):
    # cyl_y utan x-argument ligger i x=0 -> flytta till burkens axel
    return t.translate((X0, 0, 0))


def can(height=168.0):
    z0 = -PIVOT_H
    body = cyl_z(CAN_D, z0 + 6, z0 + height - 12)
    bot = (cq.Workplane("XY").workplane(offset=z0).circle(25).workplane(offset=6)
           .circle(CAN_D / 2).loft())
    top = (cq.Workplane("XY").workplane(offset=z0 + height - 12).circle(CAN_D / 2)
           .workplane(offset=11).circle(27).loft())
    lid = cyl_z(54, z0 + height - 1.5, z0 + height).cut(cyl_z(50, z0 + height - 1, z0 + height + 1))
    return body.union(bot).union(top).union(lid).translate((X0, 0, 0))


def belt():
    return box(XG1 + 1.5, XG0 - 1.5, -150, 150, -BELT_W / 2, BELT_W / 2)


# --------------------------------------------------------------- beräkning
def props(wp, rho):
    s = wp.val()
    com = cq.Shape.centerOfMass(s)
    return s.Volume() * rho, (com.x, com.y, com.z)


def analysis(parts):
    """Tyngdpunkt för den pendlande massan relativt axlarna (z=0)."""
    infill = 0.75  # effektiv fyllnadsfaktor för PETG-delarna (4 perimetrar, 25 % gyroid)
    m_cup, c_cup = props(parts["cup"], RHO_PETG * infill)
    m_cap, c_cap = props(parts["ballast_cap"], RHO_PETG * infill)
    m_bal, c_bal = props(parts["ballast"], RHO_STEEL)
    m_yoke, c_yoke = props(parts["yoke"], RHO_PETG * infill)
    out = {"massa_g": {"burkhållare": round(m_cup, 1), "ballastlock": round(m_cap, 1),
                       "ballast_stål": round(m_bal, 1), "ok": round(m_yoke, 1)}}
    cases = {
        "50 cl full": (515.0, 80.0, 160.0),     # massa g, tp över botten, höjd
        "50 cl halv": (265.0, 42.0, 160.0),
        "33 cl full": (345.0, 56.0, 110.0),
        "tom hållare": (0.0, 0.0, 0.0),
    }
    res = {}
    for name, (mc, hc, hh) in cases.items():
        for bal in (True, False):
            items = [(m_cup, c_cup[2]), (m_cap, c_cap[2])]
            if bal:
                items.append((m_bal, c_bal[2]))
            if mc:
                items.append((mc, -PIVOT_H + hc))
            m = sum(i[0] for i in items)
            zc = sum(i[0] * i[1] for i in items) / m
            # tröghetsmoment kring rollaxeln (grov: punktmassor + burk som stav)
            I = sum(i[0] * i[1] ** 2 for i in items)
            if mc:
                I += mc * (3 * 33.0 ** 2 + hh ** 2) / 12.0
            I += m_cup * (38.0 ** 2 / 2 + 100.0 ** 2 / 12)
            f = math.sqrt(m * 9810.0 * (-zc) / I) / (2 * math.pi) if zc < 0 else float("nan")
            res[f"{name}{'' if bal else ' (utan ballast)'}"] = {
                "pendlande_massa_g": round(m), "tp_under_axel_mm": round(-zc, 1),
                "egenfrekvens_Hz": round(f, 2)}
    out["stabilitet"] = res
    return out


def build():
    parts = {
        "hub_plate": hub_plate(),
        "belt_clip": belt_clip(),
        "lock_key": lock_key(),
        "yoke": yoke(),
        "bumpers": bumpers(),
        "stop_sleeve": stop_sleeve(),
        "cup": cup(),
        "ballast_cap": ballast_cap(),
        "ballast": ballast(),
    }
    parts.update(hardware())
    parts["can50"] = can(168.0)
    parts["can33"] = can(115.0)
    parts["belt"] = belt()
    return parts


# utskriftsorientering: (axel, vinkel) så att delen står på byggplattan utan stöd
PRINT_ORIENT = {
    "hub_plate": ((0, 1, 0), -90),    # baksidan mot plattan, lagersäte vertikalt
    "belt_clip": ((1, 0, 0), 90),     # på sidan, J-profilen extruderas uppåt
    "lock_key": ((0, 1, 0), 90),
    "yoke": None,                     # plant, som monterat
    "cup": None,                      # stående på botten
    "ballast_cap": ((1, 0, 0), 180),  # ballastfickan uppåt
    "bumpers": ((0, 1, 0), -90),      # TPU
    "stop_sleeve": ((0, 1, 0), -90),  # TPU
}

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    (out / "assembly").mkdir(parents=True, exist_ok=True)
    (out / "print").mkdir(parents=True, exist_ok=True)
    parts = build()
    asm = cq.Assembly()
    for n, p in parts.items():
        cq.exporters.export(p, str(out / "assembly" / f"{n}.stl"), tolerance=0.02, angularTolerance=0.15)
        if n not in ("can50", "can33", "belt"):
            asm.add(p, name=n)
    (out / "section").mkdir(exist_ok=True)
    half = box(-200, 300, 0, 300, -300, 300)
    for n, p in parts.items():
        if n in ("can50", "belt"):
            continue
        cq.exporters.export(p.intersect(half), str(out / "section" / f"{n}.stl"), tolerance=0.02, angularTolerance=0.15)
    asm.save(str(out / "nordgrip_h2_assembly.step"))
    for n, rot in PRINT_ORIENT.items():
        p = parts[n]
        if rot:
            p = p.rotate((0, 0, 0), rot[0], rot[1])
        bb = p.val().BoundingBox()
        p = p.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
        cq.exporters.export(p, str(out / "print" / f"{n}.stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(p, str(out / "print" / f"{n}.step"))
        bb = p.val().BoundingBox()
        print(f"{n:12s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm")
    a = analysis(parts)
    (out / "analysis.json").write_text(json.dumps(a, indent=2, ensure_ascii=False))
    print(json.dumps(a, indent=2, ensure_ascii=False))
