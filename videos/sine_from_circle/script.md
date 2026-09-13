# Sine from a Circle

**One-line premise:** the sine wave isn't a separate object from the circle — it
*is* the circle's height, unrolled against angle.

**Length:** ~14s across two parts.

This file is the storyboard. `scenes.py` implements it beat for beat; each
scene class carries the beat's name in a comment so the two stay in sync.

---

## Part01_Circle — the setup

**Beat 1 — the circle**
- *On screen:* a unit circle, left half of the frame, drawn in MUTED. A dot on
  its edge at angle 0 (the 3 o'clock position) in ACCENT, and a radius line
  from center to dot, also MUTED.
- *What changes:* circle and radius fade in together; the dot fades in a beat
  later so the eye lands on it last.
- *Timing:* ~1s fade, ~0.5s hold. Calm — nothing is being claimed yet.

**Beat 2 — the empty stage**
- *On screen:* axes on the right half. X axis spans one full revolution
  (0 to 2π) and is labeled "angle"; Y axis spans −1.5 to 1.5, labeled
  "height". Axes in MUTED, labels in TEXT.
- *What changes:* axes fade in after the circle, so the order reads as
  "here's the thing → here's where we'll record it".
- *Timing:* ~1s. Hold ~1s on the complete, still frame before Part 2 starts.

**Meaning-carrying details:**
- The dot is the *only* ACCENT object on screen. It's the subject; everything
  else is scaffolding, hence MUTED.
- The axes are empty on purpose. The frame poses a question — what goes here? —
  and Part 2 answers it.
- Y range is 1.5, not 1.0: the curve needs headroom or it reads as clipped.

---

## Part02_Trace — the unrolling

**Beat 3 — one revolution**
- *On screen:* everything from Part 1.
- *What changes:* the dot travels counterclockwise around the circle, exactly
  one full revolution. The radius line stays attached to it. As the dot moves,
  a curve draws on the right axes plotting the dot's *height* against the angle
  it has swept. A dashed MUTED line connects the dot to the pen tip — the
  curve's leading end — at every instant.
- *Timing:* 8s, linear. Linear matters: any easing would make the sine look
  like it has a variable period, which is a lie about the mathematics.

**Beat 4 — the name**
- *On screen:* completed circle-and-curve.
- *What changes:* the dashed connector fades out (the correspondence has been
  made; the scaffolding can go). Then `y = sin(θ)` fades in as real LaTeX,
  centered under the curve.
- *Timing:* ~0.5s for the connector out, ~1s for the label in, ~2s hold on the
  final frame.

**Meaning-carrying details:**
- **The dot and the curve are the same color.** This is the whole point of the
  video. Shared color says "these are one quantity", which is the claim being
  made. If you change one, change the other.
- **The dashed connector is horizontal at every instant** — it links the dot's
  height to the curve's height. It's the visual proof that the graph is reading
  off the circle, not being drawn from a formula.
- The label arrives *last*, after the thing itself has been shown. The viewer
  should already understand the shape before it's given a name.
