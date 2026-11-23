"""Watt?! Video 14: Richtig messen (Spannung, Strom, Widerstand, Messbereich). Eine Klasse pro Abschnitt (Szene01 = s01 ...).
Rendern (Probe): WATT_CUES=stimme/cues.json $VENV/bin/manim -ql --fps 30 --disable_caching video14_messen.py SzeneNN
Rendern (final): WATT_CUES=stimme/cues.json $VENV/bin/manim -r 2560,1440 --fps 60 --disable_caching video14_messen.py SzeneNN
Hinweis: In den Cues steht "Ampär" und Kommazahlen zusammengeschrieben ("nullkommaeins"); bis_wort nie auf "Ampere".
Roter Faden: Multimeter an der Steckdose, rote Messleitung in der 10-A-Buchse, es knallt. Metapher: Wasserleitung mit
Manometer (seitlich, Spannung) und Wasseruhr (im Rohr, Strom). Keine Personen, keine Hand im Bild.
Folientitel unter dem kleinen Logo bei y = 1.55 (PROZESS, V9).
"""
import sys
from pathlib import Path
sys.path.insert(0, "/mnt/project-files/youtube-kanal/werkzeuge")
from watt_manim import *

setze_sprechtext(Path(__file__).with_name("video14_sprechtext.txt"))

ORANGE = "#FF8A3D"
ROT_HELL = "#F2545B"
WASSER = "#4FC3E0"
ROHR = "#8A97A5"
ROHR_D = "#55606C"
GRUEN = "#5FCB6E"
METALL = "#C3CDD8"
DISPLAY = "#0B2A1E"
GEHAEUSE = "#1E2B38"


# --- allgemeine Bausteine (wie Video 9/12/13) ---------------------------------------------------
def karte(inhalt, farbe=GELB, pad=0.35):
    r = RoundedRectangle(width=inhalt.width + 2 * pad, height=inhalt.height + 2 * pad, corner_radius=0.18,
                         stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(inhalt)
    return VGroup(r, inhalt)


def badge(text, farbe=GELB, textfarbe=NAVY, size=40, markup=False):
    t = MT(text, size, textfarbe, HEAVY) if markup else T(text, size, textfarbe, HEAVY)
    return VGroup(RoundedRectangle(width=t.width + 0.5, height=t.height + 0.35, corner_radius=0.25, stroke_width=0,
                                   fill_color=farbe, fill_opacity=1), t)


def ergebnis(text, size=60, markup=False):
    t = MT(text, size, NAVY, HEAVY) if markup else T(text, size, NAVY, HEAVY)
    return VGroup(RoundedRectangle(width=t.width + 0.6, height=t.height + 0.45, corner_radius=0.2, stroke_width=0,
                                   fill_color=GELB, fill_opacity=1), t)


def aufleuchten(mob, farbe=GELB, breite=8):
    return mob.animate(rate_func=there_and_back).set_stroke(farbe, breite)


def alle_updater_weg(*mobs):
    for m in mobs:
        for f in m.get_family():
            f.clear_updaters()


def hud_teile(scene):
    return [m for m in scene.mobjects if getattr(m, "_hud_w", None)]


def kreuz(mitte, g=0.25, farbe=ROT_HELL, sw=7):
    return VGroup(Line(UL, DR), Line(UR, DL)).set_stroke(farbe, sw).scale(g).move_to(mitte)


def einschalten(*fluesse, start=0.0):
    t = ValueTracker(start)
    for f in fluesse:
        f.an = t.get_value
    return t


def alles_weg(scene, run_time=0.5):
    """Alles ausser Sternenstaub und HUD ausblenden (Updater vorher weg)."""
    alt = Group(*[m for m in scene.mobjects if m is not scene.hg and not getattr(m, "_hud_w", None)
                  and not isinstance(m, ValueTracker)])
    for m in alt.get_family():
        m.clear_updaters()
    scene.play(FadeOut(alt, shift=UP * 0.3), run_time=run_time)
    scene.aufraeumen(*hud_teile(scene))


def countdown(scene, mitte, t_ende):
    """Denkpause: Ring läuft ab bis t_ende (Muster Video 12/E2, einheitlich seit 9.11.)."""
    rest = ValueTracker(1.0)
    rm = np.array(mitte, dtype=float)
    spur = Circle(radius=0.6, stroke_color=GELB, stroke_width=7, stroke_opacity=0.18).move_to(rm)
    bogen = always_redraw(lambda: Arc(radius=0.6, start_angle=PI / 2 - TAU * (1 - rest.get_value()),
                                      angle=-TAU * max(0.001, rest.get_value()), arc_center=rm,
                                      stroke_color=GELB, stroke_width=7))
    pause = VGroup(Rectangle(width=0.14, height=0.45), Rectangle(width=0.14, height=0.45).shift(RIGHT * 0.28)
                   ).set_style(fill_color=WEISS, fill_opacity=1, stroke_width=0).move_to(rm)
    scene.add(spur, bogen)
    scene.play(FadeIn(pause, scale=1.4), run_time=0.4)
    puls(pause, 0.08, 1.0)
    scene.play(rest.animate.set_value(0.0), run_time=max(0.5, t_ende - scene.jetzt() - 0.1), rate_func=linear)
    bogen.clear_updaters()
    pause.clear_updaters()
    scene.play(FadeOut(pause), FadeOut(bogen), FadeOut(spur), run_time=0.3)


# --- Gegenstände --------------------------------------------------------------------------------
def multimeter14(mitte, s=1.0, wert=None, fmt=None, farbe=CYAN, modus="V", rot_in="V", anzeige=None):
    """Digitalmultimeter von vorn mit Drehschalter (V, A, Ω) und drei Buchsen: 10A links, COM mitte, VΩ rechts.
    rot_in: Buchse der roten Messleitung ("V" oder "A"). wert = Funktion -> mitlaufende Anzeige; anzeige = fester Text."""
    m = np.array(mitte, dtype=float)
    k = RoundedRectangle(width=1.7 * s, height=2.6 * s, corner_radius=0.18 * s, stroke_color=WEISS, stroke_width=3,
                         fill_color=GEHAEUSE, fill_opacity=1).move_to(m)
    disp = RoundedRectangle(width=1.36 * s, height=0.62 * s, corner_radius=0.06 * s, stroke_width=0,
                            fill_color=DISPLAY, fill_opacity=1).move_to(m + UP * 0.8 * s)
    km = m + DOWN * 0.12 * s
    knopf = Circle(0.34 * s, stroke_color=GRAU, stroke_width=3, fill_color=NAVY, fill_opacity=1).move_to(km)
    winkel = {"V": PI * 0.2, "A": PI * 0.8, "Ω": PI * 0.5, "aus": -PI * 0.5}[modus]
    zg = Line(km, km + 0.3 * s * np.array([np.cos(winkel), np.sin(winkel), 0]), stroke_color=WEISS, stroke_width=4)
    lab = VGroup(T("V", int(15 * s), CYAN, BOLD).move_to(km + 0.5 * s * np.array([np.cos(PI * 0.2), np.sin(PI * 0.2), 0])),
                 T("Ω", int(15 * s), ORANGE, BOLD).move_to(km + 0.5 * s * np.array([0, 1, 0])),
                 T("A", int(15 * s), GELB, BOLD).move_to(km + 0.5 * s * np.array([np.cos(PI * 0.8), np.sin(PI * 0.8), 0])))
    by = -1.0 * s
    b_a = VGroup(Circle(0.1 * s, stroke_color=ROT, stroke_width=2.5, fill_color=NAVY, fill_opacity=1).move_to(m + np.array([-0.5, by, 0]) * s / s))
    b_com = VGroup(Circle(0.1 * s, stroke_color=WEISS, stroke_width=2.5, fill_color=NAVY, fill_opacity=1).move_to(m + np.array([0.0, by, 0])))
    b_v = VGroup(Circle(0.1 * s, stroke_color=ROT, stroke_width=2.5, fill_color=NAVY, fill_opacity=1).move_to(m + np.array([0.5 * s, by, 0])))
    b_a[0].move_to(m + np.array([-0.5 * s, by, 0]))
    bl = VGroup(T("10A", int(11 * s), GRAU, BOLD).move_to(b_a[0].get_center() + DOWN * 0.2 * s),
                T("COM", int(11 * s), GRAU, BOLD).move_to(b_com[0].get_center() + DOWN * 0.2 * s),
                T("VΩ", int(11 * s), GRAU, BOLD).move_to(b_v[0].get_center() + DOWN * 0.2 * s))
    g = VGroup(k, disp, knopf, zg, lab, b_a, b_com, b_v, bl)
    if wert is not None:
        g.anzeige = Zaehler(wert, fmt or (lambda v: de(v, 1) + " V"), int(26 * s), farbe, HEAVY, ort=disp.get_center())
        g.add(g.anzeige)
    elif anzeige is not None:
        g.anzeige = T(anzeige, int(24 * s), farbe, HEAVY).move_to(disp.get_center())
        g.add(g.anzeige)
    g.b_rot = (b_a if rot_in == "A" else b_v)[0]
    g.b_sw = b_com[0]
    g.b_a, g.b_v, g.b_com, g.disp, g.zg, g.knopf, g.km, g.koerper = b_a[0], b_v[0], b_com[0], disp, zg, knopf, km, k
    return g


def leitung(a, b, farbe, hang=0.6, sw=5):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    return CubicBezier(a, a + DOWN * hang, b + DOWN * hang, b, stroke_color=farbe, stroke_width=sw)


def leitung2(a, b, farbe, ca, cb, sw=5):
    """Messleitung mit eigenen Steuerpunkten: ca am Anfang (Messgerät), cb am Ende (Steckdose), damit keine Leitung über ein Loch läuft."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    return CubicBezier(a, a + np.array(ca, dtype=float), b + np.array(cb, dtype=float), b, stroke_color=farbe, stroke_width=sw)


def polung(plus, minus, farbe=WEISS, size=24):
    """Plus- und Minuszeichen an zwei Punkten (Ivan 23.11.: Polung an jeder Gleichspannungsquelle und jedem Messgerät)."""
    return VGroup(T("+", size, farbe, HEAVY).move_to(plus), T("−", size, farbe, HEAVY).move_to(minus))


def steckdose(mitte, s=1.0):
    """Schweizer Steckdose Typ 13 (Ivan 30.10.): quadratische Platte, Sechseck, drei Löcher (L, N oben, PE unten)."""
    m = np.array(mitte, dtype=float)
    sechseck = Polygon([-0.2 * s, 0.3 * s, 0], [0.2 * s, 0.3 * s, 0], [0.38 * s, 0, 0], [0.2 * s, -0.3 * s, 0],
                       [-0.2 * s, -0.3 * s, 0], [-0.38 * s, 0, 0], stroke_color=WEISS, stroke_width=3,
                       fill_color=NAVY, fill_opacity=1)
    g = VGroup(RoundedRectangle(width=1.0 * s, height=1.0 * s, corner_radius=0.16 * s, stroke_color=WEISS,
                                stroke_width=4, fill_color=NAVY2, fill_opacity=1),
               sechseck,
               Dot([-0.165 * s, 0.09 * s, 0], 0.05 * s, color=WEISS), Dot([0.165 * s, 0.09 * s, 0], 0.05 * s, color=WEISS),
               Dot([0.0, -0.14 * s, 0], 0.05 * s, color=WEISS)).move_to(m)
    g.loch_l, g.loch_n, g.loch_pe = g[2], g[3], g[4]
    return g


def ls_schalter(mitte, text="B13", s=1.0):
    """Leitungsschutzschalter mit Kipphebel (oben = ein)."""
    m = np.array(mitte, dtype=float)
    koerper = RoundedRectangle(width=0.95 * s, height=1.75 * s, corner_radius=0.08 * s, stroke_color=GRAU,
                               stroke_width=3, fill_color="#E6ECF2", fill_opacity=1).move_to(m)
    fenster = RoundedRectangle(width=0.5 * s, height=0.55 * s, corner_radius=0.05 * s, stroke_width=0,
                               fill_color="#9AA8B6", fill_opacity=1).move_to(m + UP * 0.1 * s)
    hebel = RoundedRectangle(width=0.32 * s, height=0.32 * s, corner_radius=0.04 * s, stroke_width=0,
                             fill_color=NAVY, fill_opacity=1).move_to(m + UP * 0.22 * s)
    klemmen = VGroup(Line(m + UP * 0.88 * s, m + UP * 1.15 * s), Line(m + DOWN * 0.88 * s, m + DOWN * 1.15 * s)
                     ).set_stroke(WEISS, 5)
    g = VGroup(klemmen, koerper, fenster, hebel)
    if text:
        g.add(T(text, int(30 * s), NAVY, HEAVY).move_to(m + DOWN * 0.55 * s))
    g.hebel, g.s = hebel, s
    return g


def lampe_symbol(mitte, r=0.32, farbe=WEISS):
    """DIN-Lampensymbol: Kreis mit Kreuz."""
    m = np.array(mitte, dtype=float)
    c = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY, fill_opacity=1).move_to(m)
    x = VGroup(Line(m + r * np.array([-0.7, -0.7, 0]), m + r * np.array([0.7, 0.7, 0])),
               Line(m + r * np.array([-0.7, 0.7, 0]), m + r * np.array([0.7, -0.7, 0]))).set_stroke(farbe, 4)
    g = VGroup(c, x)
    g.kreis = c
    return g


def messgeraet_symbol(mitte, buchstabe="V", farbe=CYAN, r=0.36):
    """Rundes Messgerätesymbol (V oder A) mit Buchstabe."""
    m = np.array(mitte, dtype=float)
    c = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    t = T(buchstabe, int(28 * r / 0.36), farbe, HEAVY).move_to(m)
    g = VGroup(c, t)
    g.kreis = c
    return g


def quelle_symbol(mitte, text="U", farbe=WEISS, r=0.4):
    m = np.array(mitte, dtype=float)
    c = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    t = T(text, int((28 if len(text) <= 2 else 17) * r / 0.4), CYAN, HEAVY).move_to(m)
    return VGroup(c, t)


def stromkreis(mitte, b=4.4, h=2.4, s=1.0, quelle="U"):
    """Einfacher Stromkreis: Quelle links, Lampe rechts, Rechteck aus Leitungen.
    Attribute: weg (geschlossener Punktzug), lampe, q, P(x, y) lokal, oben_y."""
    m = np.array(mitte, dtype=float)

    def P(x, y):
        return m + np.array([x, y, 0]) * s

    bb, hh = b / 2, h / 2
    q = quelle_symbol(P(-bb, 0), quelle, r=0.4 * s)
    la = lampe_symbol(P(bb, 0), 0.32 * s)
    d = VGroup(VMobject().set_points_as_corners([P(-bb, 0.4), P(-bb, hh), P(bb, hh), P(bb, 0.32)]),
               VMobject().set_points_as_corners([P(bb, -0.32), P(bb, -hh), P(-bb, -hh), P(-bb, -0.4)])).set_stroke(WEISS, 4)
    pol = polung(P(-bb + 0.55, 0.42), P(-bb + 0.55, -0.42), WEISS, int(24 * s))
    g = VGroup(d, q, la, pol)
    g.P, g.s, g.q, g.lampe, g.draht, g.pol = P, s, q, la, d, pol
    g.weg = [P(-bb, 0), P(-bb, hh), P(bb, hh), P(bb, -hh), P(-bb, -hh)]
    g.oben = (P(-bb, hh), P(bb, hh))
    return g


def manometer(mitte, wert, r=0.45, farbe=WEISS):
    m = np.array(mitte, dtype=float)
    ring = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    skala = VGroup(*[Line(m + r * 0.76 * np.array([np.cos(a), np.sin(a), 0]), m + r * 0.9 * np.array([np.cos(a), np.sin(a), 0]),
                          stroke_color=farbe, stroke_width=2) for a in np.linspace(PI * 1.2, -PI * 0.2, 7)])
    rot = Arc(radius=r * 0.83, start_angle=-PI * 0.2, angle=PI * 0.35, arc_center=m, stroke_color=ROT, stroke_width=4)

    def zeiger():
        a = PI * 1.2 - PI * 1.4 * max(0.0, min(1.0, wert.get_value()))
        return Line(m, m + r * 0.8 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=GELB, stroke_width=4)

    return VGroup(ring, skala, rot, always_redraw(zeiger), Dot(radius=0.06, color=GELB).move_to(m))


def wasseruhr(mitte, r=0.5, farbe=WEISS):
    """Wasseruhr im Rohr: runder Zähler mit Ziffern und einem kleinen Rädchen, das sich dreht (dt)."""
    m = np.array(mitte, dtype=float)
    ring = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    fenster = RoundedRectangle(width=r * 1.3, height=r * 0.5, corner_radius=0.04, stroke_width=0, fill_color="#06101A",
                               fill_opacity=1).move_to(m + UP * r * 0.3)
    ziff = T("0 4 2 7", int(26 * r), WEISS, BOLD).move_to(fenster)
    rad = VGroup(*[Line(m + DOWN * r * 0.4, m + DOWN * r * 0.4 + r * 0.22 * np.array([np.cos(a), np.sin(a), 0]),
                        stroke_color=ROT, stroke_width=3) for a in np.linspace(0, TAU, 5)[:-1]])
    rad.add(Circle(r * 0.24, stroke_color=GRAU, stroke_width=2).move_to(m + DOWN * r * 0.4))
    g = VGroup(ring, fenster, ziff, rad)
    g.rad, g.tempo = rad, 0.0
    rad.add_updater(lambda mm, dt: mm.rotate(-g.tempo * dt, about_point=m + DOWN * r * 0.4))
    return g


def messwerk(mitte, anteil, r=0.6, farbe=WEISS, text=None):
    """Drehspulmesswerk: Halbkreis-Skala, Zeiger folgt dem Tracker anteil (0..1)."""
    m = np.array(mitte, dtype=float)
    ring = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    skala = Arc(radius=r * 0.78, start_angle=PI * 0.85, angle=-PI * 0.7, arc_center=m + DOWN * r * 0.25, stroke_color=GRAU, stroke_width=3)
    striche = VGroup(*[Line(m + DOWN * r * 0.25 + r * 0.7 * np.array([np.cos(a), np.sin(a), 0]),
                            m + DOWN * r * 0.25 + r * 0.86 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=GRAU, stroke_width=2)
                       for a in np.linspace(PI * 0.85, PI * 0.15, 6)])

    def zeiger():
        a = PI * 0.85 - PI * 0.7 * max(0.0, min(1.0, anteil.get_value()))
        return Line(m + DOWN * r * 0.25, m + DOWN * r * 0.25 + r * 0.82 * np.array([np.cos(a), np.sin(a), 0]),
                    stroke_color=GELB, stroke_width=4)

    g = VGroup(ring, skala, striche, always_redraw(zeiger), Dot(radius=0.05, color=GELB).move_to(m + DOWN * r * 0.25))
    if text:
        g.add(T(text, int(20 * r / 0.6), farbe, BOLD).move_to(m + DOWN * (r + 0.22)))
    g.kreis = ring
    return g


def widerstand_h(mitte, breite=1.1, hoehe=0.42, farbe=WEISS, fuell=NAVY):
    return Rectangle(width=breite, height=hoehe, stroke_color=farbe, stroke_width=4, fill_color=fuell, fill_opacity=1).move_to(mitte)


def stromzange(mitte, s=1.0, offen=0.0):
    """Stromzange: Ring aus zwei Backen um den Leiter (Mitte = Leiter), Griff unten, kleines Display."""
    m = np.array(mitte, dtype=float)
    r = 0.7 * s
    b1 = Arc(radius=r, start_angle=PI / 2, angle=PI - offen, arc_center=m, stroke_color=METALL, stroke_width=14 * s)
    b2 = Arc(radius=r, start_angle=PI / 2, angle=-(PI - offen), arc_center=m, stroke_color=METALL, stroke_width=14 * s)
    griff = RoundedRectangle(width=1.1 * s, height=2.0 * s, corner_radius=0.18 * s, stroke_color=WEISS, stroke_width=3,
                             fill_color=GEHAEUSE, fill_opacity=1).move_to(m + DOWN * (r + 1.05 * s))
    disp = RoundedRectangle(width=0.86 * s, height=0.42 * s, corner_radius=0.05 * s, stroke_width=0, fill_color=DISPLAY,
                            fill_opacity=1).move_to(griff.get_center() + UP * 0.45 * s)
    g = VGroup(griff, disp, b1, b2)
    g.disp, g.b1, g.b2, g.m, g.r = disp, b1, b2, m, r
    return g


def verteiler(mitte, s=1.0, text="Verteiler"):
    m = np.array(mitte, dtype=float)
    kasten = RoundedRectangle(width=1.5 * s, height=1.9 * s, corner_radius=0.12 * s, stroke_color=WEISS, stroke_width=4,
                              fill_color=NAVY2, fill_opacity=1).move_to(m)
    reihe = VGroup(*[ls_schalter(m + np.array([x * s, 0.0, 0]), "", 0.36 * s) for x in (-0.42, 0.0, 0.42)])
    g = VGroup(kasten, reihe)
    if text:
        g.add(T(text, int(24 * s), GRAU, BOLD).next_to(kasten, DOWN, 0.12))
    return g


def waage_icon(s=1.0):
    """Personenwaage von oben (für die Abspannkarte): Platte, kleines Display, vier Füsse als Punkte."""
    platte = RoundedRectangle(width=2.2 * s, height=1.6 * s, corner_radius=0.2 * s, stroke_color=WEISS, stroke_width=4,
                              fill_color=NAVY2, fill_opacity=1)
    disp = RoundedRectangle(width=0.9 * s, height=0.36 * s, corner_radius=0.05 * s, stroke_width=0, fill_color=DISPLAY,
                            fill_opacity=1).move_to(platte.get_top() + DOWN * 0.35 * s)
    z = T("72,4", int(18 * s), CYAN, HEAVY).move_to(disp)
    fuesse = VGroup(*[Dot(platte.get_center() + np.array([x, y, 0]) * s, 0.09 * s, color=GELB) for x in (-0.75, 0.75) for y in (-0.45, 0.3)])
    return VGroup(platte, disp, z, fuesse)


class Rauch(VGroup):
    """Leichter Rauch: Wölkchen steigen von quelle auf, wachsen, driften, verblassen (dt-basiert)."""

    def __init__(self, quelle, staerke=1.0, n=7, farbe=GRAU, seed=3):
        super().__init__()
        self.q = np.array(quelle, dtype=float)
        self.staerke = staerke
        self.rng = np.random.default_rng(seed)
        self.teile = []
        for i in range(n):
            c = Circle(0.08, stroke_width=0, fill_color=farbe, fill_opacity=0).move_to(self.q)
            c._alter = i * 0.35
            self.teile.append(c)
            self.add(c)
        self.add_updater(lambda m, dt: m._schritt(dt))

    def _schritt(self, dt):
        st = self.staerke() if callable(self.staerke) else self.staerke
        for c in self.teile:
            c._alter += dt
            if c._alter > 2.4:
                c._alter = 0.0
                c.move_to(self.q + RIGHT * self.rng.uniform(-0.1, 0.1))
                c.set(width=0.16)
            a = c._alter
            c.move_to(c.get_center() + UP * 0.55 * dt + RIGHT * 0.12 * np.sin(2.0 * a) * dt)
            c.set(width=max(0.16, 0.16 + 0.5 * a))
            c.set_fill(opacity=st * max(0.0, 0.5 * (1 - a / 2.4)) if a > 0 else 0)


# --- Szene 1: Haken -------------------------------------------------------------------------------
# Steckdose links gross, Multimeter rechts, rote Leitung in "10A". Leitungen an die Steckdose: Blitz, Knall,
# Rauch, Display dunkel, LS kippt. Steckdose "in Ordnung". Dann rhetorische Frage.
class Szene01(WattScene):
    def construct(self):
        sd = steckdose([-3.6, 0.1, 0], 2.9)
        mm = multimeter14([3.3, -0.9, 0], 1.45, modus="V", rot_in="A", anzeige="0.0")
        self.add(sd, mm)
        schweben(mm, 0.02, 0.4)
        ls = ls_schalter([5.6, 2.6, 0], "B13", 0.9)
        self.add(ls)
        # Leitungen kommen zur Steckdose
        self.bis(0, 0.05)
        ziel_l = sd.loch_l.get_center()
        ziel_n = sd.loch_n.get_center()
        p_rot = ValueTracker(0.0)
        start_r = mm.b_rot.get_center() + DOWN * 0.25
        start_s = mm.b_sw.get_center() + DOWN * 0.25
        l_rot = always_redraw(lambda: leitung2(mm.b_rot.get_center(), start_r + (ziel_l - start_r) * p_rot.get_value(), ROT, DOWN * 1.2, RIGHT * 2.6 + DOWN * 1.3))
        l_sw = always_redraw(lambda: leitung2(mm.b_sw.get_center(), start_s + (ziel_n - start_s) * p_rot.get_value(), GRAU, DOWN * 1.4, RIGHT * 2.0 + DOWN * 1.5))
        self.add(l_rot, l_sw)
        self.play(p_rot.animate.set_value(1.0), run_time=self.rt(1.4, 0, 0.95), rate_func=smooth)
        rot_b = badge("10A", ROT, WEISS, 22).next_to(mm.b_a, DOWN, 0.35)
        self.play(FadeIn(rot_b, scale=1.3), run_time=self.rt(0.4, 1))
        puls(rot_b, 0.05, 1.0)

        # Knall
        self.bis_wort(1, "knallt")
        bogen = Lichtbogen(lambda: ziel_l + LEFT * 0.05, lambda: ziel_n + RIGHT * 0.05, GELB, n=9, breite=7, amp=0.3)
        bogen.set_z_index(6)
        self.add(bogen)
        self.blitzlicht(GELB, 0.5, 0.5)
        self.kamera_wackeln(0.16, 0.5)
        stern = VGroup(*[Line(ORIGIN, 0.6 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=GELB, stroke_width=5)
                         for a in np.linspace(0, TAU, 9)[:-1]]).move_to(sd.get_center() + RIGHT * 0.2)
        self.play(FadeIn(stern, scale=0.3), run_time=0.2)
        self.play(FadeOut(stern, scale=1.8), run_time=self.rt(0.4, 2))
        rauch = Rauch(ziel_l + UP * 0.1, 1.0)
        self.add(rauch)
        # Sicherung fliegt, Messgerät hin
        self.bis_wort(2, "Sicherung")
        bogen.an = 0.0
        self.play(ls.hebel.animate.shift(DOWN * 0.42 * ls.s), run_time=0.25)
        aus = badge("aus", ROT, WEISS, 22).next_to(ls, DOWN, 0.2)
        self.play(FadeIn(aus, scale=1.3), run_time=self.rt(0.4, 2, wort="Messgerät"))
        self.remove(bogen)
        self.bis_wort(2, "Messgerät")
        self.play(mm.disp.animate.set_fill("#050A0F"), mm.anzeige.animate.set_opacity(0), run_time=0.3)
        kz = kreuz(mm.disp.get_center(), 0.3, ROT_HELL, 8)
        self.play(Create(kz), run_time=self.rt(0.4, 3))
        rauch2 = Rauch(mm.koerper.get_top() + DOWN * 0.1, 0.8, seed=5)
        self.add(rauch2)
        mm.add(kz)
        # Steckdose in Ordnung
        self.bis_wort(3, "Ordnung")
        ok = badge("in Ordnung", GRUEN, NAVY, 30).move_to([-3.6, -2.0, 0])
        self.play(FadeIn(ok, scale=1.2), aufleuchten(sd[0], GRUEN, 8), run_time=self.rt(0.6, 4))
        puls(ok, 0.04, 0.9)
        # rhetorische Frage
        self.rhetorische_frage(4)
        self.ende()


# --- Szene 2: Intro ---------------------------------------------------------------------------------
class Szene02(WattScene):
    def construct(self):
        logo = self.logo_intro(k_weiter=1)
        self.bis(1)
        self.play(logo.animate.scale(0.3).move_to([0, 2.85, 0]), run_time=self.rt(0.8, 1, 0.3), rate_func=smooth)
        self.bis_wort(1, "Messen")
        titel = T("Richtig messen", 92, GELB, HEAVY).move_to([0, 1.0, 0])
        self.play(Write(titel), run_time=self.rt(0.8, 2))
        schweben(titel, 0.035, 0.45)

        drei = VGroup(VGroup(messgeraet_symbol(ORIGIN, "V", CYAN, 0.45), T("Spannung", 28, CYAN, BOLD)).arrange(DOWN, buff=0.15),
                      VGroup(messgeraet_symbol(ORIGIN, "A", GELB, 0.45), T("Strom", 28, GELB, BOLD)).arrange(DOWN, buff=0.15),
                      VGroup(messgeraet_symbol(ORIGIN, "Ω", ORANGE, 0.45), T("Widerstand", 28, ORANGE, BOLD)).arrange(DOWN, buff=0.15)
                      ).arrange(RIGHT, buff=0.9).move_to([-2.6, -1.4, 0])
        for i, w in enumerate(("Spannung", "Strom", "Widerstand")):
            self.bis_wort(2, w)
            self.play(FadeIn(drei[i], shift=UP * 0.2), run_time=self.rt(0.4, 2, wort=("Strom", "Widerstand", "Messgerät")[i]))
            schweben(drei[i], 0.03, 0.45, 0.25 * i)
        self.bis_wort(2, "Messgerät")
        mm = multimeter14([4.2, -1.5, 0], 0.85, modus="V", rot_in="A", anzeige="230")
        self.play(FadeIn(mm, shift=UP * 0.2), run_time=self.rt(0.5, 3))
        schweben(mm, 0.03, 0.4, 0.5)
        self.bis_wort(3, "Messleitung")
        l = leitung(mm.b_rot.get_center(), mm.b_rot.get_center() + DOWN * 1.0 + LEFT * 0.6, ROT, 0.4)
        pf = pfeil(mm.b_a.get_center() + DL * 0.9, mm.b_a.get_center() + DL * 0.25, ROT, 5, 0.2)
        self.play(Create(l), GrowArrow(pf), run_time=self.rt(0.5, 3, wort="Knall"))
        self.bis_wort(3, "Knall")
        bl = blitz_form(0.8, GELB).move_to(mm.get_top() + UP * 0.1 + RIGHT * 0.9)
        self.play(FadeIn(bl, scale=0.4), run_time=0.3)
        wackeln(bl, 0.08, 1.4)
        self.bis_wort(3, "sicher")
        hk = haken([5.9, -2.9, 0], 0.5, GRUEN, 8)
        self.play(Create(hk), run_time=self.rt(0.5, 4))
        self.ende()


# --- Szene 3: Spannung messen: Manometer seitlich, Voltmeter parallel, 10 MΩ ------------------------------
class Szene03(WattScene):
    def construct(self):
        self.kapitel("Spannung messen")
        # Wasserleitung links
        rohr_y = 0.6
        weg = [np.array([-6.6, rohr_y, 0]), np.array([-0.9, rohr_y, 0])]
        rohr = Line(weg[0], weg[1], stroke_color=ROHR, stroke_width=24)
        bohr = Line(weg[0], weg[1], stroke_color=NAVY, stroke_width=13)
        fl = Fluss(weg, n=24, tempo=1.3, farbe=WASSER, radius=0.06, rand=0.3).set_z_index(3)
        an = einschalten(fl)
        self.play(Create(rohr), run_time=self.rt(0.6, 0, 0.9))
        self.add(bohr, fl)
        self.play(an.animate.set_value(1.0), run_time=self.rt(0.4, 1))
        # Manometer seitlich
        self.bis_wort(1, "Manometer")
        p1 = ValueTracker(0.0)
        stub = Line([-3.7, rohr_y + 0.1, 0], [-3.7, rohr_y + 0.75, 0], stroke_color=ROHR, stroke_width=7)
        m1 = manometer([-3.7, rohr_y + 1.3, 0], p1, 0.5)
        self.play(FadeIn(stub), FadeIn(m1), run_time=self.rt(0.5, 2))
        self.play(p1.animate.set_value(0.8), run_time=self.rt(0.7, 2, wort="seitlich"), rate_func=smooth)
        self.bis_wort(2, "seitlich")
        seit = badge("seitlich dran", CYAN, NAVY, 24).next_to(m1, RIGHT, 0.3)
        self.play(FadeIn(seit, shift=LEFT * 0.1), run_time=self.rt(0.4, 2, wort="kein"))
        schweben(seit, 0.02, 0.5)
        self.bis_wort(2, "kein")
        wen = badge("nimmt fast nichts weg", WASSER, NAVY, 24).move_to([-3.7, -0.3, 0])
        self.play(FadeIn(wen, shift=UP * 0.1), run_time=self.rt(0.4, 3))
        schweben(wen, 0.02, 0.5, 0.3)

        # Stromkreis rechts: Quelle, Lampe, Voltmeter parallel
        self.bis(3)
        sk = stromkreis([3.6, 0.3, 0], 4.2, 2.6, 0.95)
        P = sk.P
        self.play(FadeIn(sk, shift=UP * 0.2), run_time=self.rt(0.6, 4))
        fl2 = Fluss(sk.weg, n=28, tempo=1.0, farbe=GELB, radius=0.055, geschlossen=True).set_z_index(3)
        an2 = einschalten(fl2)
        self.add(fl2)
        self.play(an2.animate.set_value(1.0), run_time=self.rt(0.4, 4, wort="zwei"))
        self.bis_wort(4, "zwei")
        pa = Dot(P(2.1, 0.55), 0.09, color=CYAN)
        pb = Dot(P(2.1, -0.55), 0.09, color=CYAN)
        self.play(FadeIn(pa, scale=2), FadeIn(pb, scale=2), run_time=self.rt(0.4, 4, wort="Voltmeter"))
        puls(pa, 0.15, 1.2)
        puls(pb, 0.15, 1.2)
        self.bis_wort(4, "Voltmeter")
        vm = messgeraet_symbol(P(3.4, 0.0), "V", CYAN, 0.36)
        vl = VGroup(VMobject().set_points_as_corners([P(2.1, 0.55), P(3.4, 0.55), P(3.4, 0.36)]),
                    VMobject().set_points_as_corners([P(3.4, -0.36), P(3.4, -0.55), P(2.1, -0.55)])).set_stroke(CYAN, 3)
        vpol = polung(P(3.85, 0.55), P(3.85, -0.55), CYAN, 22)
        self.play(FadeIn(vm, scale=0.6), Create(vl), FadeIn(vpol), run_time=self.rt(0.6, 5))
        self.bis_wort(5, "parallel")
        par = badge("parallel zum Verbraucher", CYAN, NAVY, 26).move_to([3.6, -1.75, 0])
        self.play(FadeIn(par, shift=UP * 0.1), aufleuchten(sk.lampe.kreis, CYAN, 8), run_time=self.rt(0.5, 6))
        schweben(par, 0.02, 0.5)
        self.bis(6)
        self.play(aufleuchten(sk.draht, GELB, 6), run_time=self.rt(0.7, 7))
        bleibt = badge("Stromkreis bleibt, wie er ist", GELB, NAVY, 22).move_to([3.6, 2.35, 0])
        self.play(FadeIn(bleibt, shift=DOWN * 0.1), run_time=self.rt(0.4, 7))
        schweben(bleibt, 0.02, 0.5, 0.4)

        # 10 MΩ innen
        self.bis_wort(7, "innen")
        alle_updater_weg(wen, seit)
        self.play(FadeOut(wen), FadeOut(seit), run_time=0.3)
        ri = badge("Rᵢ ≈ 10 MΩ", CYAN, NAVY, 30).next_to(vm, RIGHT, 0.25)
        self.play(FadeIn(ri, scale=1.3), aufleuchten(vm.kreis, WEISS, 8), run_time=self.rt(0.6, 8))
        puls(ri, 0.04, 0.9)
        # 230 V -> 23 µA
        self.bis_wort(8, "zweihundert")
        rech = MT('230 V / 10 MΩ = <span foreground="#22D3EE">23 µA</span>', 34, WEISS, BOLD).move_to([-3.4, -1.9, 0])
        self.play(FadeIn(rech, shift=UP * 0.15), run_time=self.rt(0.7, 8, wort="dreiundzwanzig"))
        self.bis_wort(8, "merkt")
        merkt = badge("die Schaltung merkt nichts", GRUEN, NAVY, 24).next_to(rech, DOWN, 0.3)
        self.play(FadeIn(merkt, shift=UP * 0.1), run_time=self.rt(0.4, 9))
        schweben(VGroup(rech, merkt), 0.02, 0.5)
        # gefahrlos an eine Spannungsquelle
        self.bis(9)
        alle_updater_weg(rech, merkt)
        self.play(FadeOut(rech), FadeOut(merkt), run_time=self.rt(0.4, 10))
        sd = steckdose([-4.6, -2.1, 0], 1.2)
        vm2 = messgeraet_symbol([-2.2, -2.1, 0], "V", CYAN, 0.42)
        ll = VGroup(leitung2(vm2.get_center() + LEFT * 0.42 + UP * 0.1, sd.loch_n.get_center(), ROT, LEFT * 0.5, RIGHT * 0.6),
                    leitung2(vm2.get_center() + LEFT * 0.42 + DOWN * 0.1, sd.loch_l.get_center(), GRAU, LEFT * 0.4 + DOWN * 0.6, DOWN * 0.9))
        self.bis(10)
        self.play(FadeIn(sd), FadeIn(vm2), Create(ll), run_time=self.rt(0.6, 10, wort="gefahrlos"))
        self.bis_wort(10, "gefahrlos")
        hk = haken(vm2.get_center() + RIGHT * 0.9, 0.5, GRUEN, 8)
        gef = badge("gefahrlos", GRUEN, NAVY, 26).next_to(hk, RIGHT, 0.2)
        self.play(Create(hk), FadeIn(gef, shift=LEFT * 0.1), run_time=self.rt(0.5, 11))
        schweben(VGroup(hk, gef), 0.02, 0.5)
        self.bis(11)
        self.play(aufleuchten(vm2.kreis, GRUEN, 8), run_time=self.rt(0.6, 12))
        self.ende()


# --- Szene 4: Strom messen: Wasseruhr im Rohr, Amperemeter in Reihe, Shunt, Zwischenfrage ---------------------
class Szene04(WattScene):
    def construct(self):
        self.kapitel("Strom messen")
        rohr_y = 0.6
        weg = [np.array([-6.6, rohr_y, 0]), np.array([-0.9, rohr_y, 0])]
        rohr = Line(weg[0], weg[1], stroke_color=ROHR, stroke_width=24)
        bohr = Line(weg[0], weg[1], stroke_color=NAVY, stroke_width=13)
        fl = Fluss(weg, n=24, tempo=1.3, farbe=WASSER, radius=0.06, rand=0.3).set_z_index(3)
        an = einschalten(fl, start=1.0)
        self.add(rohr, bohr, fl)
        sk = stromkreis([3.6, 0.3, 0], 4.2, 2.6, 0.95)
        P = sk.P
        fl2 = Fluss(sk.weg, n=28, tempo=1.0, farbe=GELB, radius=0.055, geschlossen=True).set_z_index(3)
        self.add(sk, fl2)
        self.bis(0, 0.2)
        umg = badge("umgekehrt", GELB, NAVY, 30).move_to([3.6, 2.35, 0])
        self.play(FadeIn(umg, scale=1.2), run_time=self.rt(0.5, 1))
        wackeln(umg, 0.04, 1.0)
        self.bis_wort(1, "durch die Leitung")
        self.play(aufleuchten(sk.draht, GELB, 7), run_time=self.rt(0.7, 1, wort="Messgerät"))
        self.bis_wort(1, "Messgerät")
        mm = multimeter14([6.3, 2.6, 0], 0.5, modus="A", rot_in="A", anzeige="0.0")
        self.play(FadeIn(mm, shift=LEFT * 0.2), run_time=self.rt(0.4, 2))
        schweben(mm, 0.03, 0.4)
        # Wasseruhr im Rohr
        self.bis_wort(2, "Wasseruhr")
        wu = wasseruhr([-3.7, rohr_y, 0], 0.62)
        wu.set_z_index(4)
        self.play(GrowFromCenter(wu), run_time=self.rt(0.5, 3))
        wu.tempo = 3.0
        self.bis_wort(3, "steckt")
        im = badge("steckt im Rohr", WASSER, NAVY, 24).move_to([-3.7, rohr_y + 1.25, 0])
        self.play(FadeIn(im, shift=DOWN * 0.1), run_time=self.rt(0.4, 3, wort="alles"))
        schweben(im, 0.02, 0.5)
        self.bis_wort(3, "alles")
        alles = badge("alles Wasser läuft hindurch", WASSER, NAVY, 24).move_to([-3.7, -0.5, 0])
        self.play(FadeIn(alles, shift=UP * 0.1), fl.animate.set_fill(opacity=1), run_time=self.rt(0.4, 4))
        schweben(alles, 0.02, 0.5, 0.3)

        # Stromkreis auftrennen, Amperemeter in die Luecke
        self.bis_wort(4, "trennst")
        alle_updater_weg(umg)
        self.play(FadeOut(umg), run_time=0.2)
        oben_links, oben_rechts = sk.oben
        gap_a, gap_b = P(-0.6, 1.3), P(0.6, 1.3)
        neu_oben = VGroup(VMobject().set_points_as_corners([P(-2.1, 0.4), P(-2.1, 1.3), gap_a]),
                          VMobject().set_points_as_corners([gap_b, P(2.1, 1.3), P(2.1, 0.32)])).set_stroke(WEISS, 4)
        fl2.an = 0.0
        self.remove(sk.draht[0])
        self.add(neu_oben)
        sch = kreuz(P(0, 1.3), 0.22, ROT_HELL, 6)
        self.play(FadeIn(sch, scale=1.5), run_time=0.3)
        self.play(FadeOut(sch), run_time=self.rt(0.3, 4, wort="Amperemeter"))
        self.bis_wort(4, "Amperemeter")
        am = messgeraet_symbol(P(0, 1.3), "A", GELB, 0.36)
        am.set_z_index(4)
        self.play(FadeIn(am, scale=0.5), run_time=self.rt(0.5, 4, wort="Reihe"))
        lk = VGroup(Line(gap_a, am.get_left()), Line(am.get_right(), gap_b)).set_stroke(GELB, 4)
        self.add(lk, polung(P(-0.55, 1.62), P(0.55, 1.62), GELB, 22))
        fl2.an = 1.0
        self.bis_wort(4, "Reihe")
        reihe = badge("in Reihe mit dem Verbraucher", GELB, NAVY, 26).move_to([3.6, -1.75, 0])
        self.play(FadeIn(reihe, shift=UP * 0.1), run_time=self.rt(0.5, 5))
        schweben(reihe, 0.02, 0.5)
        # sehr kleiner Widerstand: Shunt
        self.bis_wort(5, "kleinen")
        ri = badge("Rᵢ ≈ 0,01 Ω", GELB, NAVY, 30).next_to(am, UP, 0.3)
        self.play(FadeIn(ri, scale=1.3), aufleuchten(am.kreis, WEISS, 8), run_time=self.rt(0.6, 6))
        puls(ri, 0.04, 0.9)
        self.bis_wort(6, "Shunt")
        alle_updater_weg(im, alles)
        self.play(FadeOut(im), FadeOut(alles), run_time=0.3)
        # Innenleben: Shunt-Widerstand, Spannung daran
        sh = widerstand_h([-3.6, -1.6, 0], 1.3, 0.42, GELB)
        sht = T("Shunt", 26, GELB, BOLD).next_to(sh, UP, 0.15)
        dr = VGroup(Line([-5.4, -1.6, 0], sh.get_left()), Line(sh.get_right(), [-1.8, -1.6, 0])).set_stroke(WEISS, 4)
        self.play(FadeIn(dr), GrowFromCenter(sh), FadeIn(sht), run_time=self.rt(0.6, 6, wort="Hundertstel"))
        fl3 = Fluss([[-5.4, -1.6, 0], [-1.8, -1.6, 0]], n=16, tempo=1.4, farbe=GELB, radius=0.05, rand=0.3).set_z_index(3)
        self.add(fl3)
        self.bis_wort(6, "Hundertstel")
        hund = badge("0,01 Ω", GELB, NAVY, 24).next_to(sh, DOWN, 0.15)
        self.play(FadeIn(hund, scale=1.2), run_time=self.rt(0.4, 6, wort="winzige"))
        self.bis_wort(6, "winzige")
        mv = VGroup(VMobject().set_points_as_corners([sh.get_left() + UP * 0.21, sh.get_left() + UP * 0.8, [-3.6, -0.8, 0]]),
                    VMobject().set_points_as_corners([[-3.6, -0.8, 0], sh.get_right() + UP * 0.8, sh.get_right() + UP * 0.21])).set_stroke(CYAN, 3)
        mvt = badge("mV", CYAN, NAVY, 22).move_to([-3.6, -0.8, 0])
        self.play(Create(mv), FadeIn(mvt, scale=1.2), run_time=self.rt(0.5, 7))
        puls(mvt, 0.05, 1.0)

        # Zwischenfrage: Bild vom Anfang
        self.bis(7)
        alles_weg(self, self.rt(0.5, 7, 0.5))
        sd = steckdose([-3.0, 0.0, 0], 1.9)
        mm2 = multimeter14([3.0, -0.4, 0], 1.3, modus="V", rot_in="A", anzeige="0.0")
        ll = VGroup(leitung2(mm2.b_rot.get_center(), sd.loch_l.get_center(), ROT, DOWN * 1.0, RIGHT * 1.7 + DOWN * 0.85),
                    leitung2(mm2.b_sw.get_center(), sd.loch_n.get_center(), GRAU, DOWN * 1.2, RIGHT * 1.3 + DOWN * 1.0))
        self.play(FadeIn(sd), FadeIn(mm2), Create(ll), run_time=self.rt(0.7, 8))
        schweben(mm2, 0.02, 0.4)
        self.bis_wort(8, "Kurzschluss")
        ks = badge("fast ein Kurzschluss", ROT, WEISS, 30).move_to([3.0, 2.4, 0])
        self.play(FadeIn(ks, scale=1.2), aufleuchten(mm2.koerper, ROT, 8), run_time=self.rt(0.5, 9))
        puls(ks, 0.05, 1.0)
        rb = badge("10A", ROT, WEISS, 22).next_to(mm2.b_a, DOWN, 0.35)
        self.play(FadeIn(rb, scale=1.3), run_time=0.3)
        puls(rb, 0.05, 1.0)
        schleier, fz = self.rhetorische_frage(9)
        self.bis(10)
        fz.clear_updaters()
        self.play(FadeOut(fz), schleier.animate.set_fill(opacity=0.5), run_time=self.rt(0.6, 11))
        self.bis(11)
        ende = badge("Auflösung am Ende", GELB, NAVY, 36).move_to([0, 0.2, 0])
        ende.set_z_index(42)
        self.play(FadeIn(ende, scale=1.2), run_time=self.rt(0.6, 11, wort="erst"))
        puls(ende, 0.03, 0.9)
        self.ende()


# --- Szene 5: Belastung durch das Messgerät, Messbereich und Erweiterung -------------------------------------
class Szene05(WattScene):
    def construct(self):
        kap = self.kapitel("Das Messgerät verändert die Schaltung")
        eins = badge("Erstens", GELB, NAVY, 34).move_to([0, 2.6, 0])
        self.play(FadeIn(eins, scale=1.2), run_time=self.rt(0.4, 1))
        wackeln(eins, 0.03, 1.0)
        self.bis_wort(1, "Widerstand")
        mm = multimeter14([-4.6, 0.4, 0], 0.9, modus="V", anzeige="")
        rt = badge("hat selbst einen Widerstand", WEISS, NAVY, 22).next_to(mm, DOWN, 0.3)
        self.play(FadeIn(mm), FadeIn(rt, shift=UP * 0.1), run_time=self.rt(0.6, 2))
        schweben(VGroup(mm, rt), 0.02, 0.45)

        # Voltmeter 10 MΩ parallel zu 10 MΩ: halbe Spannung
        self.bis(2)
        x0 = 0.6
        r = widerstand_h([x0, 0.6, 0], 0.42, 1.2).rotate(0)  # senkrecht
        r = Rectangle(width=0.42, height=1.2, stroke_color=WEISS, stroke_width=4, fill_color=NAVY, fill_opacity=1).move_to([x0, 0.6, 0])
        r2 = Rectangle(width=0.42, height=1.2, stroke_color=WEISS, stroke_width=4, fill_color=NAVY, fill_opacity=1).move_to([x0, -1.2, 0])
        dr = VGroup(Line([x0, 1.8, 0], [x0, 1.2, 0]), Line([x0, 0.0, 0], [x0, -0.6, 0]), Line([x0, -1.8, 0], [x0, -2.3, 0])).set_stroke(WEISS, 4)
        q = quelle_symbol([-1.6, -0.3, 0], "20 V", r=0.42)
        qd = VGroup(VMobject().set_points_as_corners([[-1.6, 0.12, 0], [-1.6, 1.8, 0], [x0, 1.8, 0]]),
                    VMobject().set_points_as_corners([[-1.6, -0.72, 0], [-1.6, -2.3, 0], [x0, -2.3, 0]])).set_stroke(WEISS, 4)
        rl = VGroup(T("10 MΩ", 24, WEISS, BOLD).next_to(r, LEFT, 0.15), T("10 MΩ", 24, GRAU, BOLD).next_to(r2, LEFT, 0.15))
        qpol = polung([-1.1, 0.0, 0], [-1.1, -0.62, 0], WEISS, 24)
        self.play(FadeIn(q), Create(qd), FadeIn(r), FadeIn(r2), FadeIn(dr), FadeIn(rl), FadeIn(qpol), run_time=self.rt(0.7, 2, wort="parallel"))
        self.bis_wort(2, "parallel")
        vm = messgeraet_symbol([2.6, 0.6, 0], "V", CYAN, 0.36)
        vl = VGroup(VMobject().set_points_as_corners([[x0, 1.2, 0], [2.6, 1.2, 0], [2.6, 0.96, 0]]),
                    VMobject().set_points_as_corners([[2.6, 0.24, 0], [2.6, 0.0, 0], [x0, 0.0, 0]])).set_stroke(CYAN, 3)
        vri = badge("10 MΩ", CYAN, NAVY, 22).next_to(vm, RIGHT, 0.2)
        vpol = polung([2.95, 1.15, 0], [2.95, 0.05, 0], CYAN, 22)
        self.play(FadeIn(vm, scale=0.6), Create(vl), FadeIn(vri, scale=1.2), FadeIn(vpol), run_time=self.rt(0.6, 3))
        # halbiert sich
        self.bis_wort(3, "halbiert")
        halb = badge("zusammen 5 MΩ", ORANGE, NAVY, 24).move_to([2.2, 1.95, 0])
        self.play(FadeIn(halb, shift=DOWN * 0.1), aufleuchten(VGroup(r, vm.kreis), ORANGE, 8), run_time=self.rt(0.5, 3, wort="statt"))
        schweben(halb, 0.02, 0.5)
        self.bis_wort(3, "statt")
        soll = MT('ohne Messgerät: <span foreground="#F5F7FA">10 V</span>', 26, GRAU, BOLD).move_to([5.0, -0.15, 0])
        ist = MT('Anzeige: <span foreground="#FF8A3D">6,7 V</span>', 30, WEISS, BOLD).move_to([5.0, -0.85, 0])
        self.play(FadeIn(soll, shift=UP * 0.1), run_time=0.3)
        self.play(FadeIn(ist, shift=UP * 0.1), run_time=self.rt(0.5, 4))
        schweben(VGroup(soll, ist), 0.02, 0.5, 0.3)
        # kleine Widerstaende: keine Rolle
        self.bis_wort(4, "Lampe")
        kl = VGroup(lampe_symbol(ORIGIN, 0.3), T("Lampe, Motor: kleine Ω", 24, GRUEN, BOLD)).arrange(RIGHT, buff=0.25).move_to([3.6, -1.7, 0])
        hk = haken(kl.get_right() + RIGHT * 0.45, 0.4, GRUEN, 7)
        self.play(FadeIn(kl, shift=UP * 0.1), run_time=self.rt(0.5, 4, wort="keine"))
        self.bis_wort(4, "keine")
        self.play(Create(hk), run_time=self.rt(0.4, 5))
        schweben(VGroup(kl, hk), 0.02, 0.5)

        # Amperemeter: Spannungsabfall am Shunt
        self.bis(5)
        alles_weg(self, self.rt(0.5, 5, 0.5))
        sk = stromkreis([-2.6, 0.0, 0], 4.2, 2.6, 0.95, quelle="3 V")
        P = sk.P
        self.remove(sk)
        gap_a, gap_b = P(-0.6, 1.3), P(0.6, 1.3)
        sk.draht[0].set_points_as_corners([P(-2.1, 0.4), P(-2.1, 1.3), gap_a])
        rest = VMobject().set_points_as_corners([gap_b, P(2.1, 1.3), P(2.1, 0.32)]).set_stroke(WEISS, 4)
        am = messgeraet_symbol(P(0, 1.3), "A", GELB, 0.36)
        lk = VGroup(Line(gap_a, am.get_left()), Line(am.get_right(), gap_b), polung(P(-0.55, 1.62), P(0.55, 1.62), GELB, 22))
        lk[:2].set_stroke(GELB, 4)
        fl = Fluss(sk.weg, n=28, tempo=1.0, farbe=GELB, radius=0.055, geschlossen=True).set_z_index(3)
        self.play(FadeIn(sk), FadeIn(rest), FadeIn(am), FadeIn(lk), run_time=self.rt(0.6, 6))
        self.add(fl)
        self.bis_wort(6, "kleine Spannung")
        ab = badge("0,2 V fallen ab", ORANGE, NAVY, 26).next_to(am, UP, 0.3)
        self.play(FadeIn(ab, scale=1.2), aufleuchten(am.kreis, ORANGE, 8), run_time=self.rt(0.5, 6, wort="fehlt"))
        puls(ab, 0.04, 0.9)
        self.bis_wort(6, "fehlt")
        feh = badge("Lampe bekommt nur 2,8 V", ORANGE, NAVY, 24).next_to(sk, DOWN, 0.25).shift(RIGHT * 0.8)
        self.play(FadeIn(feh, shift=UP * 0.1), run_time=self.rt(0.5, 7))
        schweben(feh, 0.02, 0.5)
        self.bis_wort(7, "Elektronik")
        chip = VGroup(RoundedRectangle(width=1.3, height=0.9, corner_radius=0.08, stroke_color=GRAU, stroke_width=3,
                                       fill_color="#111C27", fill_opacity=1),
                      *[Line([x, -0.45, 0], [x, -0.7, 0], stroke_color=GRAU, stroke_width=3) for x in (-0.45, -0.15, 0.15, 0.45)],
                      *[Line([x, 0.45, 0], [x, 0.7, 0], stroke_color=GRAU, stroke_width=3) for x in (-0.45, -0.15, 0.15, 0.45)],
                      T("3,3 V", 22, CYAN, BOLD)).move_to([4.0, 0.5, 0])
        merk = badge("hier merkt man das", ORANGE, NAVY, 24).next_to(chip, DOWN, 0.35)
        self.play(FadeIn(chip, shift=UP * 0.2), run_time=self.rt(0.5, 7, wort="merkt"))
        self.bis_wort(7, "merkt")
        self.play(FadeIn(merk, shift=UP * 0.1), run_time=self.rt(0.4, 8))
        schweben(VGroup(chip, merk), 0.025, 0.45)

        # Zweitens: Messbereich
        self.bis(8)
        alles_weg(self, self.rt(0.5, 8, 0.6))
        self.remove(kap)
        self.kapitel("Messbereich")
        zwei = badge("Zweitens", GELB, NAVY, 34).move_to([0, 2.6, 0])
        self.play(FadeIn(zwei, scale=1.2), run_time=self.rt(0.4, 9))
        wackeln(zwei, 0.03, 1.0)
        self.bis(9)
        mb = T("der Messbereich", 48, WEISS, HEAVY).move_to([0, 1.55, 0])
        self.play(FadeIn(mb, shift=UP * 0.2), run_time=self.rt(0.5, 10))
        # Messwerk
        self.bis_wort(10, "Messwerk")
        ant = ValueTracker(0.0)
        mw = messwerk([-4.0, -0.6, 0], ant, 0.9, WEISS, "Messwerk")
        self.play(FadeIn(mw, scale=0.7), run_time=self.rt(0.5, 10, wort="bestimmten"))
        self.bis_wort(10, "bestimmten")
        self.play(ant.animate.set_value(1.0), run_time=self.rt(0.8, 11), rate_func=smooth)
        voll = badge("100 µA = Vollausschlag", GELB, NAVY, 22).next_to(mw, DOWN, 0.55)
        self.play(FadeIn(voll, shift=UP * 0.1), run_time=0.3)
        schweben(voll, 0.02, 0.5)
        self.bis_wort(11, "mehr")
        mehr = badge("mehr messen?", CYAN, NAVY, 26).move_to([-4.0, 1.0, 0])
        self.play(FadeIn(mehr, scale=1.2), run_time=self.rt(0.4, 12))
        wackeln(mehr, 0.04, 1.0)
        # Voltmeter: Vorwiderstand in Reihe
        self.bis_wort(12, "Vorwiderstand")
        xv = 0.6
        mw2 = messwerk([xv + 1.5, -0.25, 0], ant, 0.45)
        rv = widerstand_h([xv - 0.3, -0.25, 0], 1.0, 0.4, CYAN)
        rvt = T("Rᵥ", 26, CYAN, HEAVY).next_to(rv, UP, 0.1)
        dv = VGroup(Line([xv - 1.6, -0.25, 0], rv.get_left()), Line(rv.get_right(), mw2.kreis.get_left())).set_stroke(WEISS, 4)
        in_reihe = badge("in Reihe", CYAN, NAVY, 22).next_to(mw2, DOWN, 0.2)
        dvpol = polung([xv - 1.6, 0.05, 0], [xv + 2.05, 0.05, 0], WEISS, 20)
        self.play(FadeIn(dv), GrowFromCenter(rv), FadeIn(rvt), FadeIn(mw2), FadeIn(dvpol), run_time=self.rt(0.6, 12, wort="Rest"))
        self.play(FadeIn(in_reihe, shift=UP * 0.1), run_time=0.25)
        self.bis_wort(12, "Rest")
        rest_b = badge("übernimmt den Rest der Spannung", CYAN, NAVY, 22).move_to([xv + 0.6, 0.72, 0])
        self.play(FadeIn(rest_b, shift=DOWN * 0.1), aufleuchten(rv, WEISS, 8), run_time=self.rt(0.5, 13))
        schweben(rest_b, 0.02, 0.5)
        # Amperemeter: Parallelwiderstand
        self.bis_wort(13, "Parallelwiderstand")
        xa = 0.6
        mw3 = messwerk([xa + 0.6, -2.3, 0], ant, 0.42)
        rs = widerstand_h([xa + 0.6, -3.25, 0], 1.0, 0.36, GELB)
        rst = T("Shunt", 22, GELB, HEAVY).next_to(rs, DOWN, 0.1)
        da = VGroup(VMobject().set_points_as_corners([[xa - 1.3, -2.3, 0], mw3.kreis.get_left()]),
                    VMobject().set_points_as_corners([[xa - 0.4, -2.3, 0], [xa - 0.4, -3.25, 0], rs.get_left()]),
                    VMobject().set_points_as_corners([rs.get_right(), [xa + 1.6, -3.25, 0], [xa + 1.6, -2.3, 0], [xa + 2.6, -2.3, 0]]),
                    Line(mw3.kreis.get_right(), [xa + 1.6, -2.3, 0])).set_stroke(WEISS, 4)
        dapol = polung([xa - 1.3, -2.0, 0], [xa + 2.6, -2.0, 0], WEISS, 20)
        self.play(FadeIn(da), GrowFromCenter(rs), FadeIn(rst), FadeIn(mw3), FadeIn(dapol), run_time=self.rt(0.6, 13, wort="größten"))
        fls = Fluss([[xa - 1.3, -2.3, 0], [xa - 0.4, -2.3, 0], [xa - 0.4, -3.25, 0], [xa + 1.6, -3.25, 0], [xa + 1.6, -2.3, 0], [xa + 2.6, -2.3, 0]],
                    n=18, tempo=1.3, farbe=GELB, radius=0.05, rand=0.3).set_z_index(3)
        flm = Fluss([[xa - 0.4, -2.3, 0], [xa + 1.6, -2.3, 0]], n=3, tempo=1.0, farbe=GELB, radius=0.04, rand=0.3).set_z_index(3)
        self.add(fls, flm)
        self.bis_wort(13, "größten")
        vorbei = badge("Großteil am Messwerk vorbei", GELB, NAVY, 20).move_to([4.4, -2.95, 0])
        self.play(FadeIn(vorbei, shift=LEFT * 0.1), aufleuchten(rs, WEISS, 8), run_time=self.rt(0.5, 14))
        schweben(vorbei, 0.02, 0.5, 0.3)
        # Drehschalter
        self.bis_wort(14, "Drehschalter")
        alle_updater_weg(mehr, voll)
        self.play(FadeOut(mehr), FadeOut(voll), FadeOut(mw), run_time=0.3)
        mm = multimeter14([-4.3, -0.8, 0], 1.2, modus="V", anzeige="")
        self.play(FadeIn(mm, shift=UP * 0.2), run_time=self.rt(0.5, 15))
        self.bis(15)
        for w in (PI * 0.5, PI * 0.8, PI * 0.2):
            self.play(Rotate(mm.zg, w - mm.zg.get_angle(), about_point=mm.km), run_time=self.rt(0.35, 16))
        schalt = badge("schaltet Widerstände um", WEISS, NAVY, 22).next_to(mm, DOWN, 0.3)
        self.play(FadeIn(schalt, shift=UP * 0.1), run_time=self.rt(0.4, 16))
        # Regel: groesster Bereich zuerst
        self.bis(16)
        alle_updater_weg(rest_b, vorbei, in_reihe)
        self.play(FadeOut(VGroup(mw2, rv, rvt, dv, dvpol, in_reihe, rest_b, mw3, rs, rst, da, dapol, vorbei, schalt)), FadeOut(fls), FadeOut(flm), run_time=0.4)
        regel = karte(VGroup(T("Wert unbekannt?", 32, GELB, BOLD), T("größter Messbereich zuerst,", 30, WEISS, BOLD),
                             T("dann herunter", 30, WEISS, BOLD)).arrange(DOWN, buff=0.18), GELB, 0.35).move_to([2.4, -0.4, 0])
        self.play(FadeIn(regel, shift=LEFT * 0.3), run_time=self.rt(0.6, 17))
        schweben(regel, 0.02, 0.5)
        self.bis_wort(17, "größten")
        stufen = VGroup(*[T(t, 24, GRAU, BOLD) for t in ("1000 V", "200 V", "20 V", "2 V")]).arrange(DOWN, buff=0.15).move_to([-1.3, -0.6, 0])
        self.play(FadeIn(stufen), run_time=0.3)
        for i in range(4):
            self.play(stufen[i].animate.set_color(GELB), *([stufen[i - 1].animate.set_color(GRAU)] if i else []),
                      run_time=self.rt(0.35, 18))
        self.ende()


# --- Szene 6: Widerstand messen (spannungsfrei, ausgebaut), Durchgang, Stromzange --------------------------------
class Szene06(WattScene):
    def construct(self):
        kap = self.kapitel("Widerstand messen")
        mm = multimeter14([-3.8, 0.3, 0], 1.3, modus="Ω", farbe=ORANGE, anzeige="")
        self.play(FadeIn(mm, shift=UP * 0.2), run_time=self.rt(0.6, 1))
        schweben(mm, 0.02, 0.4)
        self.bis_wort(1, "ausmessen")
        r = widerstand_h([0.9, -0.9, 0], 1.3, 0.45, ORANGE)
        rt = T("R = ?", 30, ORANGE, HEAVY).next_to(r, UP, 0.15)
        ll = VGroup(leitung(mm.b_v.get_center(), r.get_right() + RIGHT * 0.1, ROT, 0.9),
                    leitung(mm.b_com.get_center(), r.get_left() + LEFT * 0.1, GRAU, 1.1))
        self.play(FadeIn(r), FadeIn(rt), Create(ll), run_time=self.rt(0.6, 2))
        # eigener Strom
        self.bis_wort(2, "eigenen")
        pts = [mm.b_v.get_center()] + [ll[0].point_from_proportion(v) for v in np.linspace(0, 1, 12)] + \
              [r.get_left() + LEFT * 0.1] + [ll[1].point_from_proportion(1 - v) for v in np.linspace(0, 1, 12)]
        fl = Fluss(pts, n=20, tempo=1.2, farbe=ORANGE, radius=0.05, rand=0.3).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        eig = badge("eigener kleiner Strom", ORANGE, NAVY, 24).move_to([0.9, 1.4, 0])
        self.play(an.animate.set_value(1.0), FadeIn(eig, shift=DOWN * 0.1), run_time=self.rt(0.5, 2, wort="Spannung"))
        schweben(eig, 0.02, 0.5)
        self.bis_wort(2, "Spannung")
        mv = badge("misst U", CYAN, NAVY, 22).next_to(r, DOWN, 0.15)
        self.play(FadeIn(mv, scale=1.2), run_time=self.rt(0.4, 2, wort="rechnet"))
        self.bis_wort(2, "rechnet")
        form = ergebnis("R = U / I", 40).move_to([4.3, 0.6, 0])
        self.play(FadeIn(form, scale=1.2), run_time=self.rt(0.5, 3))
        schweben(form, 0.025, 0.45)
        anz = T("470 Ω", int(24 * 1.3), ORANGE, HEAVY).move_to(mm.disp.get_center())
        self.play(FadeIn(anz), run_time=0.3)
        mm.add(anz)
        # nur spannungsfrei
        self.bis(3)
        warn = VGroup(warnschild(ORIGIN, 0.7), T("nur spannungsfrei", 32, ROT, BOLD)).arrange(RIGHT, buff=0.3).move_to([4.4, -0.6, 0])
        self.play(FadeIn(warn, shift=UP * 0.2), run_time=self.rt(0.6, 5))
        wackeln(warn[0], 0.08, 1.3)
        self.bis_wort(5, "Spannung")
        q = quelle_symbol([0.9, -3.1, 0], "230 V", ROT, 0.42)
        qd = VGroup(VMobject().set_points_as_corners([r.get_left() + LEFT * 0.1, [-0.5, -3.1, 0], q.get_left()]),
                    VMobject().set_points_as_corners([r.get_right() + RIGHT * 0.1, [2.3, -3.1, 0], q.get_right()])).set_stroke(ROT, 3)
        self.play(FadeIn(q), Create(qd), run_time=self.rt(0.5, 5, wort="verfälscht"))
        self.bis_wort(5, "verfälscht")
        kz = kreuz(q.get_center(), 0.5, ROT_HELL, 9)
        self.play(Create(kz), mm.disp.animate.set_fill("#3A1212"), run_time=self.rt(0.4, 5, wort="beschädigen"))
        self.bis_wort(5, "beschädigen")
        self.kamera_wackeln(0.08, 0.4)
        # ausbauen
        self.bis_wort(6, "raus")
        alle_updater_weg(eig)
        self.play(FadeOut(q), FadeOut(qd), FadeOut(kz), FadeOut(eig), mm.disp.animate.set_fill(DISPLAY), run_time=0.3)
        nb = VGroup(widerstand_h([0.9, -2.3, 0], 1.0, 0.36, GRAU), widerstand_h([2.6, -0.9, 0], 1.0, 0.36, GRAU))
        nbd = VGroup(VMobject().set_points_as_corners([r.get_left() + LEFT * 0.1, [-0.3, -2.3, 0], nb[0].get_left()]),
                     VMobject().set_points_as_corners([nb[0].get_right(), [2.1, -2.3, 0], r.get_right() + RIGHT * 0.1]),
                     Line(r.get_right() + RIGHT * 0.1, nb[1].get_left()), Line(nb[1].get_right(), [3.5, -0.9, 0])).set_stroke(GRAU, 3)
        self.play(FadeIn(nb), Create(nbd), run_time=self.rt(0.5, 6, wort="Nachbarn"))
        self.bis_wort(6, "Nachbarn")
        self.play(aufleuchten(nb, ORANGE, 8), run_time=self.rt(0.5, 7))
        nachb = badge("Nachbarn misst du mit", ORANGE, NAVY, 22).move_to([3.5, -1.85, 0])
        self.play(FadeIn(nachb, shift=UP * 0.1), run_time=0.3)
        # Durchgangspruefer
        self.bis_wort(7, "Durchgangsprüfer")
        alle_updater_weg(form, nachb)
        self.play(FadeOut(nachb), FadeOut(nb), FadeOut(nbd), FadeOut(form), FadeOut(warn), run_time=0.3)
        piep = VGroup(T("piep", 32, GRUEN, HEAVY), *[Arc(radius=0.3 + 0.2 * i, start_angle=-PI / 4, angle=PI / 2, stroke_color=GRUEN, stroke_width=4)
                                                     for i in range(3)]).move_to([4.3, 0.3, 0])
        piep[1:].next_to(piep[0], RIGHT, 0.15)
        self.play(FadeIn(piep, scale=1.2), run_time=self.rt(0.5, 7, wort="klein"))
        puls(piep, 0.05, 1.5)
        self.bis_wort(7, "klein")
        kl = badge("R klein", GRUEN, NAVY, 22).next_to(piep, DOWN, 0.25)
        self.play(FadeIn(kl, shift=UP * 0.1), run_time=self.rt(0.4, 8))

        # Stromzange
        self.bis(8)
        alles_weg(self, self.rt(0.5, 8, 0.6))
        self.remove(kap)
        self.kapitel("Stromzange")
        leiter = Line([0.4, 3.2, 0], [0.4, -3.4, 0], stroke_color=METALL, stroke_width=16)
        kern = Line([0.4, 3.2, 0], [0.4, -3.4, 0], stroke_color="#B8742E", stroke_width=7)
        self.play(Create(leiter), run_time=self.rt(0.5, 9))
        self.add(kern)
        fl = Fluss([[0.4, 3.2, 0], [0.4, -3.4, 0]], n=16, tempo=1.6, farbe=GELB, radius=0.06, rand=0.3).set_z_index(3)
        self.add(fl)
        self.bis(9)
        zange = stromzange([0.4, 0.4, 0], 1.3, offen=0.9)
        zange.set_z_index(5)
        zange.shift(RIGHT * 2.8)
        self.play(FadeIn(zange, shift=LEFT * 0.4), run_time=self.rt(0.6, 10))
        self.bis_wort(10, "legt")
        self.play(zange.animate.shift(LEFT * 2.8), run_time=self.rt(0.7, 10, wort="Magnetfeld"), rate_func=smooth)
        zu = stromzange([0.4, 0.4, 0], 1.3, offen=0.0)
        zu.set_z_index(5)
        self.remove(zange)
        self.add(zu)
        anz = T("12,4 A", int(22 * 1.3), GELB, HEAVY).move_to(zu.disp.get_center())
        anz.set_z_index(6)
        self.play(FadeIn(anz), run_time=0.3)
        self.bis_wort(10, "Magnetfeld")
        feld = VGroup(*[DashedVMobject(Circle(0.9 + 0.35 * i, stroke_color=CYAN, stroke_width=3).move_to([0.4, 0.4, 0]), num_dashes=24)
                        for i in range(3)])
        feld.set_z_index(4)
        self.play(LaggedStart(*[Create(f) for f in feld], lag_ratio=0.3), run_time=self.rt(0.8, 11))
        for i, f in enumerate(feld):
            f.add_updater(lambda m, dt, i=i: m.rotate(0.6 * dt * (1 if i % 2 == 0 else -1), about_point=np.array([0.4, 0.4, 0])))
        mf = badge("Magnetfeld des Stroms", CYAN, NAVY, 26).move_to([-3.6, 1.8, 0])
        self.play(FadeIn(mf, shift=RIGHT * 0.1), run_time=0.3)
        schweben(mf, 0.02, 0.5)
        self.bis_wort(11, "auftrennen")
        h1 = VGroup(haken(ORIGIN, 0.4, GRUEN, 7), T("nichts auftrennen", 28, GRUEN, BOLD)).arrange(RIGHT, buff=0.25).move_to([-3.6, 0.3, 0])
        self.play(FadeIn(h1, shift=RIGHT * 0.1), run_time=self.rt(0.5, 11, wort="nichts vom"))
        self.bis_wort(11, "nichts vom")
        h2 = VGroup(haken(ORIGIN, 0.4, GRUEN, 7), T("nichts liegt im Stromkreis", 28, GRUEN, BOLD)).arrange(RIGHT, buff=0.25).move_to([-3.6, -0.6, 0])
        self.play(FadeIn(h2, shift=RIGHT * 0.1), run_time=self.rt(0.5, 12))
        schweben(VGroup(h1, h2), 0.02, 0.5)
        self.bis_wort(12, "Verteiler")
        vt = verteiler([4.9, -1.8, 0], 1.0)
        self.play(FadeIn(vt, shift=UP * 0.2), run_time=self.rt(0.5, 13))
        schweben(vt, 0.025, 0.45)
        self.ende()


# --- Szene 7: Pruefungsaufgabe: Vorwiderstand ---------------------------------------------------------------------
class Szene07(WattScene):
    def construct(self):
        jetzt = badge("Jetzt du!", GELB, NAVY, 40).move_to([4.9, 3.35, 0])
        self.kapitel("Prüfungsaufgabe", FadeIn(jetzt, scale=1.5), run_time=self.rt(0.5, 1))
        wackeln(jetzt, 0.05, 1.2)
        ant = ValueTracker(0.0)
        mw = messwerk([-3.2, 0.9, 0], ant, 0.95, WEISS, "Messwerk")
        self.bis_wort(1, "Messwerk")
        self.play(FadeIn(mw, scale=0.7), run_time=self.rt(0.5, 1, wort="hundert"))
        self.bis_wort(1, "hundert")
        self.play(ant.animate.set_value(1.0), run_time=self.rt(0.6, 1, wort="Innenwiderstand"), rate_func=smooth)
        b1 = badge("100 µA Vollausschlag", GELB, NAVY, 26).move_to([-3.2, -0.95, 0])
        self.play(FadeIn(b1, scale=1.2), run_time=0.3)
        self.bis_wort(1, "Innenwiderstand")
        b2 = badge("Rᵢ = 1 kΩ", WEISS, NAVY, 26).move_to([-3.2, -1.7, 0])
        self.play(FadeIn(b2, scale=1.2), run_time=self.rt(0.4, 2))
        schweben(VGroup(b1, b2), 0.02, 0.5)
        # Ziel: 10 V
        self.bis_wort(2, "zehn")
        xv = 2.0
        mw2 = messwerk([xv + 1.6, 1.0, 0], ant, 0.45)
        rv = widerstand_h([xv - 0.2, 1.0, 0], 1.1, 0.42, CYAN)
        rvt = T("Rᵥ = ?", 30, CYAN, HEAVY).next_to(rv, UP, 0.15)
        dv = VGroup(Line([xv - 1.7, 1.0, 0], rv.get_left()), Line(rv.get_right(), mw2.kreis.get_left())).set_stroke(WEISS, 4)
        klemmen = VGroup(Dot([xv - 1.7, 1.0, 0], 0.09, color=CYAN), Dot([xv + 2.9, 1.0, 0], 0.09, color=CYAN),
                         Line(mw2.kreis.get_right(), [xv + 2.9, 1.0, 0]).set_stroke(WEISS, 4),
                         polung([xv - 1.7, 1.38, 0], [xv + 2.9, 1.38, 0], CYAN, 24))
        self.play(FadeIn(dv), FadeIn(klemmen), FadeIn(mw2), run_time=self.rt(0.5, 2, wort="Volt"))
        zehn = badge("10 V", CYAN, NAVY, 30).move_to([xv + 0.6, 2.2, 0])
        self.play(FadeIn(zehn, scale=1.3), run_time=self.rt(0.4, 3))
        puls(zehn, 0.04, 0.9)
        self.bis(3)
        self.play(GrowFromCenter(rv), FadeIn(rvt), run_time=self.rt(0.5, 4))
        wackeln(rvt, 0.04, 1.0)
        # Denkpause
        self.bis(4)
        countdown(self, [3.8, -1.3, 0], self.t_satz(5))
        # Loesung
        self.bis(5)
        x = 2.6
        l1 = MT('U<sub>M</sub> = 100 µA · 1 kΩ = <span foreground="#FFC400">0,1 V</span>', 30, WEISS, BOLD).move_to([x, -0.4, 0])
        self.bis_wort(6, "hundert")
        self.play(FadeIn(l1, shift=UP * 0.15), aufleuchten(mw2.kreis, GELB, 8), run_time=self.rt(0.7, 6, wort="nullkomma"))
        self.bis_wort(6, "nullkomma")
        um = badge("0,1 V", GELB, NAVY, 22).next_to(mw2, DOWN, 0.15)
        self.play(FadeIn(um, scale=1.2), run_time=self.rt(0.4, 7))
        self.bis_wort(7, "zehn Volt minus")
        l2 = MT('U<sub>V</sub> = 10 V − 0,1 V = <span foreground="#22D3EE">9,9 V</span>', 30, WEISS, BOLD).move_to([x, -1.2, 0])
        self.play(FadeIn(l2, shift=UP * 0.15), aufleuchten(rv, CYAN, 8), run_time=self.rt(0.7, 7, wort="neunkomma"))
        self.bis_wort(7, "neunkomma")
        uv = badge("9,9 V", CYAN, NAVY, 22).next_to(rv, DOWN, 0.15)
        self.play(FadeIn(uv, scale=1.2), run_time=self.rt(0.4, 8))
        self.bis(8)
        l3 = MT('R<sub>V</sub> = 9,9 V / 100 µA', 30, WEISS, BOLD).move_to([x, -2.0, 0])
        self.play(FadeIn(l3, shift=UP * 0.15), run_time=self.rt(0.7, 8, wort="neunundneunzig"))
        self.bis_wort(8, "neunundneunzig")
        erg = ergebnis("Rᵥ = 99 kΩ", 40).move_to([x, -2.9, 0])
        alle_updater_weg(rvt)
        self.play(FadeIn(erg, scale=1.2), Transform(rvt, T("Rᵥ = 99 kΩ", 30, CYAN, HEAVY).next_to(rv, UP, 0.15)), run_time=self.rt(0.5, 9))
        puls(erg, 0.03, 0.9)
        self.bis_wort(9, "hundert Kiloohm")
        ges = badge("ganzes Voltmeter: 100 kΩ", WEISS, NAVY, 24).move_to([xv + 0.6, 2.2, 0])
        alle_updater_weg(zehn)
        self.play(ReplacementTransform(zehn, ges), run_time=self.rt(0.5, 9, wort="genau"))
        self.bis_wort(9, "genau")
        fl = Fluss([[xv - 1.7, 1.0, 0], [xv + 2.9, 1.0, 0]], n=12, tempo=1.2, farbe=GELB, radius=0.05, rand=0.3).set_z_index(3)
        self.add(fl)
        self.play(aufleuchten(mw2.kreis, GELB, 8), run_time=self.rt(0.6, 10))
        self.ende()


# --- Szene 8: typischer Fehler, Aufloesung, Sicherheitsregeln, Zusammenfassung, Abspann -------------------------------
class Szene08(WattScene):
    def construct(self):
        kopf = VGroup(warnschild(ORIGIN, 0.8), T("Typischer Fehler", 40, ROT, BOLD)).arrange(RIGHT, buff=0.3).move_to([0, 3.0, 0])
        self.play(FadeIn(kopf, shift=DOWN * 0.3), run_time=self.rt(0.6, 1))
        wackeln(kopf[0], 0.1, 1.4)
        self.bis(1)
        verg = MT('Strom messen <span foreground="#F2545B">wie Spannung</span>', 40, WEISS, BOLD).move_to([0, 2.0, 0])
        self.play(FadeIn(verg, shift=UP * 0.2), run_time=self.rt(0.6, 2))
        sk = stromkreis([-2.0, -0.6, 0], 4.2, 2.4, 0.95)
        P = sk.P
        fl = Fluss(sk.weg, n=24, tempo=1.0, farbe=GELB, radius=0.055, geschlossen=True).set_z_index(3)
        self.bis_wort(2, "Amperemeter")
        self.play(FadeIn(sk), run_time=self.rt(0.5, 2, wort="parallel"))
        self.add(fl)
        self.bis_wort(2, "parallel")
        am = messgeraet_symbol(P(3.4, 0.0), "A", GELB, 0.36)
        al = VGroup(VMobject().set_points_as_corners([P(2.1, 0.55), P(3.4, 0.55), P(3.4, 0.36)]),
                    VMobject().set_points_as_corners([P(3.4, -0.36), P(3.4, -0.55), P(2.1, -0.55)])).set_stroke(GELB, 3)
        self.play(FadeIn(am, scale=0.6), Create(al), FadeIn(polung(P(3.85, 0.55), P(3.85, -0.55), GELB, 22)), run_time=self.rt(0.5, 2, wort="Kurzschluss"))
        self.bis_wort(2, "Kurzschluss")
        ks_weg = [P(-2.1, 0), P(-2.1, 1.2), P(3.4, 1.2), P(3.4, -1.2), P(-2.1, -1.2)]
        ks = VMobject().set_points_as_corners([P(2.1, 0.55), P(3.4, 0.55), P(3.4, -0.55), P(2.1, -0.55)]).set_stroke(ROT, 10)
        fl.tempo = 3.5
        self.play(Create(ks), run_time=0.3)
        kb = badge("Kurzschluss!", ROT, WEISS, 30).move_to([3.9, 0.9, 0])
        self.play(FadeIn(kb, scale=1.3), aufleuchten(am.kreis, ROT, 9), run_time=self.rt(0.5, 3))
        puls(kb, 0.05, 1.0)
        bogen = Lichtbogen(lambda: am.get_center() + UP * 0.36, lambda: am.get_center() + DOWN * 0.36, GELB, n=8, breite=6, amp=0.2)
        bogen.set_z_index(6)
        self.add(bogen)

        # Aufloesung
        self.bis(3)
        alles_weg(self, self.rt(0.5, 3, 0.5))
        frage = karte(T("Warum hat es geknallt?", 36, WEISS, BOLD), GELB, 0.22).move_to([-0.4, 3.0, 0])
        fz = badge("?", GELB, NAVY, 44).next_to(frage, RIGHT, 0.3)
        self.play(FadeIn(frage, shift=DOWN * 0.3), FadeIn(fz, scale=1.4), run_time=self.rt(0.6, 4))
        wackeln(fz, 0.06, 1.1)
        sd = steckdose([-4.3, -0.3, 0], 1.8)
        mm = multimeter14([2.2, -0.8, 0], 1.4, modus="V", rot_in="A", anzeige="0.0")
        ll = VGroup(leitung2(mm.b_rot.get_center(), sd.loch_l.get_center(), ROT, DOWN * 1.0, RIGHT * 1.6 + DOWN * 0.8),
                    leitung2(mm.b_sw.get_center(), sd.loch_n.get_center(), GRAU, DOWN * 1.2, RIGHT * 1.25 + DOWN * 0.95))
        self.bis_wort(4, "rote")
        self.play(FadeIn(sd), FadeIn(mm), Create(ll), run_time=self.rt(0.6, 4, wort="zehn"))
        schweben(mm, 0.02, 0.4)
        self.bis_wort(4, "zehn")
        rb = badge("10A", ROT, WEISS, 24).next_to(mm.b_a, DOWN, 0.4)
        self.play(FadeIn(rb, scale=1.3), run_time=self.rt(0.4, 4, wort="nicht"))
        puls(rb, 0.05, 1.0)
        self.bis_wort(4, "nicht")
        vb = badge("VΩ", CYAN, NAVY, 24).next_to(mm.b_v, DOWN, 0.4).shift(RIGHT * 0.5)
        pf = pfeil(vb.get_left() + LEFT * 0.05, mm.b_v.get_center() + DOWN * 0.18, CYAN, 4, 0.18)
        self.play(FadeIn(vb, scale=1.2), GrowArrow(pf), run_time=self.rt(0.4, 5))
        # Shunt hinter der Buchse
        self.bis_wort(5, "Shunt")
        sh = widerstand_h(ORIGIN, 0.7, 0.26, GELB).rotate(PI / 2).move_to(mm.b_a.get_center() + UP * 0.8)
        ecke = np.array([mm.b_a.get_center()[0], mm.b_com.get_center()[1] + 1.4, 0])
        ecke2 = np.array([mm.b_com.get_center()[0], mm.b_com.get_center()[1] + 1.4, 0])
        shd = VGroup(Line(mm.b_a.get_center(), sh.get_bottom()), Line(sh.get_top(), ecke), Line(ecke, ecke2), Line(ecke2, mm.b_com.get_center())).set_stroke(GELB, 3)
        sht = badge("0,01 Ω", GELB, NAVY, 22).next_to(mm, RIGHT, 0.25).shift(DOWN * 0.3)
        self.play(mm.koerper.animate.set_fill(opacity=0.35), mm.knopf.animate.set_fill(opacity=0.3), FadeIn(shd), GrowFromCenter(sh), FadeIn(sht, scale=1.2),
                  run_time=self.rt(0.6, 6))
        puls(sht, 0.04, 0.9)
        # Rechnung
        self.bis(6)
        rech = MT('230 V / 0,01 Ω = <span foreground="#F2545B">23 000 A</span>', 34, WEISS, BOLD).move_to([-3.4, -2.75, 0])
        self.play(FadeIn(rech, shift=UP * 0.15), run_time=self.rt(0.7, 6, wort="zwanzigtausend"))
        self.bis_wort(6, "zwanzigtausend")
        rz = badge("rechnerisch", GRAU, WEISS, 20).next_to(rech, DOWN, 0.15)
        self.play(FadeIn(rz, shift=LEFT * 0.1), run_time=self.rt(0.4, 7))
        # Lichtbogen, LS
        self.bis_wort(7, "Lichtbogen")
        bogen = Lichtbogen(lambda: sh.get_bottom(), lambda: sh.get_top(), GELB, n=8, breite=7, amp=0.25)
        bogen.set_z_index(6)
        self.add(bogen)
        self.blitzlicht(GELB, 0.4, 0.5)
        ls = ls_schalter([5.9, 2.2, 0], "B13", 0.8)
        self.play(FadeIn(ls, shift=LEFT * 0.2), run_time=0.3)
        self.play(ls.hebel.animate.shift(DOWN * 0.42 * ls.s), run_time=self.rt(0.4, 8))
        bogen.an = 0.0

        # Regeln
        self.bis(8)
        self.remove(bogen)
        alles_weg(self, self.rt(0.5, 8, 0.6))
        titel = T("Vor jeder Messung", 44, GELB, HEAVY).move_to([0, 3.0, 0])
        self.play(FadeIn(titel, shift=DOWN * 0.2), run_time=self.rt(0.5, 9))
        schweben(titel, 0.02, 0.4)
        regeln = [("Drehschalter prüfen", 9, "Drehschalter"), ("Buchsen prüfen", 9, "Buchsen"), ("Messleitungen prüfen", 9, "Messleitungen"),
                  ("Spannung: Buchse V", 10, None), ("Strom im Netz: Zange", 11, None), ("CAT III mit Sicherung", 12, "CAT")]
        zeilen = VGroup()
        for i, (txt, k, w) in enumerate(regeln):
            z = VGroup(haken(ORIGIN, 0.36, GRUEN, 7), T(txt, 30, WEISS, BOLD)).arrange(RIGHT, buff=0.28)
            z.move_to([-6.2 if i < 3 else 0.9, 1.7 - (i % 3) * 1.1, 0], aligned_edge=LEFT)
            zeilen.add(z)
            if w:
                self.bis_wort(k, w)
            else:
                self.bis(k)
            if i < 2:
                rtv = self.rt(0.5, 9, wort=regeln[i + 1][2])
            elif i < 5:
                rtv = self.rt(0.5, 10 + i - 2)
            else:
                rtv = self.rt(0.5, 12, wort="Sicherung")
            self.play(FadeIn(z[1], shift=RIGHT * 0.2), Create(z[0]), run_time=rtv)
            schweben(z, 0.02, 0.5, 0.2 * i)
        self.bis_wort(12, "Sicherung")
        sich = badge("Sicherung im Gerät", GELB, NAVY, 22).next_to(zeilen[5], DOWN, 0.2).align_to(zeilen[5][1], LEFT)
        self.play(FadeIn(sich, shift=UP * 0.1), run_time=self.rt(0.4, 13))
        self.bis(13)
        fach = VGroup(warnschild(ORIGIN, 0.7), T("Netzspannung: nur Fachkräfte", 32, ROT, BOLD)).arrange(RIGHT, buff=0.3).move_to([0, -2.6, 0])
        self.play(FadeIn(fach, shift=UP * 0.2), run_time=self.rt(0.6, 14))
        wackeln(fach[0], 0.08, 1.3)

        # Zusammengefasst
        self.bis(14)
        alles_weg(self, self.rt(0.5, 14, 0.6))
        zk = T("Zusammengefasst", 44, WEISS, BOLD).move_to([0, 3.0, 0])
        self.play(FadeIn(zk, shift=DOWN * 0.2), run_time=self.rt(0.5, 15))
        schweben(zk, 0.02, 0.4)
        zeilen = [MT('Spannung <span foreground="#22D3EE">parallel</span>, Voltmeter hochohmig', 40, WEISS, BOLD),
                  MT('Strom <span foreground="#FFC400">in Reihe</span>, Amperemeter niederohmig', 40, WEISS, BOLD),
                  MT('Widerstand nur <span foreground="#FF8A3D">spannungsfrei</span> und ausgebaut', 40, WEISS, BOLD)]
        for i, (z, y) in enumerate(zip(zeilen, (1.5, 0.1, -1.3))):
            z.move_to([0, y, 0])
            self.bis(15 + i)
            self.play(FadeIn(z, shift=RIGHT * 0.3), run_time=self.rt(0.6, 16 + i))
            schweben(z, 0.03, 0.45, 0.3 * i)

        # Naechstes Video (Video 15: Di 1.12., laut kalender.md)
        self.bis(18)
        zus = VGroup(zk, *zeilen)
        alle_updater_weg(zus)
        self.play(FadeOut(zus, shift=UP * 0.4), run_time=self.rt(0.5, 18, 0.3))
        self.aufraeumen(*hud_teile(self))
        bild = waage_icon(0.8)
        self.abspann("Brückenschaltung", k=19, bild=bild, datum="ab 1.12.")
        self.bis_wort(19, "Personenwaage")
        self.abspann_video_zeigen(run_time=self.rt(1.0, 20))
        self.bis(20)
        self.abspann_abo_zeigen(run_time=self.rt(1.0, 21))
        self.bis(21)
        self.abspann_abo_zeigen(run_time=self.rt(1.0, 22))
        self.ende_abspann()
