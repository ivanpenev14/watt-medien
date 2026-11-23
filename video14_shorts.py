"""Watt?! Short 14-b (Prüfungsfrage Vorwiderstand): eigene Szene, weil die Short-Frage (100 µA, 1 kΩ, 10 V, drei
Antworten) so nicht im Video vorkommt. Zeiten aus stimme/cues_shorts.json (short14-b, +0,25 s Versatz wie make_short2).
Rendern: WATT_CUES=stimme/cues_shorts.json $VENV/bin/manim -r 2560,1440 --fps 60 --disable_caching video14_shorts.py ShortVorwiderstand
Hochformat: alles Wichtige mittig, >= 90 px vom Bildrand (Band wird auf 1080 px Breite verkleinert), grosse Schrift.
"""
from video14_messen import *  # noqa: F401,F403


class ShortVorwiderstand(WattScene):
    def construct(self):
        ant = ValueTracker(0.0)
        # Messwerk links, Reihenschaltung rechts daneben
        mw = messwerk([-4.3, 1.1, 0], ant, 1.05, WEISS, "Messwerk")
        self.bis_wort(1, "Messwerk")
        self.play(FadeIn(mw, scale=0.7), run_time=self.rt(0.5, 1, wort="hundert"))
        self.bis_wort(1, "hundert")
        self.play(ant.animate.set_value(1.0), run_time=self.rt(0.6, 1, wort="Innenwiderstand"), rate_func=smooth)
        b1 = badge("100 µA Vollausschlag", GELB, NAVY, 30).move_to([-4.3, -0.55, 0])
        self.play(FadeIn(b1, scale=1.2), run_time=0.3)
        self.bis_wort(1, "Innenwiderstand")
        b2 = badge("Rᵢ = 1 kΩ", WEISS, NAVY, 30).move_to([-4.3, -1.3, 0])
        self.play(FadeIn(b2, scale=1.2), run_time=self.rt(0.4, 2))
        schweben(VGroup(b1, b2), 0.02, 0.5)
        # Ziel: 10 V an den Klemmen
        self.bis_wort(2, "zehn")
        xv = 2.2
        mw2 = messwerk([xv + 1.7, 1.7, 0], ant, 0.5)
        rv = widerstand_h([xv - 0.3, 1.7, 0], 1.3, 0.5, CYAN)
        rvt = T("Rᵥ = ?", 40, CYAN, HEAVY).next_to(rv, UP, 0.18)
        dv = VGroup(Line([xv - 2.0, 1.7, 0], rv.get_left()), Line(rv.get_right(), mw2.kreis.get_left())).set_stroke(WEISS, 5)
        klemmen = VGroup(Dot([xv - 2.0, 1.7, 0], 0.11, color=CYAN), Dot(mw2.kreis.get_right(), 0.11, color=CYAN),
                         Line(mw2.kreis.get_right(), [xv + 3.3, 1.7, 0]).set_stroke(WEISS, 5),
                         polung([xv - 2.0, 1.38, 0], [xv + 3.3, 1.38, 0], CYAN, 24))
        self.play(FadeIn(dv), FadeIn(klemmen), FadeIn(mw2), run_time=self.rt(0.5, 2, wort="Volt"))
        zehn = badge("10 V", CYAN, NAVY, 40).move_to([xv + 0.6, 3.1, 0])
        self.play(FadeIn(zehn, scale=1.3), run_time=self.rt(0.4, 3))
        puls(zehn, 0.04, 0.9)
        self.bis(3)
        self.play(GrowFromCenter(rv), FadeIn(rvt), run_time=self.rt(0.5, 4))
        wackeln(rvt, 0.04, 1.0)
        # drei Antworten
        self.bis(4)
        opt = VGroup(*[badge(t, NAVY2, WEISS, 44) for t in ("9,9 kΩ", "99 kΩ", "999 kΩ")]).arrange(RIGHT, buff=0.6).move_to([1.4, -2.75, 0])
        for o in opt:
            o[0].set_stroke(GRAU, 3)
        for i, w in enumerate(("neunkommaneun", "neunundneunzig", "neunhundertneunundneunzig")):
            self.bis_wort(4, w)
            self.play(FadeIn(opt[i], scale=1.3), run_time=self.rt(0.4, 4, wort=("neunundneunzig", "neunhundertneunundneunzig", None)[i]) if i < 2 else self.rt(0.4, 5))
            schweben(opt[i], 0.03, 0.5, 0.2 * i)
        # Denkpause (3-2-1 kommt aus make_short2), Antwort
        self.bis(6)
        alle_updater_weg(opt)
        self.play(opt[1][0].animate.set_fill(GELB).set_stroke(GELB, 3), opt[1][1].animate.set_color(NAVY),
                  opt[0].animate.set_opacity(0.3), opt[2].animate.set_opacity(0.3), run_time=self.rt(0.5, 7))
        puls(opt[1], 0.05, 0.9)
        # Loesung rechts unter der Schaltung
        x = 2.4
        self.bis_wort(7, "hundert")
        l1 = MT('100 µA · 1 kΩ = <span foreground="#FFC400">0,1 V</span>', 38, WEISS, BOLD).move_to([x, -0.15, 0])
        self.play(FadeIn(l1, shift=UP * 0.15), aufleuchten(mw2.kreis, GELB, 8), run_time=self.rt(0.7, 7, wort="nullkomma"))
        self.bis_wort(7, "nullkomma")
        um = badge("0,1 V", GELB, NAVY, 28).next_to(mw2, DOWN, 0.15)
        self.play(FadeIn(um, scale=1.2), run_time=self.rt(0.4, 8))
        self.bis_wort(8, "neunkommaneun")
        l2 = MT('10 V − 0,1 V = <span foreground="#22D3EE">9,9 V</span>', 38, WEISS, BOLD).move_to([x, -0.95, 0])
        self.play(FadeIn(l2, shift=UP * 0.15), aufleuchten(rv, CYAN, 8), run_time=self.rt(0.7, 8, wort="Vorwiderstand"))
        uv = badge("9,9 V", CYAN, NAVY, 28).next_to(rv, DOWN, 0.15)
        self.play(FadeIn(uv, scale=1.2), run_time=0.3)
        self.bis_wort(8, "geteilt")
        l3 = MT('9,9 V / 100 µA = <span foreground="#22D3EE">99 kΩ</span>', 38, WEISS, BOLD).move_to([x, -1.75, 0])
        self.play(FadeIn(l3, shift=UP * 0.15), run_time=self.rt(0.7, 8, wort="neunundneunzig"))
        self.bis_wort(8, "neunundneunzig")
        alle_updater_weg(rvt)
        self.play(Transform(rvt, T("Rᵥ = 99 kΩ", 40, CYAN, HEAVY).next_to(rv, UP, 0.18)), aufleuchten(rv, CYAN, 8), run_time=self.rt(0.5, 9))
        self.bis(9)
        erg = ergebnis("Rᵥ = 99 kΩ", 52).move_to([-4.3, -1.0, 0])
        alle_updater_weg(b1, b2)
        self.play(FadeOut(b1), FadeOut(b2), FadeIn(erg, scale=1.2), run_time=self.rt(0.5, 10))
        puls(erg, 0.03, 0.9)
        self.bis(10)
        fl = Fluss([[xv - 2.0, 1.7, 0], [xv + 3.3, 1.7, 0]], n=12, tempo=1.2, farbe=GELB, radius=0.06, rand=0.3).set_z_index(3)
        self.add(fl)
        self.play(aufleuchten(mw2.kreis, GELB, 8), run_time=self.rt(0.6, 11))
        self.ende()
