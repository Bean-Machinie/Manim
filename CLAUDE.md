# Manim explainer series — working conventions

A repo for turning storyboard descriptions into rendered explainer videos.
The workflow is: **description → `script.md` → `scenes.py` → preview → final.**

## How videos get described

The user describes a video as a **storyboard of beats**. Each beat is:

> **what's on screen** → **what changes** → **timing/emphasis**

...followed by a short list of **meaning-carrying details**: the choices that
aren't decoration, but are load-bearing for the explanation. "The dot and the
curve are the same color" isn't a style note — it's the argument the video is
making. Those details are the ones that must survive into the code, and the
ones to ask about if the description is ambiguous.

When you get a description, write it into `script.md` in that beat form
*before* writing scene code. The script is the spec; `scenes.py` implements it.
If they drift apart, the script is right and the code is wrong.

## Adding a new video

1. `mkdir videos/<name>/`
2. Write `videos/<name>/script.md` from the description, in beats as above.
3. Implement `videos/<name>/scenes.py` with scene classes named
   `Part01_Something`, `Part02_SomethingElse`, ... The numeric prefix is how
   `render.py` finds and orders them, so it isn't optional.
4. Import colors, fonts, sizes, and timings from `common/theme.py`.
5. Reuse what's in `common/mobjects.py` and `common/helpers.py`.
6. Preview it, then render final.

`videos/sine_from_circle/` is the worked reference — read its `script.md` and
`scenes.py` side by side to see how a description maps to code.

### Rules

- **Never hardcode a color.** Every color comes from `common/theme.py`, by its
  semantic name (`ACCENT`, `MUTED`, `HIGHLIGHT`, ...). A literal hex in a scene
  file is a bug. If you need a color that doesn't exist, add it to `theme.py`
  with a note on what it *means*, then import it.
- Same for fonts and standard timings — `text_kwargs()`, `tex_kwargs()`,
  `BEAT`, `BEAT_FAST`, `BEAT_SLOW`.
- **Use `tex_kwargs()` for all `MathTex`/`Tex`**, so math typesets identically
  across the series.
- Each `PartNN_` class renders as an independent scene and can't inherit state
  from the previous one. When parts share a set, build it in one function
  (see `build_stage()` in the reference video) and call it from both.
- Prefer one `ValueTracker` driving several `always_redraw` mobjects over
  several separately-animated objects. It keeps things in sync by construction.

### The promote-on-second-use rule

`common/mobjects.py` and `common/helpers.py` gain a new entry **the second time
a video needs it — never the first.**

Write it inline in `videos/<name>/scenes.py` first. When a second video reaches
for the same thing, move it into `common/` and update both callers. Abstractions
built on one example are shaped around a guess; the second use is what reveals
which parts are actually general. Don't pre-build a library of objects you
imagine will be useful.

## Rendering

```bash
python render.py <name>              # all parts, high quality, concatenated to output/<name>.mp4
python render.py <name> --preview    # fast low-quality render of all parts, then opens it
python render.py <name> --part 2     # just Part02, fast — the iteration loop
```

**Preview-then-final workflow:** while building a video, work in `--part N` on
whichever part you're editing — 480p15 renders in seconds and is enough to
judge staging and timing. Use `--preview` to check how the parts read together.
Only run the bare `python render.py <name>` (1080p30 + ffmpeg concat) when the
video is done; it's slow and it's the only mode that writes the final
`output/<name>.mp4`.

Never commit anything from `output/` — it's gitignored.

## Layout

```
manim.cfg              16:9, 30fps, dark background, output/ as media dir
common/theme.py        palette, fonts, sizes, timings, Tex template
common/mobjects.py     reusable on-screen objects (promote-on-second-use)
common/helpers.py      reusable animation patterns (promote-on-second-use)
videos/<name>/script.md   the storyboard, in beats
videos/<name>/scenes.py   Part01_/Part02_/... implementing it
assets/                svgs, images, data
output/                renders (gitignored)
render.py              the render wrapper
```

## System dependencies

Rendering needs, beyond `requirements.txt`:

- **LaTeX** — required for `MathTex`/`Tex`. Without it, any scene containing
  math fails with a bare `FileNotFoundError` from `subprocess`. That error means
  "install LaTeX", not "the scene is broken".
- **ffmpeg** — required by `render.py` for the final concat step. Manim 0.19
  encodes individual scenes through PyAV, so single-scene renders work without
  it; only the full `python render.py <name>` needs it.

On Windows: `winget install --id=Gyan.FFmpeg -e` and
`winget install --id=MiKTeX.MiKTeX -e`, then restart the terminal.

## Environment

`.venv/` is a Python **3.12** virtualenv — not 3.14, which manim 0.19's
dependency wheels don't all cover yet.

```bash
.venv/Scripts/python.exe render.py sine_from_circle --preview
```
