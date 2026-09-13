"""Sine from a Circle — the reference video for this repo.

Implements videos/sine_from_circle/script.md beat for beat. Read the script
first; the beat names in the comments below map back to it.

Scene classes are named Part01_/Part02_/... — render.py discovers them by that
numeric prefix and renders them in order.
"""

import numpy as np
from manim import (
    TAU,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Scene,
    Text,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
)

from common.helpers import point_on_circle, trace_with_connector
from common.theme import (
    ACCENT,
    BEAT,
    BEAT_FAST,
    BEAT_SLOW,
    MUTED,
    SIZE_CAPTION,
    tex_kwargs,
    text_kwargs,
)

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
# The one geometric constraint that makes this video work: the dashed connector
# must be exactly horizontal, so the circle's vertical scale and the axes'
# vertical scale have to agree.
#
#   dot height   = RADIUS * sin(theta)                      (scene units)
#   pen height   = sin(theta) * Y_LENGTH / y_range_span     (scene units)
#
# Those are equal when Y_LENGTH / y_range_span == RADIUS. With a y range of
# -1.5..1.5 (span 3) and RADIUS 1.5, Y_LENGTH must be 4.5. Change one of these
# and the connector starts to slope, which quietly breaks the video's argument.
RADIUS = 1.5
Y_MAX = 1.5
Y_LENGTH = RADIUS * (2 * Y_MAX)  # = 4.5
X_LENGTH = 6.5

CIRCLE_CENTER = LEFT * 4.3
AXES_CENTER = RIGHT * 3.3


def build_stage():
    """The static set that both parts share.

    Each Part renders as its own independent scene, so Part02 has to rebuild
    Part01's final frame rather than inherit it. Keeping that construction in
    one function is what stops the two parts from drifting apart.

    Returns:
        (stage, parts) where `stage` is a VGroup of everything and `parts` is a
        dict of the individually-animatable pieces.
    """
    # --- Beat 1: the circle ---
    circle = Circle(radius=RADIUS, color=MUTED, stroke_width=3).move_to(CIRCLE_CENTER)

    # The dot starts at angle 0 — the 3 o'clock position.
    dot = Dot(
        point=point_on_circle(CIRCLE_CENTER, RADIUS, 0.0),
        color=ACCENT,
        radius=0.09,
    )
    radius_line = Line(CIRCLE_CENTER, dot.get_center(), color=MUTED, stroke_width=3)

    # --- Beat 2: the empty stage ---
    axes = Axes(
        x_range=[0, TAU, TAU / 4],
        y_range=[-Y_MAX, Y_MAX, 0.5],
        x_length=X_LENGTH,
        y_length=Y_LENGTH,
        axis_config={
            "color": MUTED,
            "stroke_width": 2,
            "include_ticks": True,
            "tick_size": 0.06,
        },
        tips=False,
    ).move_to(AXES_CENTER)

    x_label = Text("angle", **text_kwargs(font_size=SIZE_CAPTION)).next_to(
        axes.x_axis, DOWN, buff=0.3
    )
    y_label = Text("height", **text_kwargs(font_size=SIZE_CAPTION)).next_to(
        axes.y_axis, UP, buff=0.3
    )

    parts = {
        "circle": circle,
        "dot": dot,
        "radius_line": radius_line,
        "axes": axes,
        "x_label": x_label,
        "y_label": y_label,
    }
    return VGroup(*parts.values()), parts


class Part01_Circle(Scene):
    """Beats 1-2: the circle, then the empty axes it will be recorded on."""

    def construct(self):
        _, p = build_stage()

        # Beat 1 — circle and radius arrive together as one object; the dot
        # lands after, so the eye finishes on the subject.
        self.play(Create(p["circle"]), Create(p["radius_line"]), run_time=BEAT)
        self.play(FadeIn(p["dot"], scale=0.5), run_time=BEAT_FAST)
        self.wait(BEAT_FAST)

        # Beat 2 — the empty stage. Posing the question the next part answers.
        self.play(
            Create(p["axes"]),
            FadeIn(p["x_label"]),
            FadeIn(p["y_label"]),
            run_time=BEAT,
        )
        self.wait(BEAT)


class Part02_Trace(Scene):
    """Beats 3-4: one revolution traced onto the axes, then named."""

    def construct(self):
        stage, p = build_stage()
        axes, dot = p["axes"], p["dot"]

        # Part01's closing frame, established instantly — this part opens on it.
        self.add(stage)

        # theta drives everything: the dot's position, the radius line, the
        # curve's extent, and the connector. One animated value, four effects.
        theta = ValueTracker(0.0)

        dot.add_updater(
            lambda m: m.move_to(point_on_circle(CIRCLE_CENTER, RADIUS, theta.get_value()))
        )
        radius_line = always_redraw(
            lambda: Line(
                CIRCLE_CENTER, dot.get_center(), color=MUTED, stroke_width=3
            )
        )
        # Swap the static radius for the live one now that theta exists.
        self.remove(p["radius_line"])
        self.add(radius_line)

        # The curve shares the dot's color deliberately: same color == same
        # quantity. That equivalence is the entire claim of the video.
        trace = trace_with_connector(
            axes,
            np.sin,
            theta,
            dot,
            color=ACCENT,
            connector_color=MUTED,
        )
        self.add(trace.group)

        # Beat 3 — one revolution. linear, because easing here would imply the
        # period changes, which would be false.
        self.play(theta.animate.set_value(TAU), run_time=8, rate_func=linear)

        dot.clear_updaters()

        # Beat 4 — the correspondence has been made, so the scaffolding goes.
        self.play(FadeOut(trace.connector), run_time=BEAT_FAST)

        # Real LaTeX, via the series' shared Tex template.
        label = MathTex(r"y = \sin(\theta)", **tex_kwargs(color=ACCENT)).move_to(
            axes.c2p(TAU / 2, -Y_MAX + 0.25)
        )
        self.play(FadeIn(label, shift=UP * 0.3), run_time=BEAT)
        self.wait(BEAT_SLOW)
