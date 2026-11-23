"""Watt?! Video 13: Innenwiderstand. Eine Klasse pro Abschnitt im Sprechtext (Szene01 = s01 ...).
Rendern (Probe): WATT_CUES=stimme/cues.json $VENV/bin/manim -ql --fps 30 --disable_caching video13_innenwiderstand.py SzeneNN
Rendern (final): WATT_CUES=stimme/cues.json $VENV/bin/manim -r 2560,1440 --fps 60 --disable_caching video13_innenwiderstand.py SzeneNN
Hinweis: In den Cues steht "Ampär" und Kommazahlen zusammengeschrieben ("einskommadrei"); bis_wort nie auf "Ampere".
Roter Faden: Fernbedienung "tot", Messgerät sagt "voll". Metapher: Wasserturm mit verkalktem Rohr (Druck am Hahn sinkt,
sobald Wasser fliesst). Zweites Alltagsbild: Auto, Scheinwerfer werden beim Starten dunkler. Keine Personen im Bild.
"""
import sys
from pathlib import Path
sys.path.insert(0, "/mnt/project-files/youtube-kanal/werkzeuge")
from watt_manim import *

setze_sprechtext(Path(__file__).with_name("video13_sprechtext.txt"))

ORANGE = "#FF8A3D"
ROT_HELL = "#F2545B"
WASSER = "#4FC3E0"
KALK = "#E8E2D0"
ROHR = "#8A97A5"
ROHR_D = "#55606C"
GRUEN = "#5FCB6E"
METALL = "#C3CDD8"
DISPLAY = "#0B2A1E"


# --- allgemeine Bausteine (wie Video 9/12) ---------------------------------------------------
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
    """Gemeinsamer Helligkeitsregler für Punkt-Flüsse (statt FadeIn, das die Bewegung anhält)."""
    t = ValueTracker(start)
    for f in fluesse:
        f.an = t.get_value
    return t


def pulsend(fluss, regler, freq=3.0, lo=0.1):
    """Fluss blinkt wie Stromimpulse (Fernbedienung): Helligkeit = Regler · Impulsform."""
    fluss.an = lambda: regler.get_value() * (lo + (1 - lo) * (0.5 + 0.5 * np.sin(TAU * freq * uhr())) ** 3)
    return fluss


class PfadFluss(Fluss):
    """Wie Fluss, aber die Laufstrecke wird über dt aufsummiert: tempo darf sich ändern, ohne dass Punkte springen."""

    def __init__(self, *args, **kw):
        self._s = 0.0
        super().__init__(*args, **kw)
        self.clear_updaters()
        self.add_updater(lambda m, dt: m._schritt(dt))
        self._schritt(0)

    def _schritt(self, dt):
        self._s += self.tempo * dt
        pts = [np.array(p, dtype=float) for p in self.punkte_fn()]
        seg = [np.linalg.norm(b - a) for a, b in zip(pts[:-1], pts[1:])]
        L = sum(seg)
        cum = np.concatenate([[0], np.cumsum(seg)])
        n = len(self.submobjects)
        an = self.an() if callable(self.an) else self.an
        for i, d in enumerate(self.submobjects):
            s = (self._s + i * L / n) % L
            k = min(int(np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
            a = (s - cum[k]) / max(seg[k], 1e-9)
            d.move_to(pts[k] + a * (pts[k + 1] - pts[k]))
            d.set_fill(opacity=max(0.0, an * min(1.0, s / self.rand, (L - s) / self.rand)))

    def _upd(self):
        pass


def heiss_farbe(h, kalt=METALL):
    """Farbe eines Metallstücks bei Wärme h (0 kalt .. 1 sehr heiss): grau -> orange -> rotorange."""
    h = max(0.0, min(1.0, h))
    if h < 0.6:
        return interpolate_color(ManimColor(kalt), ManimColor(ORANGE), h / 0.6)
    return interpolate_color(ManimColor(ORANGE), ManimColor("#FF5A36"), (h - 0.6) / 0.4)


def waerme_wellen(mitte, staerke, breite=0.6, hoehe=1.0, n=3, farbe=ORANGE, sw=4):
    """Drei flimmernde Wärmelinien über mitte; Deckkraft folgt dem Tracker staerke."""
    m = np.array(mitte, dtype=float)

    def linie(i):
        x = m[0] + (i - (n - 1) / 2) * breite / max(n - 1, 1)
        t = uhr() * 1.3 + i * 0.7
        pts = [m + np.array([x - m[0] + 0.08 * np.sin(4 * u + t * 4), 0.15 + u * hoehe, 0]) for u in np.linspace(0, 1, 12)]
        l = VMobject().set_points_smoothly(pts).set_stroke(farbe, sw)
        a = max(0.0, (staerke.get_value() - 0.35) / 0.65)
        return l.set_stroke(opacity=a * (0.6 + 0.4 * np.sin(t * 3)))

    return VGroup(*[always_redraw(lambda i=i: linie(i)) for i in range(n)])


# --- Gegenstände --------------------------------------------------------------------------------
def batterie_aa(s=1.0):
    k = RoundedRectangle(width=1.6, height=0.62, corner_radius=0.1, stroke_color=WEISS, stroke_width=3,
                         fill_color="#2A3B4D", fill_opacity=1)
    band = Rectangle(width=0.5, height=0.62, stroke_width=0, fill_color=GELB, fill_opacity=1).move_to([-0.55, 0, 0])
    pol = Rectangle(width=0.12, height=0.26, stroke_width=0, fill_color=WEISS, fill_opacity=1).move_to([0.86, 0, 0])
    plus = T("+", 18, WEISS, HEAVY).move_to([0.55, 0, 0])
    minus = T("−", 18, NAVY, HEAVY).move_to([-0.55, 0, 0])
    g = VGroup(k, band, pol, plus, minus).scale(s)
    g.pol_plus = lambda: g[2].get_right()
    g.pol_minus = lambda: g[0].get_left()
    return g


def fernbedienung(s=1.0):
    k = RoundedRectangle(width=0.7, height=1.7, corner_radius=0.2, stroke_color=WEISS, stroke_width=3,
                         fill_color="#1E2B38", fill_opacity=1)
    knoepfe = VGroup(*[Circle(0.07, stroke_width=0, fill_color=GRAU, fill_opacity=1).move_to([x, y, 0])
                       for x in (-0.15, 0.15) for y in (-0.5, -0.2, 0.1)])
    rot = Circle(0.1, stroke_width=0, fill_color=ROT, fill_opacity=1).move_to([0, 0.55, 0])
    ir = Circle(0.07, stroke_width=0, fill_color="#3A2430", fill_opacity=1).move_to([0, 0.8, 0])
    fach = RoundedRectangle(width=0.42, height=0.3, corner_radius=0.05, stroke_color=GRAU, stroke_width=2,
                            fill_opacity=0).move_to([0, -0.7, 0])
    g = VGroup(k, knoepfe, rot, ir, fach).scale(s)
    g.taste, g.ir, g.fach = rot, ir, fach
    return g


def multimeter(mitte, s=1.0, wert=None, fmt=None, farbe=CYAN):
    """Digitalmultimeter von vorn; wert = Funktion (z. B. tracker.get_value) -> mitlaufende Anzeige."""
    m = np.array(mitte, dtype=float)
    k = RoundedRectangle(width=1.6 * s, height=2.4 * s, corner_radius=0.18 * s, stroke_color=WEISS, stroke_width=3,
                         fill_color="#1E2B38", fill_opacity=1).move_to(m)
    disp = RoundedRectangle(width=1.28 * s, height=0.62 * s, corner_radius=0.06 * s, stroke_width=0,
                            fill_color=DISPLAY, fill_opacity=1).move_to(m + UP * 0.72 * s)
    knopf = Circle(0.33 * s, stroke_color=GRAU, stroke_width=3, fill_color=NAVY, fill_opacity=1).move_to(m + DOWN * 0.22 * s)
    zg = Line(m + DOWN * 0.22 * s, m + DOWN * 0.22 * s + np.array([0.2, 0.22, 0]) * s, stroke_color=WEISS, stroke_width=3)
    vz = T("V", int(16 * s), GRAU, BOLD).move_to(m + np.array([0.34, 0.14, 0]) * s)
    b_rot = Circle(0.08 * s, stroke_width=0, fill_color=ROT, fill_opacity=1).move_to(m + np.array([0.4, -0.9, 0]) * s)
    b_sw = Circle(0.08 * s, stroke_width=0, fill_color=WEISS, fill_opacity=1).move_to(m + np.array([-0.4, -0.9, 0]) * s)
    g = VGroup(k, disp, knopf, zg, vz, b_rot, b_sw)
    if wert is not None:
        g.anzeige = Zaehler(wert, fmt or (lambda v: de(v, 2) + " V"), int(26 * s), farbe, HEAVY, ort=disp.get_center())
        g.add(g.anzeige)
    g.b_rot, g.b_sw, g.disp = b_rot, b_sw, disp
    return g


def leitung(a, b, farbe, hang=0.6, sw=5):
    """Messleitung, die leicht durchhängt."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    return CubicBezier(a, a + DOWN * hang, b + DOWN * hang, b, stroke_color=farbe, stroke_width=sw)


def esb(mitte, s=1.0, u0="U₀", ri="Rᵢ", gehaeuse=True, titel=None, farbe=WEISS):
    """Ersatzschaltbild einer Quelle: Spannungsquelle (DIN-Kreis) links, Innenwiderstand oben, Klemmen rechts.
    Lokale Koordinaten über g.P(x, y); Stromweg um eine Last bei x_last: g.weg(x_last)."""
    m = np.array(mitte, dtype=float)

    def P(x, y):
        return m + np.array([x, y, 0]) * s

    q = Circle(0.45 * s, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(P(-1.6, 0))
    strich = Line(P(-1.6, -0.45), P(-1.6, 0.45), stroke_color=farbe, stroke_width=4)
    u0_t = T(u0, int(34 * s), CYAN, HEAVY).move_to(P(-2.45, 0))
    plus = T("+", int(24 * s), WEISS, HEAVY).move_to(P(-1.25, 0.62))
    minus = T("−", int(24 * s), WEISS, HEAVY).move_to(P(-1.25, -0.62))
    d1 = VMobject().set_points_as_corners([P(-1.6, 0.45), P(-1.6, 1.0), P(-0.78, 1.0)]).set_stroke(farbe, 4)
    r = Rectangle(width=1.1 * s, height=0.45 * s, stroke_color=farbe, stroke_width=4, fill_color=NAVY,
                  fill_opacity=1).move_to(P(-0.2, 1.0))
    ri_t = T(ri, int(34 * s), GELB, HEAVY).move_to(P(-0.2, 1.55))
    d2 = Line(P(0.35, 1.0), P(1.4, 1.0), stroke_color=farbe, stroke_width=4)
    d3 = VMobject().set_points_as_corners([P(-1.6, -0.45), P(-1.6, -1.0), P(1.4, -1.0)]).set_stroke(farbe, 4)
    k_o = Dot(radius=0.09 * s, color=WEISS).move_to(P(1.4, 1.0))
    k_u = Dot(radius=0.09 * s, color=WEISS).move_to(P(1.4, -1.0))
    g = VGroup(d1, d2, d3, q, strich, u0_t, plus, minus, r, ri_t, k_o, k_u)
    if gehaeuse:
        # 20.11. (Ivan, V13 «gequetscht»): Gehäuse grösser, damit Rᵢ und U₀ nicht auf der Rahmenlinie liegen
        geh = DashedVMobject(RoundedRectangle(width=4.9 * s, height=3.8 * s, corner_radius=0.3 * s,
                                              stroke_color=GRAU, stroke_width=3).move_to(P(-0.75, 0)), num_dashes=46)
        g.add(geh)
        g.gehaeuse = geh
        if titel:
            g.titel = T(titel, int(26 * s), GRAU, BOLD).move_to(P(-1.4, -1.5))   # 20.11.: im Gehäuse unten links
            g.add(g.titel)
    g.P, g.s = P, s
    g.quelle, g.ri, g.ri_label, g.u0_label, g.k_o, g.k_u = q, r, ri_t, u0_t, k_o, k_u
    g.weg = lambda x_last: [P(-1.6, 0.45), P(-1.6, 1.0), P(x_last, 1.0), P(x_last, -1.0), P(-1.6, -1.0), P(-1.6, -0.45)]
    return g


def last(e, x=3.0, name="Rₐ", farbe=WEISS):
    """Verbraucher rechts an den Klemmen des ESB e."""
    P = e.P
    r = Rectangle(width=0.45 * e.s, height=1.0 * e.s, stroke_color=farbe, stroke_width=4, fill_color=NAVY,
                  fill_opacity=1).move_to(P(x, 0))
    d = VMobject().set_points_as_corners([P(1.4, 1.0), P(x, 1.0), P(x, 0.5)]).set_stroke(farbe, 4)
    d2 = VMobject().set_points_as_corners([P(x, -0.5), P(x, -1.0), P(1.4, -1.0)]).set_stroke(farbe, 4)
    t = T(name, int(32 * e.s), CYAN, HEAVY).move_to(P(x + 0.65, 0))
    g = VGroup(d, d2, r, t)
    g.r, g.t = r, t
    return g


def voltmeter(e, x=2.2, farbe=CYAN):
    """Voltmeter-Symbol zwischen den Klemmen des ESB e."""
    P = e.P
    c = Circle(0.36 * e.s, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(P(x, 0))
    v = T("V", int(28 * e.s), farbe, HEAVY).move_to(P(x, 0))
    d = Line(P(1.4, 1.0), P(x, 1.0), stroke_color=farbe, stroke_width=3)
    d1 = Line(P(x, 1.0), P(x, 0.36), stroke_color=farbe, stroke_width=3)
    d2 = Line(P(x, -0.36), P(x, -1.0), stroke_color=farbe, stroke_width=3)
    d3 = Line(P(x, -1.0), P(1.4, -1.0), stroke_color=farbe, stroke_width=3)
    return VGroup(d, d1, d2, d3, c, v)


def kurzschluss(e, x=2.1):
    P = e.P
    return VMobject().set_points_as_corners([P(1.4, 1.0), P(x, 1.0), P(x, -1.0), P(1.4, -1.0)]).set_stroke(ROT, 8)


def manometer(mitte, wert, r=0.45, farbe=WEISS):
    """Rundes Manometer; Zeiger folgt dem Tracker wert (0 .. 1)."""
    m = np.array(mitte, dtype=float)
    ring = Circle(r, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(m)
    skala = VGroup(*[Line(m + r * 0.76 * np.array([np.cos(a), np.sin(a), 0]), m + r * 0.9 * np.array([np.cos(a), np.sin(a), 0]),
                          stroke_color=farbe, stroke_width=2) for a in np.linspace(PI * 1.2, -PI * 0.2, 7)])
    rot = Arc(radius=r * 0.83, start_angle=-PI * 0.2, angle=PI * 0.35, arc_center=m, stroke_color=ROT, stroke_width=4)

    def zeiger():
        a = PI * 1.2 - PI * 1.4 * max(0.0, min(1.0, wert.get_value()))
        return Line(m, m + r * 0.8 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=GELB, stroke_width=4)

    g = VGroup(ring, skala, rot, always_redraw(zeiger), Dot(radius=0.06, color=GELB).move_to(m))
    return g


def auto_front(mitte, s=1.0):
    """Auto von vorn mit Scheinwerfern; Helligkeit über g.hell (0 .. 1)."""
    m = np.array(mitte, dtype=float)

    def P(x, y):
        return m + np.array([x, y, 0]) * s

    raeder = VGroup(*[RoundedRectangle(width=0.6 * s, height=0.5 * s, corner_radius=0.1 * s, stroke_width=0,
                                       fill_color="#1A2430", fill_opacity=1).move_to(P(x, -1.35)) for x in (-1.75, 1.75)])
    karosse = RoundedRectangle(width=4.4 * s, height=2.0 * s, corner_radius=0.35 * s, stroke_color=WEISS, stroke_width=4,
                               fill_color=NAVY2, fill_opacity=1).move_to(P(0, -0.3))
    dach = VMobject().set_points_as_corners([P(-1.6, 0.68), P(-1.2, 1.6), P(1.2, 1.6), P(1.6, 0.68), P(-1.6, 0.68)]
                                            ).set_stroke(WEISS, 4).set_fill(NAVY2, 1)
    scheibe = VMobject().set_points_as_corners([P(-1.32, 0.75), P(-1.05, 1.42), P(1.05, 1.42), P(1.32, 0.75), P(-1.32, 0.75)]
                                               ).set_stroke(width=0).set_fill(CYAN, 0.3)
    grill = RoundedRectangle(width=1.5 * s, height=0.36 * s, corner_radius=0.1 * s, stroke_color=GRAU, stroke_width=3,
                             fill_color=NAVY, fill_opacity=1).move_to(P(0, -0.6))
    kz = RoundedRectangle(width=1.0 * s, height=0.22 * s, corner_radius=0.04 * s, stroke_width=0, fill_color=WEISS,
                          fill_opacity=0.85).move_to(P(0, -1.05))
    hell = ValueTracker(1.0)
    lampen = VGroup()
    for x in (-1.5, 1.5):
        glow = Circle(0.7 * s, stroke_width=0, fill_color=GELB, fill_opacity=0.3).move_to(P(x, -0.1))
        lampe = Circle(0.34 * s, stroke_color=WEISS, stroke_width=3, fill_color=GELB, fill_opacity=1).move_to(P(x, -0.1))
        glow.add_updater(lambda g, h=hell: g.set_fill(opacity=0.35 * h.get_value()))
        lampe.add_updater(lambda l, h=hell: l.set_fill(interpolate_color(ManimColor("#4A3C10"), ManimColor(GELB),
                                                                         h.get_value()), 1))
        lampen.add(glow, lampe)
    g = VGroup(raeder, karosse, dach, scheibe, grill, kz, lampen)
    g.hell, g.P, g.lampen = hell, P, lampen
    return g


def autobatterie(mitte, s=1.0):
    m = np.array(mitte, dtype=float)
    k = RoundedRectangle(width=3.0 * s, height=1.5 * s, corner_radius=0.12 * s, stroke_color=WEISS, stroke_width=4,
                         fill_color="#1E2B38", fill_opacity=1).move_to(m)
    pole = VGroup(*[Circle(0.2 * s, stroke_color=ROHR_D, stroke_width=3, fill_color=METALL, fill_opacity=1
                           ).move_to(m + np.array([x, 0.75, 0]) * s) for x in (-0.9, 0.9)])
    lab = VGroup(T("−", int(30 * s), WEISS, HEAVY).move_to(m + np.array([-0.9, 0.3, 0]) * s),
                 T("+", int(30 * s), ROT, HEAVY).move_to(m + np.array([0.9, 0.3, 0]) * s))
    g = VGroup(k, pole, lab)
    g.pol_minus, g.pol_plus = pole[0], pole[1]
    return g


def schraubenschluessel(mitte, s=1.0, winkel=0.0):
    griff = RoundedRectangle(width=2.6 * s, height=0.32 * s, corner_radius=0.16 * s, stroke_color=ROHR_D, stroke_width=3,
                             fill_color=METALL, fill_opacity=1)
    k1 = Circle(0.38 * s, stroke_color=ROHR_D, stroke_width=3, fill_color=METALL, fill_opacity=1).move_to(LEFT * 1.3 * s)
    k2 = k1.copy().move_to(RIGHT * 1.3 * s)
    m1 = Rectangle(width=0.3 * s, height=0.32 * s, stroke_width=0, fill_color=NAVY, fill_opacity=1).move_to(LEFT * 1.52 * s + UP * 0.1 * s)
    m2 = m1.copy().move_to(RIGHT * 1.52 * s + UP * 0.1 * s)
    g = VGroup(griff, k1, k2, m1, m2).rotate(winkel).move_to(mitte)
    g.metall = VGroup(griff, k1, k2)
    return g


def chip(mitte, s=1.0, farbe=GRAU):
    k = Square(0.7 * s, stroke_color=farbe, stroke_width=4, fill_color=NAVY2, fill_opacity=1).move_to(mitte)
    beine = VGroup()
    for i in range(4):
        y = -0.26 + i * 0.173
        beine.add(Line(k.get_left() + UP * y * s, k.get_left() + UP * y * s + LEFT * 0.18 * s, stroke_color=farbe, stroke_width=3))
        beine.add(Line(k.get_right() + UP * y * s, k.get_right() + UP * y * s + RIGHT * 0.18 * s, stroke_color=farbe, stroke_width=3))
    g = VGroup(beine, k)
    g.k = k
    return g


def schluessel(mitte, s=1.0):
    ring = Circle(0.3 * s, stroke_color=METALL, stroke_width=5, fill_color=NAVY2, fill_opacity=1)
    bart = Rectangle(width=0.9 * s, height=0.16 * s, stroke_width=0, fill_color=METALL, fill_opacity=1).move_to(DOWN * 0.7 * s)
    z1 = Rectangle(width=0.14 * s, height=0.18 * s, stroke_width=0, fill_color=METALL, fill_opacity=1).move_to(DOWN * 1.05 * s + RIGHT * 0.3 * s)
    z2 = z1.copy().shift(LEFT * 0.25 * s)
    bart.rotate(PI / 2)
    return VGroup(ring, bart, z1, z2).move_to(mitte)


def netzteil_icon(s=1.0):
    k = RoundedRectangle(width=1.0, height=0.7, corner_radius=0.1, stroke_color=WEISS, stroke_width=3, fill_color="#2A3B4D",
                         fill_opacity=1)
    st = VGroup(*[Rectangle(width=0.1, height=0.3, stroke_width=0, fill_color=METALL, fill_opacity=1).move_to([x, 0.5, 0])
                  for x in (-0.2, 0.2)])
    kabel = Line([0.5, 0, 0], [0.95, 0, 0], stroke_color=GRAU, stroke_width=4)
    return VGroup(k, st, kabel).scale(s)


def countdown(scene, mitte, t_ende):
    """Denkpause: Ring läuft ab bis t_ende (Muster Video 12)."""
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


def u_balken(mitte, hoehe, anteil, farbe=CYAN, breite=0.5, name=None):
    """Senkrechter Spannungsbalken, Höhe folgt dem Tracker anteil (0..1 von hoehe)."""
    m = np.array(mitte, dtype=float)
    rahmen = Rectangle(width=breite, height=hoehe, stroke_color=GRAU, stroke_width=2, fill_opacity=0).move_to(m + UP * hoehe / 2)
    fuell = always_redraw(lambda: Rectangle(width=breite, height=max(0.01, hoehe * anteil.get_value()), stroke_width=0,
                                            fill_color=farbe, fill_opacity=0.9).move_to(m + UP * hoehe * anteil.get_value() / 2))
    g = VGroup(rahmen, fuell)
    if name:
        g.add(T(name, 26, farbe, HEAVY).next_to(rahmen, DOWN, 0.12))
    return g


# --- Szene 1: Haken -------------------------------------------------------------------------------
# Fernbedienung gross links, Fernseher rechts bleibt dunkel. Batterie raus, Messgerät zeigt 1,3 V (grün, "fast voll"),
# Batterie zurück, wieder nichts. Dann rhetorische Frage.
class Szene01(WattScene):
    def construct(self):
        tv = VGroup(RoundedRectangle(width=5.4, height=3.3, corner_radius=0.15, stroke_color=GRAU, stroke_width=5,
                                     fill_color="#06101A", fill_opacity=1),
                    Rectangle(width=1.6, height=0.16, stroke_width=0, fill_color=GRAU, fill_opacity=1).move_to([0, -1.75, 0]),
                    Rectangle(width=2.6, height=0.08, stroke_width=0, fill_color=GRAU, fill_opacity=1).move_to([0, -1.85, 0])
                    ).move_to([3.0, 1.3, 0])
        fb = fernbedienung(2.3).move_to([-3.4, 0.2, 0])
        zelle = batterie_aa(0.62).rotate(PI / 2).move_to(fb.fach.get_center())
        self.add(tv, fb, zelle)
        schweben(VGroup(fb, zelle), 0.04, 0.4)
        schweben(tv, 0.02, 0.35, 0.3)

        def druecken(k):
            self.play(fb.taste.animate.scale(0.75).set_fill("#A02838"), run_time=0.15)
            self.play(fb.taste.animate.scale(1 / 0.75).set_fill(ROT), run_time=self.rt(0.25, k))

        self.bis(0, 0.1)
        druecken(0)
        dunkel = badge("bleibt dunkel", GRAU, WEISS, 28).move_to(tv.get_center() + DOWN * 0.3)
        self.play(FadeIn(dunkel, scale=0.8), run_time=self.rt(0.5, 1))
        wackeln(dunkel, 0.04, 0.9)

        # Batterie raus und Messgerät dran
        self.bis_wort(1, "raus")
        alle_updater_weg(fb, zelle)
        schweben(fb, 0.04, 0.4)
        self.play(zelle.animate.rotate(-PI / 2).scale(2.4).move_to([0.6, -2.25, 0]), run_time=self.rt(0.8, 1, 0.55))
        schweben(zelle, 0.03, 0.45)
        self.bis_wort(1, "Messgerät")
        u = ValueTracker(0.0)
        mm = multimeter([4.9, -1.9, 0], 0.95, wert=u.get_value)
        l_rot = always_redraw(lambda: leitung(mm.b_rot.get_center(), zelle.pol_plus() + RIGHT * 0.05, ROT, 0.5))
        l_sw = always_redraw(lambda: leitung(mm.b_sw.get_center(), zelle.pol_minus() + LEFT * 0.05, GRAU, 0.7))
        self.play(FadeIn(mm, shift=LEFT * 0.3), run_time=self.rt(0.5, 1, 0.85))
        self.add(l_rot, l_sw)
        self.play(Create(l_rot), Create(l_sw), run_time=self.rt(0.5, 2))
        schweben(mm, 0.02, 0.4, 0.5)

        # 1,3 V, fast voll
        self.bis(2)
        self.play(u.animate.set_value(1.30), run_time=self.rt(1.0, 2, wort="also"), rate_func=smooth)
        self.bis_wort(2, "fast")
        self.play(mm.disp.animate.set_fill("#1E6B3A"), run_time=0.3)
        voll = badge("fast voll", GRUEN, NAVY, 34).next_to(mm, UP, 0.3)
        self.play(FadeIn(voll, scale=1.2), run_time=self.rt(0.5, 3))
        puls(voll, 0.04, 0.9)

        # zurück, drücken, nichts
        self.bis_wort(3, "zurück")
        l_rot.clear_updaters()
        l_sw.clear_updaters()
        alle_updater_weg(zelle, voll)
        self.play(FadeOut(l_rot), FadeOut(l_sw), FadeOut(voll),
                  zelle.animate.rotate(PI / 2).scale(1 / 2.4).move_to(fb.fach.get_center()), run_time=self.rt(0.8, 3, wort="drückst"))
        self.bis_wort(3, "drückst")
        druecken(3)
        self.bis_wort(3, "nichts")
        self.play(aufleuchten(dunkel[0], WEISS, 5), run_time=self.rt(0.5, 4))

        # rhetorische Frage
        schleier, fz = self.rhetorische_frage(4)
        self.ende()


# --- Szene 2: Intro ---------------------------------------------------------------------------------
class Szene02(WattScene):
    def construct(self):
        logo = self.logo_intro(k_weiter=1)
        self.bis(1)
        self.play(logo.animate.scale(0.3).move_to([0, 2.85, 0]), run_time=self.rt(0.8, 1, 0.3), rate_func=smooth)
        self.bis_wort(1, "Innenwiderstand")
        titel = T("Innenwiderstand", 92, GELB, HEAVY).move_to([0, 1.0, 0])
        self.play(Write(titel), run_time=self.rt(0.8, 2))
        schweben(titel, 0.035, 0.45)

        self.bis_wort(2, "beide")
        trio = VGroup(fernbedienung(0.8), batterie_aa(0.8), multimeter(ORIGIN, 0.6)).arrange(RIGHT, buff=0.45).move_to([-3.6, -1.6, 0])
        frage = badge("Wer lügt?", GELB, NAVY, 34).next_to(trio, UP, 0.35)
        self.play(FadeIn(trio, shift=UP * 0.2), FadeIn(frage, scale=1.2), run_time=self.rt(0.7, 2, wort="Wahrheit"))
        schweben(trio, 0.03, 0.45)
        wackeln(frage, 0.04, 1.0)
        self.bis_wort(2, "Auto")
        auto = auto_front([3.6, -1.9, 0], 0.8)
        self.play(FadeIn(auto, shift=UP * 0.2), run_time=self.rt(0.6, 2, wort="Starten"))
        schweben(auto, 0.03, 0.4, 0.4)
        self.bis_wort(2, "dunkler")
        self.play(auto.hell.animate.set_value(0.3), run_time=0.35)
        self.play(auto.hell.animate.set_value(1.0), run_time=self.rt(0.8, 3))
        self.ende()


# --- Szene 3: Wasserturm -> Ersatzschaltbild, Uₖ = U0 - I * Ri ------------------------------------------
class Szene03(WattScene):
    def construct(self):
        f = self.camera.frame
        f.set(width=10.4).move_to([-3.2, 0.0, 0])
        self.kapitel("Wasserturm")

        # Turm: Tank oben, Beine, Boden
        tank = RoundedRectangle(width=2.8, height=1.1, corner_radius=0.2, stroke_color=WEISS, stroke_width=4,
                                fill_color=NAVY2, fill_opacity=1).move_to([-5.2, 1.75, 0])
        wasser = Rectangle(width=2.6, height=0.8, stroke_width=0, fill_color=WASSER, fill_opacity=0.75).move_to([-5.2, 1.6, 0])
        welle = always_redraw(lambda: VMobject().set_points_smoothly(
            [np.array([-6.5 + 2.6 * u, 2.0 + 0.04 * np.sin(8 * u + 3 * uhr()), 0]) for u in np.linspace(0, 1, 14)]
        ).set_stroke(WEISS, 3, opacity=0.6))
        beine = VGroup(Line([-6.3, 1.2, 0], [-6.55, -2.6, 0]), Line([-4.1, 1.2, 0], [-3.85, -2.6, 0]),
                       Line([-6.0, -0.4, 0], [-4.4, -0.4, 0]), Line([-6.15, -1.6, 0], [-4.25, -1.6, 0])).set_stroke(GRAU, 5)
        boden = Line([-7.6, -2.6, 0], [0.9, -2.6, 0], stroke_color=GRAU, stroke_width=4)
        self.play(FadeIn(beine), FadeIn(boden), GrowFromCenter(tank), run_time=self.rt(0.7, 0, 0.6))
        self.add(wasser, welle)
        self.play(FadeIn(wasser), run_time=self.rt(0.4, 1))

        # Manometer am Turm: voller Druck
        self.bis_wort(1, "Manometer")
        p1 = ValueTracker(0.0)
        stub1 = Line([-3.8, 1.75, 0], [-3.4, 1.75, 0], stroke_color=ROHR, stroke_width=6)
        m1 = manometer([-3.0, 1.75, 0], p1, 0.42)
        self.play(FadeIn(stub1), FadeIn(m1), run_time=self.rt(0.4, 1, wort="vollen"))
        self.play(p1.animate.set_value(0.95), run_time=self.rt(0.7, 2), rate_func=smooth)
        voll = badge("voller Druck", CYAN, NAVY, 26).move_to([-2.4, 0.9, 0])
        self.play(FadeIn(voll, shift=DOWN * 0.1), run_time=self.rt(0.4, 2))
        schweben(voll, 0.02, 0.5)

        # Rohr mit Kalk zum Hahn
        self.bis(2)
        weg = [np.array(p, dtype=float) for p in [[-5.2, 1.2, 0], [-5.2, -1.3, 0], [-1.4, -1.3, 0], [-1.4, -1.75, 0]]]
        rohr = VMobject().set_points_as_corners(weg[:3]).set_stroke(ROHR, 22)
        bohr = VMobject().set_points_as_corners(weg[:3]).set_stroke(NAVY, 12)
        hahn = VGroup(RoundedRectangle(width=0.55, height=0.42, corner_radius=0.08, stroke_color=ROHR_D, stroke_width=3,
                                       fill_color=ROHR, fill_opacity=1).move_to([-1.4, -1.3, 0]),
                      Rectangle(width=0.22, height=0.35, stroke_width=0, fill_color=ROHR, fill_opacity=1).move_to([-1.4, -1.62, 0]))
        griff = VGroup(Line([-1.4, -1.1, 0], [-1.4, -0.75, 0], stroke_color=ROHR_D, stroke_width=5),
                       RoundedRectangle(width=0.5, height=0.14, corner_radius=0.07, stroke_width=0, fill_color=ROT,
                                        fill_opacity=1).move_to([-1.4, -0.72, 0]))
        self.play(Create(rohr), run_time=self.rt(0.8, 2, wort="verkalktes"))
        self.add(bohr)
        self.bis_wort(2, "verkalktes")
        rng = np.random.default_rng(4)
        kalk = VGroup()
        for i in range(16):
            x = -4.6 + i * 0.19
            oben = i % 2 == 0
            kalk.add(Ellipse(width=0.3 + 0.1 * rng.random(), height=0.14 + 0.06 * rng.random(), stroke_width=0,
                             fill_color=KALK, fill_opacity=0.95).move_to([x, -1.3 + (0.12 if oben else -0.12), 0]))
        eng = badge("verkalkt: eng", KALK, NAVY, 24).move_to([-3.1, -0.65, 0])
        self.play(LaggedStart(*[GrowFromCenter(k) for k in kalk], lag_ratio=0.05), run_time=self.rt(0.8, 2, wort="Wasserhahn"))
        self.play(FadeIn(eng, shift=UP * 0.1), run_time=0.3)
        schweben(eng, 0.02, 0.5, 0.3)
        self.bis_wort(2, "Wasserhahn")
        self.play(FadeIn(hahn), FadeIn(griff), run_time=self.rt(0.4, 3))

        # Hahn zu: gleicher Druck am Hahn
        self.bis_wort(3, "fließt")
        p2 = ValueTracker(0.0)
        stub2 = Line([-1.4, -1.1, 0], [-1.4, -1.1, 0])
        m2 = manometer([-0.3, -0.35, 0], p2, 0.42)
        leit2 = VMobject().set_points_as_corners([[-1.1, -1.3, 0], [-0.3, -1.3, 0], [-0.3, -0.8, 0]]).set_stroke(ROHR, 6)
        self.play(Create(leit2), FadeIn(m2), run_time=self.rt(0.5, 3, wort="derselbe"))
        self.bis_wort(3, "derselbe")
        self.play(p2.animate.set_value(0.95), run_time=self.rt(0.7, 4), rate_func=smooth)
        gleich = badge("gleicher Druck", CYAN, NAVY, 24).move_to([0.3, 0.45, 0])
        self.play(FadeIn(gleich, shift=DOWN * 0.1), run_time=self.rt(0.3, 4))
        schweben(gleich, 0.02, 0.5, 0.6)

        # Hahn auf: Wasser fliesst, Druck am Hahn sinkt, dünner Strahl
        self.bis_wort(4, "auf")
        fl = PfadFluss(weg, n=34, tempo=1.1, farbe=WASSER, radius=0.05).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        strahl = PfadFluss([[-1.4, -1.8, 0], [-1.4, -2.55, 0]], n=5, tempo=1.6, farbe=WASSER, radius=0.04).set_z_index(3)
        strahl.an = an.get_value
        self.add(strahl)
        self.play(Rotate(griff, -PI / 2, about_point=np.array([-1.4, -1.1, 0])), an.animate.set_value(1.0),
                  run_time=self.rt(0.7, 4, wort="durch"))
        self.bis_wort(4, "enge")
        self.play(aufleuchten(VGroup(*kalk), GELB, 4), run_time=self.rt(0.6, 5))
        self.bis_wort(5, "verloren")
        alle_updater_weg(gleich)
        verl = badge("Druck geht verloren", ORANGE, NAVY, 24).move_to([-3.1, -0.65, 0])
        self.play(p2.animate.set_value(0.35), ReplacementTransform(eng, verl), FadeOut(gleich),
                  run_time=self.rt(0.8, 5, wort="dünner"), rate_func=smooth)
        schweben(verl, 0.02, 0.5, 0.3)
        self.bis_wort(5, "dünner")
        duenn = badge("dünner Strahl", WASSER, NAVY, 24).move_to([0.2, -2.1, 0])
        self.play(FadeIn(duenn, shift=LEFT * 0.1), run_time=self.rt(0.4, 6))
        schweben(duenn, 0.02, 0.5, 0.1)

        # Batterie genauso: Kamera raus, Ersatzschaltbild rechts
        self.bis(6)
        self.play(f.animate.set(width=config.frame_width).move_to(ORIGIN), run_time=self.rt(1.2, 6, 0.7), rate_func=smooth)
        e = esb([3.3, 1.0, 0], 0.95, titel="Batterie")
        self.play(Create(e.gehaeuse), FadeIn(e.titel), run_time=self.rt(0.6, 7))
        # Quelle U0
        self.bis_wort(7, "Spannungsquelle")
        self.play(GrowFromCenter(e.quelle), FadeIn(e[4]), FadeIn(e[6]), FadeIn(e[7]), run_time=self.rt(0.5, 7, wort="Leerlaufspannung"))
        self.bis_wort(7, "Leerlaufspannung")
        ll = badge("Leerlaufspannung U₀", CYAN, NAVY, 26).move_to([2.2, -1.25, 0])
        self.play(FadeIn(e.u0_label, scale=1.3), FadeIn(ll, shift=UP * 0.1), run_time=self.rt(0.5, 8))
        puls(e.u0_label, 0.04, 0.8)
        schweben(ll, 0.02, 0.5)
        # ideale Quelle gegen echte Quelle (Ivan 23.11.)
        self.bis_wort(8, "Papier")
        idq = badge("ideal: Spannung bleibt gleich", CYAN, NAVY, 20).move_to([4.4, -2.05, 0])   # 23.11.: unter dem Rahmen, frei von Rand und Symbolen
        self.play(FadeIn(idq, shift=UP * 0.1), run_time=self.rt(0.5, 9, wort="ideale"))
        schweben(idq, 0.02, 0.5)
        self.bis_wort(9, "ideale")
        self.play(aufleuchten(idq, WEISS, 3), run_time=self.rt(0.5, 10))
        self.bis_wort(10, "nach")
        eq = badge("echt: Spannung sinkt unter Last", ORANGE, NAVY, 20).move_to([4.4, -2.75, 0])
        self.play(FadeIn(eq, shift=UP * 0.1), run_time=self.rt(0.5, 11))
        schweben(eq, 0.02, 0.5, 0.3)
        self.bis_wort(11, "weniger")
        self.play(aufleuchten(eq, WEISS, 3), run_time=self.rt(0.5, 12))
        self.bis_wort(12, "Widerstand")
        self.play(aufleuchten(e.gehaeuse, GELB, 4), run_time=self.rt(0.6, 13))
        alle_updater_weg(idq, eq)
        self.play(FadeOut(idq), FadeOut(eq), run_time=self.rt(0.3, 13, 0.05))
        # Widerstand davor
        self.bis_wort(13, "Davor")
        self.play(Create(e[0]), Create(e[2]), run_time=self.rt(0.5, 13, wort="Rohr"))
        self.bis_wort(13, "Rohr")
        # 23.11.: statt Pfeil quer durchs Bild leuchtet der Chip «Druck geht verloren» auf
        self.play(aufleuchten(verl, WEISS, 4), run_time=self.rt(0.5, 13, wort="Widerstand"))
        self.bis_wort(13, "Widerstand")
        self.play(GrowFromCenter(e.ri), Create(e[1]), FadeIn(e.k_o), FadeIn(e.k_u), run_time=self.rt(0.5, 14))
        self.bis_wort(14, "Innenwiderstand")
        iw = badge("Innenwiderstand Rᵢ", GELB, NAVY, 26).move_to([4.7, -1.25, 0])   # 23.11.: war rechts abgeschnitten
        alle_updater_weg(ll)
        self.play(FadeIn(e.ri_label, scale=1.3), ReplacementTransform(ll, iw), run_time=self.rt(0.5, 15))
        puls(e.ri_label, 0.04, 0.8)
        schweben(iw, 0.02, 0.5, 0.4)
        # in jeder echten Quelle
        self.bis_wort(15, "Akku")
        ik = VGroup(batterie_aa(0.7), T("Akku", 22, WEISS, BOLD)).arrange(DOWN, buff=0.1)
        ik2 = VGroup(netzteil_icon(0.7), T("Netzteil", 22, WEISS, BOLD)).arrange(DOWN, buff=0.1)
        reihe = VGroup(ik, ik2).arrange(RIGHT, buff=0.7).move_to([3.7, -2.5, 0])
        self.play(FadeIn(ik, shift=UP * 0.15), run_time=self.rt(0.4, 15, wort="Netzteil"))
        self.bis_wort(15, "Netzteil")
        self.play(FadeIn(ik2, shift=UP * 0.15), run_time=self.rt(0.4, 16))
        schweben(reihe, 0.025, 0.45)

        # kein Strom: Klemmenspannung = U0
        self.bis(16)
        alle_updater_weg(iw, reihe)
        self.play(FadeOut(iw), FadeOut(reihe), run_time=self.rt(0.4, 16, 0.3))
        vm = voltmeter(e, 2.2)
        self.play(FadeIn(vm), run_time=self.rt(0.5, 16, wort="keine"))
        self.bis_wort(16, "keine")
        null = badge("0 V", CYAN, NAVY, 24).next_to(e.ri, DOWN, 0.12)
        self.play(FadeIn(null, scale=1.2), run_time=self.rt(0.4, 16, wort="Klemmen"))
        self.bis_wort(16, "Klemmen")
        ant = ValueTracker(1.0)
        bal = u_balken([6.55, -0.1, 0], 2.2, ant, CYAN, 0.45, "Uₖ")
        u0_strich = DashedLine([6.2, 2.1, 0], [6.9, 2.1, 0], stroke_color=WEISS, stroke_width=3)
        u0_t = T("U₀", 24, WEISS, BOLD).next_to(u0_strich, UP, 0.08)
        self.play(FadeIn(bal), FadeIn(u0_strich), FadeIn(u0_t), run_time=self.rt(0.6, 17))
        ukb = badge("Uₖ = U₀", CYAN, NAVY, 28).move_to([2.6, -1.3, 0])
        self.play(FadeIn(ukb, shift=UP * 0.1), run_time=self.rt(0.4, 17))
        schweben(ukb, 0.02, 0.5)

        # Strom fliesst: an Ri faellt I * Ri ab
        self.bis(17)
        la = last(e, 3.0, "")  # Label Rₐ kollidierte mit dem Uₖ-Balken (Final-Check 4.11.)
        fl2 = PfadFluss(e.weg(3.0), n=30, tempo=1.0, farbe=GELB, radius=0.055).set_z_index(3)
        an2 = einschalten(fl2)
        self.add(fl2)
        self.play(FadeIn(la), an2.animate.set_value(1.0), run_time=self.rt(0.6, 17, wort="fällt"))
        self.bis_wort(17, "fällt")
        iri = badge("I · Rᵢ", ORANGE, NAVY, 24).next_to(e.ri, DOWN, 0.12)
        alle_updater_weg(ukb)
        self.play(ReplacementTransform(null, iri), ant.animate.set_value(0.75), FadeOut(ukb), aufleuchten(e.ri, ORANGE, 8),
                  run_time=self.rt(0.8, 18), rate_func=smooth)
        puls(iri, 0.05, 1.0)
        self.bis(18)
        form = ergebnis("Uₖ = U₀ − I · Rᵢ", 40).move_to([4.0, -2.3, 0])   # 20.11.: frei vom Chip «dünner Strahl»
        self.play(FadeIn(form, scale=1.15), run_time=self.rt(0.7, 18, 0.5))
        schweben(form, 0.025, 0.45)
        self.bis_wort(18, "minus")
        self.play(aufleuchten(iri[0], WEISS, 5), run_time=self.rt(0.5, 19))
        # je mehr Strom, desto weniger an den Klemmen
        self.bis_wort(19, "mehr")
        fl2.tempo = 2.4
        self.play(ant.animate.set_value(0.5), run_time=self.rt(1.0, 19, wort="übrig"), rate_func=smooth)
        self.bis_wort(19, "weniger")
        wen = badge("weniger an den Klemmen", ORANGE, NAVY, 24).move_to([4.0, -1.3, 0])
        self.play(FadeIn(wen, shift=RIGHT * 0.1), run_time=self.rt(0.4, 20))
        schweben(wen, 0.02, 0.5)
        self.ende()


# --- Szene 4: Messgerät gegen Fernbedienung ------------------------------------------------------------
def weg_ueber_leitungen(e, l_rot, l_sw, mm, n=14):
    """Stromweg: Quelle -> Ri -> obere Klemme -> rote Messleitung -> Gerät -> schwarze Leitung -> untere Klemme."""
    P = e.P
    pts = [P(-1.6, 0.45), P(-1.6, 1.0), P(1.4, 1.0)]
    pts += [l_rot.point_from_proportion(1 - u) for u in np.linspace(0, 1, n)]
    pts += [mm.b_rot.get_center(), mm.b_sw.get_center()]
    pts += [l_sw.point_from_proportion(u) for u in np.linspace(0, 1, n)]
    pts += [P(1.4, -1.0), P(-1.6, -1.0), P(-1.6, -0.45)]
    return pts


class Szene04(WattScene):
    def construct(self):
        self.kapitel("Messgerät gegen Fernbedienung")
        e = esb([-2.2, 0.5, 0], 1.1, titel="Alkali-Zelle, neu")   # 20.11.: etwas tiefer, Titel im Gehäuse
        P = e.P
        self.bis_wort(0, "Batterie")
        self.play(FadeIn(e, shift=UP * 0.2), run_time=self.rt(0.7, 1))
        schweben(e, 0.02, 0.4)

        # neue Zelle: 1,5 V, 0,2 Ohm
        self.bis_wort(1, "einskommafünf")
        u0b = badge("1,5 V", CYAN, NAVY, 28).move_to(P(-0.2, -0.45))
        self.play(FadeIn(u0b, scale=1.2), run_time=self.rt(0.5, 1, wort="Innenwiderstand"))
        self.bis_wort(1, "nullkommazwei")
        rib = badge("0,2 Ω", GELB, NAVY, 28).move_to(P(1.0, 1.55))
        self.play(FadeIn(rib, scale=1.2), run_time=self.rt(0.5, 2))
        e.add(u0b, rib)

        # leer: 1,3 V, aber 3 Ohm
        self.bis_wort(2, "leer")
        leer = T("Alkali-Zelle, leer", 32, GRAU, BOLD).move_to(e.titel)
        self.play(Transform(e.titel, leer), e.gehaeuse.animate.set_stroke(ROHR_D), run_time=self.rt(0.5, 2, wort="einskommadrei"))
        self.bis_wort(2, "einskommadrei")
        u0n = badge("1,3 V", CYAN, NAVY, 28).move_to(u0b)
        self.play(Transform(u0b, u0n), run_time=self.rt(0.4, 2, wort="Innenwiderstand"))
        self.bis_wort(2, "steigt")
        gross = Rectangle(width=1.7, height=0.62, stroke_color=ROT_HELL, stroke_width=5, fill_color=NAVY, fill_opacity=1).move_to(e.ri)
        self.play(Transform(e.ri, gross), e.ri_label.animate.set_color(ROT_HELL), run_time=self.rt(0.6, 2, wort="drei"))
        self.bis_wort(2, "drei")
        rin = badge("3 Ω", ROT, WEISS, 28).move_to(rib)
        self.play(Transform(rib, rin), run_time=self.rt(0.4, 3))
        puls(rib, 0.04, 0.9)

        # Messgerät: 10 MOhm, fast kein Strom
        self.bis_wort(3, "Messgerät")
        u = ValueTracker(0.0)
        mm = multimeter([4.3, 0.7, 0], 1.05, wert=u.get_value)
        l_rot = leitung(mm.b_rot.get_center(), P(1.4, 1.0) + RIGHT * 0.05, ROT, 0.9)
        l_sw = leitung(mm.b_sw.get_center(), P(1.4, -1.0) + RIGHT * 0.05, GRAU, 0.5)
        self.play(FadeIn(mm, shift=LEFT * 0.3), run_time=self.rt(0.5, 3, wort="Eingangswiderstand"))
        self.play(Create(l_rot), Create(l_sw), run_time=self.rt(0.4, 3, wort="zehn"))
        self.bis_wort(3, "zehn")
        mo = badge("10 MΩ", CYAN, NAVY, 30).next_to(mm, UP, 0.3)
        self.play(FadeIn(mo, scale=1.2), run_time=self.rt(0.5, 3, wort="fast"))
        schweben(mo, 0.02, 0.5)
        self.bis_wort(3, "fast")
        fl = PfadFluss(weg_ueber_leitungen(e, l_rot, l_sw, mm), n=3, tempo=0.3, farbe=GELB, radius=0.045).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        self.play(an.animate.set_value(1.0), run_time=self.rt(0.4, 3, wort="weniger"))
        self.bis_wort(3, "weniger")
        ua = badge("< 1 µA", GELB, NAVY, 26).move_to([2.2, 2.5, 0])
        self.play(FadeIn(ua, shift=DOWN * 0.1), run_time=self.rt(0.4, 4))
        schweben(ua, 0.02, 0.5, 0.3)

        # an 3 Ohm faellt nichts ab, Anzeige 1,3 V
        self.bis_wort(4, "nichts")
        null = badge("0 V", CYAN, NAVY, 24).next_to(e.ri, DOWN, 0.1)
        self.play(FadeIn(null, scale=1.2), run_time=self.rt(0.4, 4, wort="volle"))
        self.bis_wort(4, "volle")
        self.play(u.animate.set_value(1.30), run_time=self.rt(1.0, 5, 0.3), rate_func=smooth)
        self.bis(5)
        self.play(mm.disp.animate.set_fill("#1E6B3A"), run_time=0.25)
        erg1 = ergebnis("1,3 V", 44).move_to([4.4, -1.55, 0])
        self.play(FadeIn(erg1, scale=1.2), run_time=self.rt(0.5, 6))
        puls(erg1, 0.03, 0.9)

        # Fernbedienung ist anders
        self.bis(6)
        alle_updater_weg(mo, ua, erg1)
        self.play(an.animate.set_value(0.0), FadeOut(mm), FadeOut(l_rot), FadeOut(l_sw), FadeOut(mo), FadeOut(ua),
                  FadeOut(erg1), FadeOut(null), run_time=self.rt(0.5, 6, 0.6))
        self.remove(fl)
        fb = fernbedienung(1.55).move_to([4.3, 0.7, 0])
        fb.ir.set_fill("#5A2430")
        f_rot = leitung(fb.fach.get_center() + RIGHT * 0.2, P(1.4, 1.0) + RIGHT * 0.05, ROT, 0.9)
        f_sw = leitung(fb.fach.get_center() + LEFT * 0.2, P(1.4, -1.0) + RIGHT * 0.05, GRAU, 0.5)
        self.play(FadeIn(fb, shift=LEFT * 0.3), Create(f_rot), Create(f_sw), run_time=self.rt(0.7, 7))
        schweben(fb, 0.02, 0.4)

        # Tastendruck: Impulse, 100 mA
        self.bis_wort(7, "Tastendruck")
        self.play(fb.taste.animate.scale(0.75), run_time=0.15)
        self.play(fb.taste.animate.scale(1 / 0.75), run_time=0.15)
        glow = Circle(0.3, stroke_width=0, fill_color=ROT, fill_opacity=0.0).move_to(fb.ir)
        self.add(glow)
        fb.ir.set_fill(ROT)
        flimmern(fb.ir, 0.2, 1.0, 6.0, stroke=False, fill=True)
        flimmern(glow, 0.0, 0.5, 6.0, stroke=False, fill=True)
        fl2 = PfadFluss(weg_ueber_leitungen(e, f_rot, f_sw, VGroup()) if False else
                        [P(-1.6, 0.45), P(-1.6, 1.0), P(1.4, 1.0)] + [f_rot.point_from_proportion(1 - v) for v in np.linspace(0, 1, 14)]
                        + [f_sw.point_from_proportion(v) for v in np.linspace(0, 1, 14)] + [P(1.4, -1.0), P(-1.6, -1.0), P(-1.6, -0.45)],
                        n=28, tempo=1.8, farbe=GELB, radius=0.06).set_z_index(3)
        an2 = ValueTracker(0.0)
        pulsend(fl2, an2, 6.0, 0.08)
        self.add(fl2)
        self.bis_wort(7, "Infrarot")
        ir = badge("Infrarot-Diode", ROT, WEISS, 24).next_to(fb, UP, 0.3)
        self.play(FadeIn(ir, shift=DOWN * 0.1), an2.animate.set_value(1.0), run_time=self.rt(0.5, 7, wort="Spitze"))
        schweben(ir, 0.02, 0.5)
        self.bis_wort(7, "hundert")
        ma = badge("100 mA", GELB, NAVY, 30).move_to([0.9, 2.5, 0])
        self.play(FadeIn(ma, scale=1.3), run_time=self.rt(0.5, 8))
        puls(ma, 0.05, 1.0)

        # 0,1 A * 3 Ohm = 0,3 V am Innenwiderstand
        self.bis(8)
        rechnung = MT('0,1 A · 3 Ω = <span foreground="#FF8A3D">0,3 V</span>', 30, WEISS, BOLD).move_to([-2.2, -2.15, 0])
        self.play(FadeIn(rechnung, shift=UP * 0.15), run_time=self.rt(0.7, 8, wort="nullkommadrei"))
        self.bis_wort(8, "nullkommadrei")
        verl = badge("0,3 V verloren", ORANGE, NAVY, 24).next_to(e.ri, DOWN, 0.1).shift(RIGHT * 0.5)   # 20.11.: Pluszeichen frei
        self.play(FadeIn(verl, scale=1.2), aufleuchten(e.ri, ORANGE, 9), run_time=self.rt(0.6, 9))
        puls(verl, 0.04, 1.0)
        # nur 1 V an den Klemmen
        self.bis_wort(9, "ein Volt")
        kl = badge("nur 1,0 V", GELB, NAVY, 28).move_to(P(2.7, -1.6))   # 20.11.: rechts neben dem Gehäuse unter der Leitung, frei von Titel und Rahmen
        self.play(FadeIn(kl, scale=1.3), aufleuchten(VGroup(e.k_o, e.k_u), GELB, 6), run_time=self.rt(0.5, 10))
        wackeln(kl, 0.04, 1.0)

        # zwei Zellen: 2,0 V statt 2,6 V, zu wenig
        self.bis_wort(10, "zwei Zellen")
        alle_updater_weg(rechnung)
        zwei = VGroup(batterie_aa(0.75), batterie_aa(0.75)).arrange(RIGHT, buff=0.1).move_to([-4.9, -2.75, 0])
        z_t = MT('2 · 1,0 V = <span foreground="#FFC400">2,0 V</span>', 30, WEISS, BOLD).next_to(zwei, RIGHT, 0.4)
        self.play(FadeOut(rechnung), FadeIn(zwei, shift=UP * 0.15), run_time=self.rt(0.5, 10, wort="zwei Volt"))
        self.bis_wort(10, "zwei Volt")
        self.play(FadeIn(z_t, shift=UP * 0.1), run_time=self.rt(0.4, 10, wort="zweikommasechs"))
        self.bis_wort(10, "zweikommasechs")
        statt = T("statt 2,6 V", 26, GRAU, BOLD).next_to(z_t, RIGHT, 0.4)
        self.play(FadeIn(statt), run_time=self.rt(0.4, 10, wort="Elektronik"))
        self.bis_wort(10, "Elektronik")
        ch = chip([4.4, -2.6, 0], 0.9)
        self.play(FadeIn(ch, scale=0.8), run_time=self.rt(0.4, 10, wort="wenig"))
        self.bis_wort(10, "wenig")
        zw = badge("zu wenig", ROT, WEISS, 28).next_to(ch, UP, 0.25)
        self.play(ch.k.animate.set_stroke(ROT).set_fill("#4A1C22"), FadeIn(zw, scale=1.3), run_time=self.rt(0.5, 11))
        wackeln(zw, 0.05, 1.0)

        # Fazit: Messgerät 1,3 V, Fernbedienung stumm
        self.bis(11)
        alle_updater_weg(zwei, zw)
        self.play(FadeOut(zwei), FadeOut(z_t), FadeOut(statt), FadeOut(ch), FadeOut(zw), run_time=self.rt(0.4, 11, 0.25))
        a = VGroup(multimeter(ORIGIN, 0.5), T("zeigt 1,3 V", 28, GRUEN, HEAVY)).arrange(RIGHT, buff=0.3).move_to([-3.2, -2.7, 0])
        self.play(FadeIn(a, shift=UP * 0.15), run_time=self.rt(0.5, 11, wort="Fernbedienung"))
        schweben(a, 0.02, 0.5)
        self.bis_wort(11, "stumm")
        st = badge("bleibt stumm", GRAU, WEISS, 30).move_to([4.4, -2.6, 0])
        self.play(FadeIn(st, scale=1.2), an2.animate.set_value(0.0), run_time=self.rt(0.5, 12))
        fb.ir.clear_updaters()
        glow.clear_updaters()
        self.play(fb.ir.animate.set_fill("#5A2430", 1), glow.animate.set_fill(opacity=0), run_time=0.3)
        wackeln(st, 0.04, 0.9)
        self.ende()


# --- Szene 5: Auto beim Starten, Ri selbst bestimmen -------------------------------------------------------
class Szene05(WattScene):
    def construct(self):
        self.kapitel("Auto beim Starten")
        auto = auto_front([-3.4, -1.15, 0], 1.25)   # 20.11.: ganze Gruppe 0,25 tiefer, Chip «Leerlauf» frei vom Kapiteltitel
        ub = ValueTracker(12.6)
        bat = autobatterie([-5.1, 1.55, 0], 0.5)
        anz = Zaehler(ub.get_value, lambda v: de(v, 1) + " V", 24, CYAN, HEAVY, ort=bat[0].get_center() + DOWN * 0.08)
        anl = VGroup(Circle(0.42, stroke_color=WEISS, stroke_width=4, fill_color=NAVY2, fill_opacity=1),
                     T("M", 30, WEISS, HEAVY)).move_to([-1.3, 1.55, 0])
        anl_t = T("Anlasser", 22, GRAU, BOLD).next_to(anl, DOWN, 0.12)
        draht = Line(bat[0].get_right(), anl.get_left(), stroke_color=WEISS, stroke_width=4)
        self.bis_wort(0, "Auto")
        self.play(FadeIn(auto, shift=UP * 0.2), run_time=self.rt(0.7, 1))
        schweben(auto, 0.02, 0.35)
        self.bis_wort(1, "Batterie")
        self.play(FadeIn(bat), FadeIn(anz), Create(draht), FadeIn(anl), FadeIn(anl_t), run_time=self.rt(0.6, 1, wort="rund"))
        self.bis_wort(1, "zwölfkommasechs")
        ll = badge("Leerlauf: 12,6 V", CYAN, NAVY, 24).next_to(bat, UP, 0.12)
        self.play(FadeIn(ll, shift=UP * 0.1), run_time=self.rt(0.5, 2))
        schweben(ll, 0.02, 0.5)

        # Schluessel: 150 A
        self.bis_wort(2, "Schlüssel")
        key = schluessel([0.3, 1.55, 0], 0.55)
        self.play(FadeIn(key, scale=0.7), run_time=0.3)
        self.play(Rotate(key, -PI / 3), run_time=self.rt(0.4, 2, wort="zieht"))
        self.bis_wort(2, "zieht")
        fl = PfadFluss([bat[0].get_right(), anl.get_left()], n=16, tempo=1.6, farbe=GELB, radius=0.075).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        self.play(an.animate.set_value(1.0), auto.hell.animate.set_value(0.88), Rotate(anl[1], TAU, about_point=anl[0].get_center()),
                  run_time=self.rt(0.6, 2, wort="hundertfünfzig"))
        self.bis_wort(2, "hundertfünfzig")
        ia = badge("150 A", GELB, NAVY, 30).next_to(draht, UP, 0.2).shift(RIGHT * 0.5)
        self.play(FadeIn(ia, scale=1.3), run_time=self.rt(0.5, 3))
        puls(ia, 0.05, 1.0)

        # gesunde Batterie: 5 mOhm -> 0,75 V -> knapp 12 V
        x = 4.1
        self.bis_wort(3, "gesunde")
        r1 = badge("gesund: Rᵢ = 5 mΩ", GRUEN, NAVY, 28).move_to([x, 2.5, 0])
        self.play(FadeIn(r1, shift=LEFT * 0.2), run_time=self.rt(0.6, 4))
        schweben(r1, 0.02, 0.5)
        self.bis(4)
        c1 = MT('150 A · 0,005 Ω = <span foreground="#FF8A3D">0,75 V</span>', 30, WEISS, BOLD).move_to([x, 1.6, 0])
        self.play(FadeIn(c1, shift=UP * 0.15), run_time=self.rt(0.7, 4, wort="nullkommasieben"))
        self.bis(5)
        e1 = MT('12,6 V − 0,75 V ≈ <span foreground="#22D3EE">11,85 V</span>', 30, WEISS, BOLD).move_to([x, 0.8, 0])
        self.play(FadeIn(e1, shift=UP * 0.15), ub.animate.set_value(11.85), run_time=self.rt(0.7, 5, wort="kaum"))
        self.bis_wort(5, "kaum")
        kaum = badge("merkst du kaum", GRUEN, NAVY, 24).move_to([-3.4, -3.3, 0])
        self.play(FadeIn(kaum, shift=UP * 0.1), run_time=self.rt(0.4, 6))
        schweben(kaum, 0.02, 0.5)

        # alte oder kalte Batterie: 20 mOhm -> 3 V -> 9,6 V, Scheinwerfer dunkler
        self.bis_wort(6, "alt")
        r2 = badge("alt oder kalt: Rᵢ = 20 mΩ", ROT, WEISS, 28).move_to([x, -0.4, 0])
        self.play(bat[0].animate.set_fill("#2E3A5A"), FadeIn(r2, shift=LEFT * 0.2), ub.animate.set_value(12.6),
                  FadeOut(kaum), run_time=self.rt(0.6, 6, wort="zwanzig"))
        schweben(r2, 0.02, 0.5, 0.3)
        self.bis(7)
        c2 = MT('150 A · 0,02 Ω = <span foreground="#F2545B">3 V</span>', 30, WEISS, BOLD).move_to([x, -1.3, 0])
        self.play(FadeIn(c2, shift=UP * 0.15), run_time=self.rt(0.7, 7, wort="drei"))
        self.bis(8)
        e2 = MT('12,6 V − 3 V = <span foreground="#F2545B">9,6 V</span>', 30, WEISS, BOLD).move_to([x, -2.1, 0])
        self.play(FadeIn(e2, shift=UP * 0.15), ub.animate.set_value(9.6), run_time=self.rt(0.7, 8, wort="Scheinwerfer"))
        self.bis_wort(8, "Scheinwerfer")
        self.play(auto.hell.animate.set_value(0.3), run_time=self.rt(0.5, 8, wort="dunkler"), rate_func=smooth)
        self.bis_wort(8, "dunkler")
        dk = badge("sichtbar dunkler", ROT, WEISS, 26).move_to([-3.4, -3.0, 0])
        self.play(FadeIn(dk, shift=UP * 0.1), run_time=self.rt(0.4, 9))
        wackeln(dk, 0.04, 0.9)

        # Werkstatt prueft unter Last
        self.bis(9)
        alle_updater_weg(r1, r2, dk, ia)
        self.play(FadeOut(VGroup(r1, c1, e1, r2, c2, e2)), FadeOut(dk), FadeOut(ia), an.animate.set_value(0.0),
                  auto.hell.animate.set_value(1.0), ub.animate.set_value(12.6), run_time=self.rt(0.6, 9, wort="nie"))
        self.remove(fl)
        self.bis_wort(9, "nie")
        vm = VGroup(multimeter(ORIGIN, 0.6), T("nur Voltmeter", 26, GRAU, BOLD)).arrange(RIGHT, buff=0.3).move_to([x, 1.9, 0])
        kz = kreuz(vm[0].get_center(), 0.5, ROT_HELL, 8)
        self.play(FadeIn(vm), run_time=self.rt(0.4, 9, wort="sondern"))
        self.play(Create(kz), run_time=0.3)
        self.bis_wort(9, "Last")
        ul = ergebnis("unter Last prüfen", 36).move_to([x, 0.6, 0])
        self.play(FadeIn(ul, scale=1.15), run_time=self.rt(0.5, 10))
        puls(ul, 0.03, 0.9)

        # Ri selbst bestimmen: drei Schritte
        self.bis(10)
        alle_updater_weg(ul)
        self.play(FadeOut(vm), FadeOut(kz), FadeOut(ul), run_time=self.rt(0.4, 10, 0.4))
        kopf = badge("Rᵢ selbst bestimmen", GELB, NAVY, 30).move_to([3.6, 2.7, 0])
        self.play(FadeIn(kopf, shift=DOWN * 0.1), run_time=self.rt(0.5, 11))
        schweben(kopf, 0.02, 0.5)
        self.bis(11)
        s1 = MT('<span foreground="#FFC400">1</span>  Leerlaufspannung U₀ messen', 23, WEISS, BOLD).move_to([3.6, 1.75, 0])
        self.play(FadeIn(s1, shift=RIGHT * 0.2), aufleuchten(bat[0], CYAN, 7), run_time=self.rt(0.6, 12))
        self.bis(12)
        s2 = VGroup(MT('<span foreground="#FFC400">2</span>  bekannter Strom I fließt:', 23, WEISS, BOLD),
                    T("Klemmenspannung Uₖ messen", 23, WEISS, BOLD)).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([3.6, 0.6, 0])
        fl2 = PfadFluss([bat[0].get_right(), anl.get_left()], n=16, tempo=1.6, farbe=GELB, radius=0.075).set_z_index(3)
        an2 = einschalten(fl2)
        self.add(fl2)
        self.play(FadeIn(s2, shift=RIGHT * 0.2), an2.animate.set_value(1.0), auto.hell.animate.set_value(0.85),
                  ub.animate.set_value(11.85), run_time=self.rt(0.7, 13))
        self.bis(13)
        s3 = ergebnis("Rᵢ = (U₀ − Uₖ) / I", 38).move_to([x, -0.9, 0])
        self.play(FadeIn(s3, scale=1.15), run_time=self.rt(0.7, 13, wort="geteilt"))
        schweben(s3, 0.025, 0.45)
        self.bis_wort(13, "Innenwiderstand")
        bsp = T("z. B. (12,6 V − 11,85 V) / 150 A = 0,005 Ω", 20, GRAU, BOLD).move_to([3.6, -1.9, 0])
        self.play(FadeIn(bsp, shift=UP * 0.1), run_time=self.rt(0.5, 14))
        self.ende()


# --- Szene 6: Kurzschlussstrom, Leistungsanpassung ------------------------------------------------------------
class Szene06(WattScene):
    def construct(self):
        self.kapitel("Kurzschluss")
        e = esb([-3.4, 1.5, 0], 0.95, gehaeuse=False)
        self.play(FadeIn(e, shift=UP * 0.2), run_time=self.rt(0.7, 0, 0.5))
        schweben(e, 0.02, 0.4)
        # Kurzschluss: Plus und Minus direkt verbunden (Ivan 23.11., anfaengerfreundlich)
        self.bis_wort(0, "Draht")
        ks = kurzschluss(e, 2.1)
        fl = PfadFluss(e.weg(2.1), n=40, tempo=2.6, farbe=GELB, radius=0.06).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        self.play(Create(ks), an.animate.set_value(1.0), run_time=self.rt(0.6, 0, wort="ohne"))
        self.bis(1)
        kz = badge("Plus und Minus direkt verbunden", ROT, WEISS, 24).move_to([-3.2, -0.95, 0])   # 23.11.: Abstand zu «nur noch Rᵢ bremst»
        self.play(FadeIn(kz, scale=1.2), run_time=self.rt(0.5, 2))
        wackeln(kz, 0.04, 1.0)
        self.bis_wort(2, "außer")
        nr = badge("nur noch Rᵢ bremst", GELB, NAVY, 24).move_to([-3.4, -0.1, 0])
        self.play(FadeIn(nr, scale=1.2), aufleuchten(e.ri, GELB, 9), run_time=self.rt(0.6, 3))
        schweben(nr, 0.02, 0.5)
        self.bis_wort(3, "höchstens")
        self.play(aufleuchten(e.ri, GELB, 9), run_time=self.rt(0.6, 4))
        self.bis_wort(4, "Kurzschlussstrom")
        ikc = badge("Iₖ = größter Strom der Quelle", CYAN, NAVY, 24).move_to([3.3, 2.6, 0])
        self.play(FadeIn(ikc, scale=1.2), run_time=self.rt(0.5, 5))
        schweben(ikc, 0.02, 0.5)
        self.bis(5)
        x = 3.3
        form = ergebnis("Iₖ = U₀ / Rᵢ", 42).move_to([x, 2.6, 0])
        alle_updater_weg(ikc)
        self.play(ReplacementTransform(ikc, form), run_time=self.rt(0.7, 5, 0.6))
        schweben(form, 0.025, 0.45)

        # neue Zelle: 7,5 A, wird heiss
        self.bis(6)
        zt = T("neue Zelle", 24, GRAU, BOLD).move_to([x, 1.75, 0])
        self.play(FadeIn(zt), run_time=self.rt(0.4, 7))
        self.bis(7)
        c1 = MT('1,5 V / 0,2 Ω = <span foreground="#FFC400">7,5 A</span>', 30, WEISS, BOLD).move_to([x, 1.2, 0])
        self.play(FadeIn(c1, shift=UP * 0.15), run_time=self.rt(0.7, 7, wort="siebeneinhalb"))
        self.bis_wort(7, "Zelle")
        z = batterie_aa(1.0).move_to([x - 1.9, 0.3, 0])
        hz = ValueTracker(0.0)
        z[0].add_updater(lambda m: m.set_fill(interpolate_color(ManimColor("#2A3B4D"), ManimColor("#FF5A36"), hz.get_value()), 1))
        ww = waerme_wellen(z.get_top() + DOWN * 0.05, hz, 0.8, 0.7)
        self.play(FadeIn(z, shift=UP * 0.15), run_time=self.rt(0.4, 7, wort="heiß"))
        self.add(ww)
        self.play(hz.animate.set_value(1.0), run_time=self.rt(0.8, 7, wort="heiß"))
        self.bis_wort(7, "heiß")
        hb = badge("nach einer Minute heiß", ROT, WEISS, 26).next_to(z, RIGHT, 0.3)
        self.play(FadeIn(hb, scale=1.2), run_time=self.rt(0.4, 8))
        wackeln(hb, 0.04, 1.0)

        # Autobatterie: ueber 2000 A, Schraubenschluessel glueht
        self.bis(8)
        at = T("Autobatterie", 24, GRAU, BOLD).move_to([x, -0.6, 0])
        self.play(FadeIn(at), run_time=self.rt(0.4, 9))
        self.bis(9)
        c2 = MT('12,6 V / 0,005 Ω = <span foreground="#F2545B">über 2000 A</span>', 30, WEISS, BOLD).move_to([x, -1.15, 0])
        self.play(FadeIn(c2, shift=UP * 0.15), run_time=self.rt(0.8, 9, wort="zweitausend"))
        self.bis_wort(9, "zweitausend")
        self.play(aufleuchten(c2, ROT, 3), run_time=self.rt(0.5, 10))
        self.bis_wort(10, "kleiner")
        kl = badge("kleiner Rᵢ → riesiger Iₖ", GELB, NAVY, 24).move_to([x, -1.75, 0])
        self.play(FadeIn(kl, shift=UP * 0.1), run_time=self.rt(0.5, 11))
        schweben(kl, 0.02, 0.5)
        self.bis(11)
        alle_updater_weg(nr, kz, kl)
        self.play(an.animate.set_value(0.0), FadeOut(ks), FadeOut(nr), FadeOut(kz), FadeOut(kl), run_time=self.rt(0.4, 11, 0.1))
        self.remove(fl)
        ab = autobatterie([-3.4, -2.2, 0], 0.8)
        self.play(FadeIn(ab, shift=UP * 0.2), run_time=self.rt(0.4, 11, wort="Schraubenschlüssel"))
        self.bis_wort(11, "Schraubenschlüssel")
        sk = schraubenschluessel([-3.4, -1.62, 0], 0.6)
        hk = ValueTracker(0.0)
        for m in sk.metall:
            m.add_updater(lambda mm, h=hk: mm.set_fill(heiss_farbe(h.get_value()), 1))
        self.play(FadeIn(sk, shift=DOWN * 0.4), run_time=self.rt(0.4, 11, wort="glüht"))
        self.bis_wort(11, "glüht")
        fk = PfadFluss([ab.pol_plus.get_center(), ab.pol_minus.get_center()], n=14, tempo=3.0, farbe=GELB, radius=0.06).set_z_index(3)
        self.add(fk)
        ww2 = waerme_wellen([-3.4, -1.45, 0], hk, 1.2, 0.7, 4)
        self.add(ww2)
        self.play(hk.animate.set_value(1.0), Flash(sk.get_center(), color=GELB, line_length=0.35, flash_radius=1.0, num_lines=14),
                  self.kamera_wackeln(0.04, 0.4), run_time=self.rt(0.6, 11, wort="deshalb"))
        ws = warnschild([-1.3, -1.9, 0], 0.9)
        self.play(FadeIn(ws, scale=1.3), run_time=0.3)
        wackeln(ws, 0.08, 1.2)
        self.bis_wort(11, "Minuspol")
        mp = badge("beim Abklemmen: Minuspol zuerst", GELB, NAVY, 24).move_to([x, -2.3, 0])
        self.play(FadeIn(mp, shift=UP * 0.1), aufleuchten(ab.pol_minus, CYAN, 8), run_time=self.rt(0.5, 12))
        schweben(mp, 0.02, 0.5)
        puls(ab.pol_minus, 0.08, 1.0)

        # Leistungsanpassung
        self.bis(12)
        alles = Group(*[m for m in self.mobjects if m is not self.hg and not getattr(m, "_hud_w", None)
                        and not isinstance(m, ValueTracker)])
        for mm in alles.get_family():
            mm.clear_updaters()
        self.play(FadeOut(alles, shift=UP * 0.3), run_time=self.rt(0.5, 12, 0.6))
        self.aufraeumen(*hud_teile(self))
        dran = badge("Sonderfall: Leistungsanpassung", GELB, NAVY, 30).move_to([0.9, 3.0, 0])   # 23.11. Ivan: «drankommt» raus
        self.play(FadeIn(dran, scale=1.2), run_time=self.rt(0.5, 13))
        wackeln(dran, 0.03, 0.9)

        self.bis(13)
        e2 = esb([-3.6, 0.8, 0], 0.95, gehaeuse=False)
        la = last(e2, 3.0, "Rₐ")
        fl2 = PfadFluss(e2.weg(3.0), n=24, tempo=1.0, farbe=GELB, radius=0.055).set_z_index(3)
        an2 = einschalten(fl2)
        self.add(fl2)
        self.play(FadeIn(e2), FadeIn(la), an2.animate.set_value(1.0), run_time=self.rt(0.7, 13, wort="genauso"))
        self.bis_wort(13, "genauso")
        gl = badge("Rₐ = Rᵢ", CYAN, NAVY, 28).next_to(la.r, DOWN, 0.8)   # 20.11.: unter der Leitung, nicht auf der Ecke
        self.play(FadeIn(gl, scale=1.2), aufleuchten(VGroup(e2.ri, la.r), CYAN, 8), run_time=self.rt(0.5, 13, wort="teilt"))
        schweben(gl, 0.02, 0.5)
        self.bis_wort(13, "teilt")
        a_ri, a_ra, a_p = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        b1 = u_balken([3.1, -1.9, 0], 2.4, a_ri, ORANGE, 0.55, "an Rᵢ")
        b2 = u_balken([4.3, -1.9, 0], 2.4, a_ra, CYAN, 0.55, "an Rₐ")
        u0l = DashedLine([2.7, 0.5, 0], [4.7, 0.5, 0], stroke_color=WEISS, stroke_width=3)
        u0t = T("U₀", 24, WEISS, BOLD).next_to(u0l, RIGHT, 0.1)
        self.play(FadeIn(b1), FadeIn(b2), FadeIn(u0l), FadeIn(u0t), run_time=0.4)
        self.play(a_ri.animate.set_value(0.5), a_ra.animate.set_value(0.5), run_time=self.rt(0.8, 13, wort="halb"), rate_func=smooth)
        self.bis_wort(13, "halb")
        h1 = T("U₀/2", 24, ORANGE, HEAVY).move_to([3.1, -0.4, 0])
        h2 = T("U₀/2", 24, CYAN, HEAVY).move_to([4.3, -0.4, 0])
        self.play(FadeIn(h1), FadeIn(h2), run_time=self.rt(0.4, 14))
        # groesste Leistung
        self.bis_wort(14, "größte")
        b3 = u_balken([5.9, -1.9, 0], 2.4, a_p, GRUEN, 0.55, "P an Rₐ")
        self.play(FadeIn(b3), a_p.animate.set_value(1.0), run_time=self.rt(0.8, 14, wort="Leistungsanpassung"))
        self.bis_wort(14, "Leistungsanpassung")
        lp = badge("Leistungsanpassung: P max", GRUEN, NAVY, 26).move_to([3.9, 1.9, 0])
        self.play(FadeIn(lp, shift=DOWN * 0.1), run_time=self.rt(0.5, 15))
        schweben(lp, 0.02, 0.5)
        # andere Haelfte heizt Ri
        self.bis_wort(15, "heizt")
        hz2 = ValueTracker(0.0)
        e2.ri.add_updater(lambda m: m.set_fill(interpolate_color(ManimColor(NAVY), ManimColor(ORANGE), hz2.get_value()), 1))
        ww3 = waerme_wellen(e2.ri.get_top() + DOWN * 0.05, hz2, 0.7, 0.6)
        self.add(ww3)
        self.play(hz2.animate.set_value(1.0), run_time=self.rt(0.6, 15, wort="Wirkungsgrad"))
        self.bis_wort(15, "fünfzig")
        eta = badge("η = 50 %", ROT, WEISS, 28).move_to([3.9, 1.1, 0])
        self.play(FadeIn(eta, scale=1.2), run_time=self.rt(0.5, 16))
        wackeln(eta, 0.04, 1.0)
        # Ri viel kleiner als Last: Spannung stabil
        self.bis_wort(16, "viel kleiner")
        alle_updater_weg(gl, lp, eta)
        e2.ri.clear_updaters()
        klein = Rectangle(width=0.5 * 0.95, height=0.3 * 0.95, stroke_color=WEISS, stroke_width=4, fill_color=NAVY,
                          fill_opacity=1).move_to(e2.ri)
        gross = Rectangle(width=0.6 * 0.95, height=1.6 * 0.95, stroke_color=WEISS, stroke_width=4, fill_color=NAVY,
                          fill_opacity=1).move_to(la.r)
        kl = badge("Rᵢ ≪ Rₐ", CYAN, NAVY, 28).move_to(gl)
        for w in ww3:
            w.clear_updaters()
        self.play(Transform(e2.ri, klein), Transform(la.r, gross), ReplacementTransform(gl, kl), FadeOut(ww3),
                  FadeOut(lp), FadeOut(eta), FadeOut(h1), FadeOut(h2), a_ri.animate.set_value(0.08),
                  a_ra.animate.set_value(0.92), a_p.animate.set_value(0.35), run_time=self.rt(1.0, 16, wort="stabil"), rate_func=smooth)
        schweben(kl, 0.02, 0.5)
        self.bis_wort(16, "stabil")
        st = ergebnis("Spannung bleibt stabil", 34).move_to([3.9, 1.5, 0])
        self.play(FadeIn(st, scale=1.15), run_time=self.rt(0.5, 17))
        puls(st, 0.03, 0.9)
        self.ende()


# --- Szene 7: Pruefungsaufgabe ---------------------------------------------------------------------------------
class Szene07(WattScene):
    def construct(self):
        jetzt = badge("Jetzt du!", GELB, NAVY, 40).move_to([4.9, 3.35, 0])
        self.kapitel("Prüfungsaufgabe", FadeIn(jetzt, scale=1.5), run_time=self.rt(0.5, 1))
        wackeln(jetzt, 0.05, 1.2)

        e = esb([-3.8, 0.9, 0], 1.0, gehaeuse=False)   # 20.11.: tiefer, Rᵢ frei vom Kapiteltitel
        P = e.P
        self.bis_wort(1, "Akku")
        self.play(FadeIn(e, shift=UP * 0.2), run_time=self.rt(0.6, 1, wort="zwölf"))
        schweben(e, 0.02, 0.4)
        self.bis_wort(1, "zwölf")
        u0b = badge("U₀ = 12 V", CYAN, NAVY, 28).move_to(P(-1.2, -1.55))  # unter die Masche, verdeckte sonst Quelle und 1-V-Badge
        self.play(FadeIn(u0b, scale=1.2), run_time=self.rt(0.5, 1, wort="Innenwiderstand"))
        self.bis_wort(1, "nullkommafünf")
        rib = badge("Rᵢ = 0,5 Ω", GELB, NAVY, 28).move_to(P(1.6, 1.55))
        self.play(FadeIn(rib, scale=1.2), run_time=self.rt(0.5, 2))
        e.add(u0b, rib)
        self.bis_wort(2, "Verbraucher")
        la = last(e, 3.0, "")
        rab = badge("Rₐ = 5,5 Ω", WEISS, NAVY, 28).next_to(la.r, DOWN, 0.8)
        self.play(FadeIn(la), run_time=self.rt(0.5, 2, wort="fünfkommafünf"))
        self.bis_wort(2, "fünfkommafünf")
        self.play(FadeIn(rab, scale=1.2), run_time=self.rt(0.5, 3))
        schweben(rab, 0.02, 0.5)

        # Fragen
        self.bis(3)
        fr = VGroup(T("I = ?", 32, GELB, BOLD), T("Uₖ = ?", 32, CYAN, BOLD), T("Iₖ = ?", 32, ROT_HELL, BOLD)
                    ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fk = karte(fr, CYAN, 0.3).move_to([3.8, 1.5, 0])
        self.play(FadeIn(fk, shift=LEFT * 0.3), run_time=self.rt(0.8, 3, 0.5))
        schweben(fk, 0.02, 0.5)

        # Denkpause
        self.bis(4)
        countdown(self, [3.8, -1.3, 0], self.t_satz(5))

        # Loesung
        self.bis(5)
        alle_updater_weg(fk)
        self.play(FadeOut(fk, shift=UP * 0.2), run_time=self.rt(0.4, 5, 0.3))
        x = 3.9
        l1 = MT('R<sub>ges</sub> = 0,5 Ω + 5,5 Ω = <span foreground="#F5F7FA">6 Ω</span>', 30, GRAU, BOLD).move_to([x, 2.5, 0])
        self.bis_wort(5, "Reihe")
        self.play(FadeIn(l1, shift=UP * 0.15), aufleuchten(VGroup(e.ri, la.r), WEISS, 8), run_time=self.rt(0.7, 6))
        self.bis(6)
        l2 = MT('I = 12 V / 6 Ω = <span foreground="#FFC400">2 A</span>', 30, WEISS, BOLD).move_to([x, 1.7, 0])
        self.play(FadeIn(l2, shift=UP * 0.15), run_time=self.rt(0.7, 6, wort="zwei"))
        self.bis_wort(6, "zwei")
        fl = PfadFluss(e.weg(3.0), n=24, tempo=1.0, farbe=GELB, radius=0.055).set_z_index(3)
        an = einschalten(fl)
        self.add(fl)
        ib = badge("2 A", GELB, NAVY, 28).move_to(P(0.9, -1.55))
        self.play(an.animate.set_value(1.0), FadeIn(ib, scale=1.3), run_time=self.rt(0.5, 7))
        puls(ib, 0.04, 0.9)
        self.bis(7)
        l3 = MT('U<sub>Ri</sub> = 2 A · 0,5 Ω = <span foreground="#FF8A3D">1 V</span>', 30, WEISS, BOLD).move_to([x, 0.9, 0])
        self.play(FadeIn(l3, shift=UP * 0.15), aufleuchten(e.ri, ORANGE, 9), run_time=self.rt(0.7, 7, wort="ein Volt"))
        self.bis_wort(7, "ein Volt")
        vb = badge("1 V", ORANGE, NAVY, 24).next_to(e.ri, DOWN, 0.1)
        self.play(FadeIn(vb, scale=1.2), run_time=self.rt(0.4, 8))
        self.bis(8)
        l4 = MT('U<sub>K</sub> = 12 V − 1 V = <span foreground="#22D3EE">11 V</span>', 30, WEISS, BOLD).move_to([x, 0.1, 0])
        self.play(FadeIn(l4, shift=UP * 0.15), run_time=self.rt(0.7, 8, wort="elf"))
        self.bis_wort(8, "elf")
        kb = badge("11 V", CYAN, NAVY, 26).move_to(P(2.2, 0.0))
        self.play(FadeIn(kb, scale=1.2), aufleuchten(VGroup(e.k_o, e.k_u), CYAN, 6), run_time=self.rt(0.4, 9))
        self.bis(9)
        l5 = MT('Kontrolle: 2 A · 5,5 Ω = <span foreground="#22D3EE">11 V</span>', 28, GRAU, BOLD).move_to([x, -0.7, 0])
        self.play(FadeIn(l5, shift=UP * 0.15), run_time=self.rt(0.6, 10, wort="ebenfalls"))
        self.bis_wort(10, "passt")
        hk = haken(l5.get_right() + RIGHT * 0.45, 0.4, GRUEN, 7)
        self.play(Create(hk), run_time=self.rt(0.4, 11))
        self.bis(11)
        l6 = MT('I<sub>K</sub> = 12 V / 0,5 Ω', 30, WEISS, BOLD).move_to([x, -1.6, 0])
        self.play(FadeIn(l6, shift=UP * 0.15), run_time=self.rt(0.7, 11, wort="vierundzwanzig"))
        self.bis_wort(11, "vierundzwanzig")
        erg = ergebnis("Iₖ = 24 A", 40).move_to([x, -2.6, 0])
        self.play(FadeIn(erg, scale=1.2), run_time=self.rt(0.5, 12))
        puls(erg, 0.03, 0.9)
        self.ende()


# --- Szene 8: typischer Fehler, Aufloesung, Zusammenfassung, Abspann ---------------------------------------------
class Szene08(WattScene):
    def construct(self):
        kopf = VGroup(warnschild(ORIGIN, 0.8), T("Typischer Fehler", 40, ROT, BOLD)).arrange(RIGHT, buff=0.3
                                                                                              ).move_to([0, 3.0, 0])
        self.play(FadeIn(kopf, shift=DOWN * 0.3), run_time=self.rt(0.6, 1))
        wackeln(kopf[0], 0.1, 1.4)
        self.bis(1)
        verg = MT('den <span foreground="#F2545B">Innenwiderstand vergessen</span>', 40, WEISS, BOLD).move_to([0, 2.0, 0])
        self.play(FadeIn(verg, shift=UP * 0.2), run_time=self.rt(0.6, 2))

        e = esb([-3.8, -0.4, 0], 0.9, gehaeuse=False)
        P = e.P
        la = last(e, 3.0, "")
        la.add(badge("5,5 Ω", WEISS, NAVY, 22).next_to(la.r, RIGHT, 0.2))
        rib = badge("0,5 Ω", GELB, NAVY, 24).move_to(P(1.1, 1.55))
        self.bis_wort(2, "rechnen")
        self.play(FadeIn(e), FadeIn(la), FadeIn(rib), run_time=self.rt(0.6, 2, wort="zwölf"))
        schweben(VGroup(e, la, rib), 0.05, 0.4)  # 4.11.: Standbild 3,7 s im Final-Check, mehr Bewegung
        self.bis_wort(2, "zwölf")
        falsch = MT('12 V / 5,5 Ω = 2,18 A', 38, WEISS, BOLD).move_to([3.3, 0.5, 0])
        self.play(FadeIn(falsch, shift=UP * 0.2), run_time=self.rt(0.7, 2, wort="zweikomma"))
        schweben(falsch, 0.04, 0.6, phase=0.3)
        self.bis_wort(2, "zweikomma")
        kz = kreuz(falsch.get_right() + RIGHT * 0.5, 0.28)
        schweben(kz, 0.04, 0.6, phase=0.3)
        self.play(Create(kz), falsch.animate.set_opacity(0.5), aufleuchten(e.ri, ROT, 9), run_time=self.rt(0.5, 3))
        wackeln(kz, 0.06, 1.0)
        self.bis_wort(3, "beide")
        self.play(aufleuchten(VGroup(e.ri, la.r), GELB, 9), run_time=self.rt(0.6, 3, wort="sechs"))
        self.bis_wort(3, "sechs")
        richtig = MT('12 V / <span foreground="#FFC400">6 Ω</span> = 2 A', 42, WEISS, BOLD).move_to([3.3, -0.7, 0])
        self.play(FadeIn(richtig, shift=UP * 0.2), run_time=self.rt(0.6, 3, wort="zwei"))
        self.bis_wort(3, "zwei")
        wert = ergebnis("2 A", 40).next_to(richtig, DOWN, 0.35)
        self.play(FadeIn(wert, scale=1.2), run_time=self.rt(0.5, 4))
        schweben(VGroup(richtig, wert), 0.02, 0.5)

        # Aufloesung
        self.bis(4)
        alt = Group(*[m for m in self.mobjects if m is not self.hg and not getattr(m, "_hud_w", None)
                      and not isinstance(m, ValueTracker)])
        for mm in alt.get_family():
            mm.clear_updaters()
        self.play(FadeOut(alt, shift=UP * 0.4), run_time=self.rt(0.6, 4, 0.6))
        self.aufraeumen(*hud_teile(self))
        frage = karte(T("Wer lügt: Messgerät oder Fernbedienung?", 36, WEISS, BOLD), GELB, 0.22).move_to([-0.4, 3.0, 0])
        fz = badge("?", GELB, NAVY, 44).next_to(frage, RIGHT, 0.3)
        self.bis(5)
        self.play(FadeIn(frage, shift=DOWN * 0.3), FadeIn(fz, scale=1.4), run_time=self.rt(0.6, 5, 0.4))
        wackeln(fz, 0.06, 1.1)

        # links Messgeraet, rechts Fernbedienung, je mit Zelle
        u = ValueTracker(1.3)
        mm = multimeter([-4.6, 0.9, 0], 0.85, wert=u.get_value)
        mm.disp.set_fill("#1E6B3A")
        zl = batterie_aa(1.0).move_to([-4.6, -1.0, 0])
        ml = VGroup(leitung(mm.b_rot.get_center(), zl.pol_plus() + RIGHT * 0.05, ROT, 0.3),
                    leitung(mm.b_sw.get_center(), zl.pol_minus() + LEFT * 0.05, GRAU, 0.3))
        fb = fernbedienung(1.2).move_to([4.6, 1.0, 0])
        zr = batterie_aa(1.0).move_to([4.6, -1.0, 0])
        mr = VGroup(leitung(fb.fach.get_center() + RIGHT * 0.15, zr.pol_plus() + RIGHT * 0.05, ROT, 0.3),
                    leitung(fb.fach.get_center() + LEFT * 0.15, zr.pol_minus() + LEFT * 0.05, GRAU, 0.3))
        self.bis_wort(5, "Messgerät")
        self.play(FadeIn(mm), FadeIn(zl), Create(ml), run_time=self.rt(0.5, 5, wort="Fernbedienung"))
        self.bis_wort(5, "Fernbedienung")
        self.play(FadeIn(fb), FadeIn(zr), Create(mr), run_time=self.rt(0.5, 6))
        schweben(VGroup(mm, zl, ml), 0.025, 0.45)
        schweben(VGroup(fb, zr, mr), 0.025, 0.45, 0.4)
        self.bis(6)
        keiner = ergebnis("Keiner von beiden!", 44).move_to([0, 0.9, 0])
        self.play(FadeIn(keiner, scale=1.2), run_time=self.rt(0.6, 7))
        puls(keiner, 0.03, 0.9)
        # Messgeraet: kein Strom, sieht U0
        self.bis_wort(7, "fast keinen")
        t1 = VGroup(T("fast kein Strom", 24, CYAN, BOLD), T("sieht U₀ = 1,3 V", 24, CYAN, BOLD)).arrange(DOWN, buff=0.1
                                                                                                        ).move_to([-4.6, -2.3, 0])
        self.play(FadeIn(t1[0], shift=UP * 0.1), run_time=self.rt(0.4, 7, wort="Leerlaufspannung"))
        self.bis_wort(7, "Leerlaufspannung")
        self.play(FadeIn(t1[1], shift=UP * 0.1), run_time=self.rt(0.4, 8))
        schweben(t1, 0.02, 0.5)
        # Fernbedienung: Strom, Spannung bricht ein
        self.bis_wort(8, "braucht Strom")
        fl = PfadFluss([fb.fach.get_center() + RIGHT * 0.15] + [mr[0].point_from_proportion(v) for v in np.linspace(0, 1, 10)]
                       + [zr.pol_plus(), zr.get_center(), zr.pol_minus()]
                       + [mr[1].point_from_proportion(1 - v) for v in np.linspace(0, 1, 10)] + [fb.fach.get_center() + LEFT * 0.15],
                       n=16, tempo=1.4, farbe=GELB, radius=0.05).set_z_index(3)
        an = ValueTracker(0.0)
        pulsend(fl, an, 5.0, 0.1)
        self.add(fl)
        fb.ir.set_fill(ROT)
        flimmern(fb.ir, 0.2, 1.0, 5.0, stroke=False, fill=True)
        t2 = VGroup(T("braucht Strom", 24, GELB, BOLD), T("Spannung bricht ein: 1,0 V", 24, ROT_HELL, BOLD)).arrange(
            DOWN, buff=0.1).move_to([4.6, -2.3, 0])
        self.play(an.animate.set_value(1.0), FadeIn(t2[0], shift=UP * 0.1), run_time=self.rt(0.5, 8, wort="bricht"))
        self.bis_wort(8, "bricht")
        self.play(FadeIn(t2[1], shift=UP * 0.1), run_time=self.rt(0.5, 9))
        schweben(t2, 0.02, 0.5, 0.3)
        # Merksatz
        self.bis_wort(9, "weniger")   # 20.11. Faktencheck: Merksatz neu formuliert
        alle_updater_weg(keiner)
        ms = ergebnis("leer = hoher Innenwiderstand", 36).move_to([0, 0.9, 0])
        self.bis_wort(9, "Innenwiderstand")
        self.play(ReplacementTransform(keiner, ms), run_time=self.rt(0.6, 10))
        puls(ms, 0.03, 0.9)

        # Zusammengefasst
        self.bis(10)
        alt = Group(*[m for m in self.mobjects if m is not self.hg and not getattr(m, "_hud_w", None)
                      and not isinstance(m, ValueTracker)])
        for mm2 in alt.get_family():
            mm2.clear_updaters()
        zk = T("Zusammengefasst", 44, WEISS, BOLD).move_to([0, 3.0, 0])
        self.play(FadeOut(alt, shift=UP * 0.4), FadeIn(zk, shift=DOWN * 0.2), run_time=self.rt(0.6, 11))
        self.aufraeumen(zk, *hud_teile(self))
        schweben(zk, 0.02, 0.4)
        zeilen = [MT('Jede echte Quelle hat einen <span foreground="#FFC400">Innenwiderstand</span>', 40, WEISS, BOLD),
                  MT('<span foreground="#22D3EE">Uₖ = U₀ − I · Rᵢ</span>', 44, WEISS, BOLD),
                  MT('Batterie immer <span foreground="#FFC400">unter Last</span> prüfen', 40, WEISS, BOLD)]
        for i, (z, y) in enumerate(zip(zeilen, (1.5, 0.1, -1.3))):
            z.move_to([0, y, 0])
            self.bis(11 + i)
            self.play(FadeIn(z, shift=RIGHT * 0.3), run_time=self.rt(0.6, 12 + i))
            schweben(z, 0.03, 0.45, 0.3 * i)

        # Naechstes Video (Video 14: Fr 27.11., laut kalender.md)
        self.bis(14)
        zus = VGroup(zk, *zeilen)
        alle_updater_weg(zus)
        self.play(FadeOut(zus, shift=UP * 0.4), run_time=self.rt(0.5, 14, 0.3))
        self.aufraeumen(*hud_teile(self))
        bild = VGroup(multimeter(ORIGIN, 0.75), blitz_form(0.9, GELB).shift(RIGHT * 0.9 + DOWN * 0.6)).move_to(ORIGIN)
        self.abspann("Richtig messen", k=15, bild=bild, datum="ab 27.11.")
        self.bis_wort(15, "knallt")
        self.abspann_video_zeigen(run_time=self.rt(1.0, 16))
        self.bis(16)                                   # "Abonnier den Kanal" (Ivan 8.11.)
        self.abspann_abo_zeigen(run_time=self.rt(1.0, 17))
        self.bis(17)                                   # "Bis dann bei Watt?!"
        self.abspann_abo_zeigen(run_time=self.rt(1.0, 18))
        self.ende_abspann()                            # 7 s Nachlauf fuer die Endscreen-Elemente
