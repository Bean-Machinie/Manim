"""Reusable on-screen objects.

Deliberately almost empty. The rule for this file is *promote on second use*:
an object earns a place here the second time a video needs it, never the first
time we imagine it might. Building a library up front produces abstractions
shaped around guesses instead of around real scenes — so write it inline in
videos/<name>/scenes.py first, and move it here when a second video reaches
for it. See CLAUDE.md.
"""

from manim import (
    DOWN,
    VGroup,
    Dot,
    Text,
    always_redraw,
)

from common.theme import ACCENT, SIZE_CAPTION, text_kwargs


class LabeledDot(VGroup):
    """A dot with a text label that follows it around.

    The generic "here is the thing you should be watching" marker. The label
    tracks the dot every frame, so it stays attached through any animation that
    moves the dot — including ones driven by a ValueTracker.

        dot = LabeledDot("P", color=ACCENT).move_to(LEFT * 2)
        self.play(dot.animate.move_to(RIGHT * 2))   # label comes along

    Args:
        label: text to show, or None for a bare dot.
        color: dot and label color; defaults to the series ACCENT.
        radius: dot radius.
        direction: where the label sits relative to the dot.
        buff: gap between dot and label.
    """

    def __init__(
        self,
        label: str | None = None,
        color=ACCENT,
        radius: float = 0.08,
        direction=DOWN,
        buff: float = 0.2,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.dot = Dot(radius=radius, color=color)
        self.add(self.dot)

        if label is not None:
            # always_redraw re-evaluates each frame, so the label follows the
            # dot no matter what moved it.
            self.label = always_redraw(
                lambda: Text(
                    label, **text_kwargs(color=color, font_size=SIZE_CAPTION)
                ).next_to(self.dot, direction, buff=buff)
            )
            self.add(self.label)
        else:
            self.label = None

    def get_center(self):
        """Center on the dot, not the dot+label bounding box.

        Without this, .move_to() would aim the *group's* midpoint at the
        target, and the dot would sit off by half the label height.
        """
        return self.dot.get_center()
