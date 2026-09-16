"""Morley's Miracle.

Implements videos/morleys_miracle/script.md beat for beat. Read the script
first; the beat names in the comments below map back to it.

Scene classes are named Part01_/Part02_/... — render.py discovers them by that
numeric prefix and renders them in order.
"""

from __future__ import annotations

import numpy as np
from manim import (
    PI,
    DOWN,
    UP,
    Arc,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Polygon,
    Scene,
    Tex,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
)

from common.theme import (
    ACCENT,
    ACCENT_ALT,
    BEAT,
    BEAT_FAST,
    BEAT_SLOW,
    HIGHLIGHT,
    MUTED,
    SIZE_CAPTION,
    tex_kwargs,
)

# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
# Promotion candidates: ray_intersect() and trisector_dir() are the generic
# half of this file. Per CLAUDE.md's promote-on-second-use rule they stay
# inline until a *second* video needs them — at which point they, and probably
# a "trisected triangle" mobject built on them, move into common/.


def _angle_of(v: np.ndarray) -> float:
    """Direction of a scene-space vector, in radians CCW from +x."""
    return float(np.arctan2(v[1], v[0]))


def _wrap(angle: float) -> float:
    """Fold an angle into (-pi, pi] — the signed short way round."""
    return (angle + PI) % (2 * PI) - PI


def _unit(angle: float) -> np.ndarray:
    return np.array([np.cos(angle), np.sin(angle), 0.0])


def trisector_dir(vertex, toward, other, *, index: int = 1) -> np.ndarray:
    """Direction of a trisector of the interior angle at `vertex`.

    The interior angle at `vertex` is swept from the ray towards `toward` round
    to the ray towards `other`. `index=1` is the trisector one third of the way
    across — the one *adjacent to the side vertex-toward*, which is the pair
    Morley's theorem is about. `index=2` is the other one.

    The sweep is wrapped to the signed short way round, which is always the
    interior angle of a triangle, so this works whichever order the vertices
    were given in and whichever way round the triangle is wound.
    """
    base = _angle_of(toward - vertex)
    sweep = _wrap(_angle_of(other - vertex) - base)
    return _unit(base + index * sweep / 3.0)


def ray_intersect(p1, d1, p2, d2) -> np.ndarray:
    """Where the line through p1 along d1 meets the line through p2 along d2.

    Solves p1 + t*d1 == p2 + s*d2 in the xy plane. The callers here only
    intersect trisectors of a non-degenerate triangle, which are never
    parallel, so a singular system would mean the geometry is already wrong —
    let np.linalg.solve raise rather than paper over it.
    """
    matrix = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    t, _ = np.linalg.solve(matrix, (p2 - p1)[:2])
    return p1 + t * d1


def morley_points(a, b, c):
    """The three Morley points, ordered (opposite A, opposite B, opposite C).

    Each is where the two trisectors *adjacent to a side* cross: the point
    opposite A is where B's trisector nearest BC meets C's trisector nearest
    CB. Any other pairing gives points that are not equilateral — this choice
    is the theorem, so it is the line to check if the video ever looks wrong.
    """
    return (
        ray_intersect(b, trisector_dir(b, c, a), c, trisector_dir(c, b, a)),
        ray_intersect(c, trisector_dir(c, a, b), a, trisector_dir(a, c, b)),
        ray_intersect(a, trisector_dir(a, b, c), b, trisector_dir(b, a, c)),
    )


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
# B and C are pinned to the bottom of the frame; A is the vertex Part04 drives.
# Its path is an arc sampled by vertex_a(u) for u in [0, 1]. Along it the
# smallest interior angle never drops below 30 degrees and the highest point of
# the triangle still clears the top of the frame — both load-bearing, see the
# script.
B_POINT = np.array([-4.3, -2.3, 0.0])
C_POINT = np.array([4.1, -2.0, 0.0])

# How far along the path Part04 stops. Deliberately not 1.0: ending back at the
# start would read as a loop instead of as a claim that held all the way. And
# deliberately short of the path's far end, where the triangle passes through a
# near-isosceles shape — finishing there would hand the viewer the "it's just
# symmetry" explanation that Part01 goes out of its way to rule out. At 0.70
# the triangle is obtuse and plainly scalene: 96/31/53 against the opening
# 81/61/37.
U_END = 0.70

TRIANGLE_WIDTH = 3.0
TRISECTOR_WIDTH = 2.0
INNER_WIDTH = 5.0
ARC_RADIUS = 0.75
# Each equal-angle arc is drawn slightly short of its third, leaving a gap on
# either side. Without the gap the three arcs meet end to end and render as one
# continuous arc — which says "here is an angle", the opposite of the point.
ARC_SPAN = 0.74
# Half-length of an equal-length tick. Kept small against the ~1.0-unit inner
# side: longer and the ticks read as crosses drawn on the triangle rather than
# as marks on its edges.
TICK_LENGTH = 0.085
LABEL_BUFF = 0.42


def vertex_a(u: float) -> np.ndarray:
    """Vertex A at parameter u along its path. u=0 is the establishing shape."""
    phase = PI * u
    return np.array([-2.0 + 4.2 * np.sin(phase), 2.3 + 1.0 * np.sin(2 * phase), 0.0])


def outer_triangle(a, b, c) -> Polygon:
    """The original triangle. MUTED: it is scaffolding, not the subject."""
    return Polygon(a, b, c, color=MUTED, stroke_width=TRIANGLE_WIDTH)


def trisectors_at(vertex, left, right) -> VGroup:
    """Both trisectors of the angle at `vertex`, drawn to the opposite side.

    Ending them on side left-right keeps the construction inside the triangle,
    where the intersections it is building actually live.
    """
    side_dir = right - left
    rays = []
    for index in (1, 2):
        direction = trisector_dir(vertex, left, right, index=index)
        end = ray_intersect(vertex, direction, left, side_dir)
        rays.append(Line(vertex, end, color=ACCENT_ALT, stroke_width=TRISECTOR_WIDTH))
    return VGroup(*rays)


def equal_angle_arcs(vertex, left, right) -> VGroup:
    """Three arcs across the three equal sub-angles, defining "trisected".

    HIGHLIGHT, and shown at one vertex only — a one-time definition of the
    word, not a permanent annotation.
    """
    base = _angle_of(left - vertex)
    sweep = _wrap(_angle_of(right - vertex) - base) / 3.0
    inset = sweep * (1.0 - ARC_SPAN) / 2.0
    # Same radius for all three — equal radius is what makes them comparable —
    # but each inset from its third, so the eye can count three of them.
    return VGroup(
        *(
            Arc(
                radius=ARC_RADIUS,
                start_angle=base + k * sweep + inset,
                angle=sweep * ARC_SPAN,
                arc_center=vertex,
                color=HIGHLIGHT,
                stroke_width=TRISECTOR_WIDTH + 1.0,
            )
            for k in range(3)
        )
    )


def inner_triangle(points) -> Polygon:
    """The Morley triangle. ACCENT — from here on, this is the subject."""
    return Polygon(*points, color=ACCENT, stroke_width=INNER_WIDTH)


def equal_length_ticks(points) -> VGroup:
    """One tick at the midpoint of each inner side.

    Standard "these three lengths are equal" notation. This is the video's
    evidence that the triangle is equilateral rather than merely
    equilateral-looking, so it stays on screen through Part04's deformation.
    """
    ticks = []
    ordered = list(points)
    for start, end in zip(ordered, ordered[1:] + ordered[:1]):
        midpoint = (start + end) / 2.0
        along = (end - start) / np.linalg.norm(end - start)
        normal = np.array([-along[1], along[0], 0.0])
        ticks.append(
            Line(
                midpoint - normal * TICK_LENGTH,
                midpoint + normal * TICK_LENGTH,
                color=ACCENT,
                stroke_width=INNER_WIDTH,
            )
        )
    return VGroup(*ticks)


def vertex_label(name: str, vertex, a, b, c) -> MathTex:
    """A vertex label pushed out from the centroid, so it clears the sides."""
    outward = vertex - (a + b + c) / 3.0
    outward = outward / np.linalg.norm(outward)
    return MathTex(name, **tex_kwargs(color=MUTED)).move_to(
        vertex + outward * LABEL_BUFF
    )


def build_figure(u: float = 0.0) -> dict:
    """Every piece of the figure at parameter u, as a dict.

    Each PartNN_ renders as its own scene and cannot inherit the previous one's
    final frame, so all four parts rebuild the figure from here. One
    construction function is what stops them drifting apart.
    """
    a, b, c = vertex_a(u), B_POINT, C_POINT
    points = morley_points(a, b, c)
    return {
        "a": a,
        "b": b,
        "c": c,
        "triangle": outer_triangle(a, b, c),
        "labels": VGroup(
            vertex_label("A", a, a, b, c),
            vertex_label("B", b, a, b, c),
            vertex_label("C", c, a, b, c),
        ),
        # Keyed per vertex so Part02 can bring them in one at a time.
        "trisectors_a": trisectors_at(a, b, c),
        "trisectors_b": trisectors_at(b, c, a),
        "trisectors_c": trisectors_at(c, a, b),
        "dots": VGroup(*(Dot(p, color=ACCENT, radius=0.075) for p in points)),
        "inner": inner_triangle(points),
        "ticks": equal_length_ticks(points),
    }


def caption() -> Tex:
    """The claim, in real LaTeX. Parts 03 and 04 must show the same words."""
    return Tex(
        r"always equilateral",
        **tex_kwargs(color=ACCENT, font_size=SIZE_CAPTION * 1.6),
    ).move_to(DOWN * 3.2)


class Part01_Triangle(Scene):
    """Beat 1: an arbitrary, clearly lopsided triangle."""

    def construct(self):
        figure = build_figure()

        # Beat 1 — the triangle draws first, then gets its names. MUTED
        # throughout: the subject of this video does not exist yet.
        self.play(Create(figure["triangle"]), run_time=BEAT_SLOW)
        self.play(FadeIn(figure["labels"]), run_time=BEAT)
        self.wait(BEAT_SLOW)


class Part02_Trisect(Scene):
    """Beats 2-3: each interior angle cut into three equal parts."""

    def construct(self):
        figure = build_figure()
        self.add(figure["triangle"], figure["labels"])

        # Beat 2 — vertex A first, with arc marks pinning down what "trisect"
        # means. The arcs are a definition, so they leave once it has landed.
        self.play(Create(figure["trisectors_a"]), run_time=BEAT)
        arcs = equal_angle_arcs(figure["a"], figure["b"], figure["c"])
        self.play(Create(arcs), run_time=BEAT)
        self.wait(BEAT)
        self.play(FadeOut(arcs), run_time=BEAT_FAST)
        self.wait(BEAT_FAST)

        # Beat 3 — B, then C. One vertex at a time keeps it followable, so each
        # gets a beat of its own to land in; the meaning is established now, so
        # no more arcs.
        self.play(Create(figure["trisectors_b"]), run_time=BEAT)
        self.wait(BEAT_FAST)
        self.play(Create(figure["trisectors_c"]), run_time=BEAT)
        self.wait(BEAT + BEAT_FAST)


class Part03_Reveal(Scene):
    """Beats 4-6: the adjacent-trisector crossings, and what they form."""

    def construct(self):
        figure = build_figure()
        self.add(
            figure["triangle"],
            figure["labels"],
            figure["trisectors_a"],
            figure["trisectors_b"],
            figure["trisectors_c"],
        )

        # Beat 4 — the three points together, not one at a time: they are a
        # single fact about the construction, not three separate ones.
        self.play(FadeIn(figure["dots"], scale=0.4), run_time=BEAT)
        self.wait(BEAT_FAST)

        # Beat 5 — the handoff to ACCENT. The ticks are what makes this a claim
        # of equality rather than an invitation to eyeball it, so they get a
        # beat to be read before the caption arrives on top of them.
        self.play(Create(figure["inner"]), run_time=BEAT)
        self.play(Create(figure["ticks"]), run_time=BEAT)
        self.wait(BEAT_FAST)

        # Beat 6 — the name arrives last, after the thing itself.
        self.play(FadeIn(caption(), shift=UP * 0.3), run_time=BEAT)
        self.wait(BEAT_SLOW)


class Part04_Miracle(Scene):
    """Beats 7-8: the outer triangle deforms; the inner one refuses to."""

    LIVE_KEYS = (
        "triangle",
        "labels",
        "trisectors_a",
        "trisectors_b",
        "trisectors_c",
        "dots",
        "inner",
        "ticks",
    )

    def construct(self):
        # u is the single source of truth. Everything on screen is recomputed
        # from it every frame, so the trisectors, the three crossings and the
        # inner triangle stay in sync *by construction* rather than by being
        # animated in parallel — which is the entire argument of this part.
        u = ValueTracker(0.0)

        # One figure per frame, shared by all eight redrawn pieces. Calling
        # build_figure() inside each of them instead would rebuild the whole
        # figure — three MathTex labels included — eight times a frame, for the
        # same u. Caching on the tracker value is exact: within a frame every
        # caller asks for the identical float.
        cache: dict = {}

        def figure_now() -> dict:
            u_now = u.get_value()
            if cache.get("u") != u_now:
                cache["u"], cache["figure"] = u_now, build_figure(u_now)
            return cache["figure"]

        # Part03's closing frame, rebuilt as live objects. The default-argument
        # binding is what stops every lambda from closing over the last key.
        live = VGroup(
            *(
                always_redraw(lambda key=key: figure_now()[key])
                for key in self.LIVE_KEYS
            )
        )
        self.add(live, caption())

        # Beat 7 — 8s, linear. Easing would suggest the deformation has
        # interesting and uninteresting moments; it does not, and the point is
        # that nothing happens to the inner triangle at any of them.
        self.play(u.animate.set_value(U_END), run_time=8, rate_func=linear)

        # Beat 8 — hold on a triangle plainly different from the opening one.
        self.wait(BEAT_SLOW)
