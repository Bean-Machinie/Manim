# Manim explainer series

Storyboard-driven explainer videos, built with [Manim Community Edition](https://www.manim.community/).

## Setup

```bash
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Plus two system dependencies:

```bash
winget install --id=Gyan.FFmpeg -e
winget install --id=MiKTeX.MiKTeX -e
```

## Render

```bash
python render.py sine_from_circle --preview   # fast, opens the result
python render.py sine_from_circle --part 2    # one part, for iteration
python render.py sine_from_circle             # final 1080p30 -> output/sine_from_circle.mp4
```

See [CLAUDE.md](CLAUDE.md) for the workflow and conventions.
