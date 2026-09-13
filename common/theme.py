"""The look of the series.

Every video imports from here so the whole channel reads as one thing. The
names are *semantic* (what a color is for) rather than descriptive (what it
looks like) — that way, restyling the series is a change to this file alone and
the scene code stays correct.

Rule: no scene file contains a literal color. If you need a new one, add it
here with a note about what it means.
"""

from manim import ManimColor, TexTemplate

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
# BG must match `background_color` in manim.cfg. Manim paints the canvas from
# the config before any scene code runs, so the value lives in both places.
BG = ManimColor("#12141C")  # canvas; near-black with a slight blue cast

ACCENT = ManimColor("#4CC9F0")  # the subject of the shot — the thing being explained
HIGHLIGHT = ManimColor("#F7B32B")  # a beat of emphasis; use sparingly or it stops meaning anything
MUTED = ManimColor("#6B7280")  # scaffolding: axes, grids, construction lines
TEXT = ManimColor("#E8EAF0")  # labels and prose
SUCCESS = ManimColor("#4ADE80")  # a result landing / something resolving
WARNING = ManimColor("#F87171")  # a counterexample or a thing going wrong

# Secondary accent, for when two subjects share a frame and must stay distinct.
ACCENT_ALT = ManimColor("#C77DFF")

# --------------------------------------------------------------------------
# Type
# --------------------------------------------------------------------------
# Used by Text(); a widely-available sans so renders don't silently fall back
# to something else on another machine.
FONT = "Segoe UI"
FONT_MONO = "Consolas"

# Sizes, so headings and captions stay consistent between videos.
SIZE_TITLE = 48
SIZE_LABEL = 32
SIZE_CAPTION = 24

# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------
# Shared beat lengths. Calm pacing is part of the series' identity — reach for
# these before inventing a new duration.
BEAT_FAST = 0.5
BEAT = 1.0
BEAT_SLOW = 2.0

# --------------------------------------------------------------------------
# LaTeX
# --------------------------------------------------------------------------
# A single template for all Tex/MathTex in the series, so math is typeset
# identically everywhere. amsmath/amssymb cover most of what explainers need.
TEX_TEMPLATE = TexTemplate(
    preamble=r"""
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
""",
)


def tex_kwargs(**overrides):
    r"""Standard kwargs for MathTex/Tex, so LaTeX color and template match.

    Usage:  MathTex(r"y = \sin(\theta)", **tex_kwargs(color=ACCENT))
    """
    kwargs = {"tex_template": TEX_TEMPLATE, "color": TEXT}
    kwargs.update(overrides)
    return kwargs


def text_kwargs(**overrides):
    """Standard kwargs for Text(), so on-screen prose matches everywhere."""
    kwargs = {"font": FONT, "color": TEXT, "font_size": SIZE_LABEL}
    kwargs.update(overrides)
    return kwargs
