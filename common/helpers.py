"""Reusable animation helpers.

Things that describe *how something moves*, as opposed to common/mobjects.py,
which holds *things that are on screen*. Same promote-on-second-use rule
applies — except for patterns we already know are load-bearing for this series,
like trace_with_connector below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from manim import (
    Axes,
    DashedLine,
    Mobject,
    VGroup,
    VMobject,
    ValueTracker,
    always_redraw,
)

from common.theme import ACCENT, MUTED


@dataclass
class Trace:
    """What trace_with_connector() hands back.

    Attributes:
        curve: the growing plotted curve.
        connector: the dashed line from the source mobject to the pen tip.
        group: both of the above, for a single add()/remove()/FadeOut().
        pen_tip: callable returning the current pen-tip point in scene coords,
            in case a scene wants to hang something else off it.
    """

    curve: VMobject
    connector: VMobject
    group: VGroup
    pen_tip: Callable[[], np.ndarray]


def trace_with_connector(
    axes: Axes,
    func: Callable[[float], float],
    tracker: ValueTracker,
    source: Mobject | Callable[[], np.ndarray],
    *,
    x_start: float | None = None,
    color=ACCENT,
    connector_color=MUTED,
    stroke_width: float = 4.0,
    connector_width: float = 2.0,
    dash_length: float = 0.12,
    dashed_ratio: float = 0.5,
    step: float = 0.02,
) -> Trace:
    r"""Draw a curve as a tracker advances, with a dashed line to the pen tip.

    The pattern this series leans on constantly: something moves on the left,
    and its value is written out as a graph on the right, with a dashed line
    making the correspondence explicit at every instant. The dashed line is
    what turns two separate animations into one idea.

    Everything here is driven by `tracker`, so the caller animates a single
    value and both the curve and the connector follow:

        tracker = ValueTracker(0)
        trace = trace_with_connector(axes, np.sin, tracker, dot)
        self.add(trace.group)
        self.play(tracker.animate.set_value(TAU), run_time=8, rate_func=linear)

    Args:
        axes: the Axes the curve is plotted on.
        func: x -> y, in axes' *data* coordinates.
        tracker: its value is the current x; the curve is drawn from x_start
            up to it.
        source: the mobject the connector starts from (its center is used), or
            a callable returning a point — use a callable when the start isn't
            simply a mobject's center.
        x_start: where the curve begins. Defaults to the axes' x_range start.
        color: curve color. Pass the same color as the source mobject — shared
            color is what reads as "these are the same quantity".
        connector_color: dashed line color; scaffolding, so MUTED by default.
        stroke_width, connector_width, dash_length, dashed_ratio: styling.
        step: sampling step for the curve, in data units. Smaller is smoother
            and slower.

    Returns:
        A Trace. Add `trace.group` to the scene before animating the tracker.
    """
    if x_start is None:
        x_start = axes.x_range[0]

    get_source_point = source.get_center if isinstance(source, Mobject) else source

    def pen_tip() -> np.ndarray:
        """Current end of the curve, in scene coordinates."""
        x = tracker.get_value()
        return axes.coords_to_point(x, func(x))

    def make_curve() -> VMobject:
        x = tracker.get_value()
        # Before the tracker has moved, there's no curve to draw yet — and
        # axes.plot() with a zero-width range would raise.
        if x - x_start < step:
            return VMobject()
        return axes.plot(
            func,
            x_range=[x_start, x, step],
            color=color,
            stroke_width=stroke_width,
        )

    def make_connector() -> VMobject:
        start, end = get_source_point(), pen_tip()
        # A zero-length DashedLine has no direction to normalize.
        if np.linalg.norm(end - start) < 1e-6:
            return VMobject()
        return DashedLine(
            start,
            end,
            color=connector_color,
            stroke_width=connector_width,
            dash_length=dash_length,
            dashed_ratio=dashed_ratio,
        )

    curve = always_redraw(make_curve)
    connector = always_redraw(make_connector)

    return Trace(
        curve=curve,
        connector=connector,
        group=VGroup(curve, connector),
        pen_tip=pen_tip,
    )


def point_on_circle(center: np.ndarray, radius: float, angle: float) -> np.ndarray:
    """Scene-space point at `angle` radians CCW from the +x axis."""
    return center + radius * np.array([np.cos(angle), np.sin(angle), 0.0])
