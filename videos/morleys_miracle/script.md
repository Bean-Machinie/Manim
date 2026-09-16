# Morley's Miracle

**One-line premise:** trisect the three angles of *any* triangle, and the three
points where adjacent trisectors meet form a perfectly equilateral triangle —
and it stays equilateral while you bend the original out of shape.

**Length:** 30s across four parts — 5s + 8s + 7s + 10s.

Every duration below is one of `BEAT_FAST` / `BEAT` / `BEAT_SLOW` from
`common/theme.py`, or a sum of them.

This file is the storyboard. `scenes.py` implements it beat for beat; each
scene class carries the beat's name in a comment so the two stay in sync.

---

## Part01_Triangle — the setup (~0-5s)

**Beat 1 — a lopsided triangle**
- *On screen:* a clearly scalene triangle ABC, filling most of the frame, drawn
  in MUTED. Angles roughly 81° / 61° / 37° — visibly not special.
- *What changes:* the three sides draw in together, then the vertex labels
  `A`, `B`, `C` fade in, placed outward from the centroid so they never sit on
  a side.
- *Timing:* 2s to draw, 1s for the labels, 2s hold. Calm — nothing is being
  claimed yet.

**Meaning-carrying details:**
- The triangle is MUTED because it is *scaffolding*, not the subject. The
  subject doesn't exist yet; it appears in Part 3.
- It has to look arbitrary. A triangle that reads as isosceles would let the
  viewer explain the result away as symmetry, which is exactly the wrong
  intuition.

---

## Part02_Trisect — the construction (~5-13s)

**Beat 2 — trisecting one vertex**
- *On screen:* the triangle from Part 1.
- *What changes:* at vertex `A`, two rays grow from the vertex into the
  triangle, cutting its interior angle into three equal parts, and stopping at
  the opposite side. Then three small arc marks appear across the three
  sub-angles in HIGHLIGHT, saying "these are equal", and fade out again.
- *Timing:* 1s for the rays, 1s for the arcs, 1s hold, 0.5s fade, 0.5s beat.

**Beat 3 — the other two vertices**
- *What changes:* the same pair of rays grows from `B`, then from `C` — one
  vertex at a time, so the construction stays followable.
- *Timing:* 1s each with a 0.5s beat between, then 1.5s hold on the finished
  construction.

**Meaning-carrying details:**
- The trisectors are ACCENT_ALT and thin: a *secondary* tone. They are more
  important than the triangle (they're being built now) but less important than
  what they produce (which gets ACCENT in Part 3). The three-tone hierarchy is
  how the eye knows where the argument is going.
- The arc marks appear at exactly one vertex and then leave. They exist to
  define the word "trisect" once; repeating them at all three vertices would
  clutter the frame with something already understood.
- Trisectors, not bisectors. Angle *bisectors* meet at the incenter and are the
  thing most viewers expect; the trisection is what makes the result strange.

---

## Part03_Reveal — the claim (~13-20s)

**Beat 4 — the three points**
- *On screen:* the full trisector construction.
- *What changes:* three ACCENT dots pop in, at the points where the trisectors
  **adjacent to each side** cross — the trisector from `B` nearest side `BC`
  meets the one from `C` nearest side `BC` at one point, and likewise for `CA`
  and `AB`.
- *Timing:* 1s, the three together, then a 0.5s beat.

**Beat 5 — the inner triangle**
- *What changes:* the three dots are connected into a triangle, drawn in ACCENT
  at full weight. A single equal-length tick mark appears at the midpoint of
  each of its three sides.
- *Timing:* 1s to draw, 1s for the ticks, 0.5s to read them before the
  caption lands on top of them.

**Beat 6 — the name**
- *What changes:* the caption `always equilateral` fades in below the figure, in
  real LaTeX, in ACCENT.
- *Timing:* 1s in, 2s hold.

**Meaning-carrying details:**
- **The tick marks are the argument, not decoration.** Without them the viewer
  is asked to trust that the inner triangle *looks* equilateral. One tick per
  side is the standard notation for "these three lengths are equal", and it
  turns an impression into a claim.
- The inner triangle is the first and only ACCENT object in the video. The
  color change *is* the handoff: scaffolding (MUTED) built construction lines
  (ACCENT_ALT) which produced the subject (ACCENT).
- "Adjacent to each side" is load-bearing. The other pairings of trisectors
  also meet, at points that form no equilateral triangle at all. If the code
  picks the wrong pair, the video is simply false.

---

## Part04_Miracle — the payoff (~20-30s)

**Beat 7 — bend the triangle**
- *On screen:* the complete figure from Part 3.
- *What changes:* vertex `A` travels along a slow closed arc while `B` and `C`
  stay put, so the outer triangle continuously deforms — its angles sweep from
  81°/61°/37° to an obtuse 96°/31°/53°. Every other thing on screen
  recomputes from that one motion: the trisectors re-aim, the three
  intersection points slide, the inner triangle moves and changes size — and
  stays visibly equilateral, ticks and all, for every frame of it.
- *Timing:* 8s, linear. Slow enough to actually watch the inner triangle and
  check that it never distorts.

**Beat 8 — the final frame**
- *What changes:* the motion stops on a triangle clearly different from the one
  it started with. Everything holds.
- *Timing:* 2s hold.

**Meaning-carrying details:**
- **Invariance under deformation is the proof-feel.** A static picture could be
  a coincidence of one triangle; a moving one that never breaks cannot be. This
  beat is the reason the video exists.
- **Everything is driven by one `ValueTracker`.** The trisectors, the three
  intersection points, the inner triangle and its ticks are all recomputed from
  the same value each frame, so they are in sync *by construction*. If they
  were animated separately, the inner triangle would be a drawing of the claim
  rather than a consequence of it — and the video would prove nothing.
- The path stays well away from degenerate triangles (its smallest angle never
  drops below 30°), because a near-flat triangle collapses the inner one to a
  speck and the invariance stops being visible.
- It ends on a *different* triangle than it started on, not back at the start.
  Returning home would let the viewer suspect a loop; ending elsewhere makes
  the point that the claim held all the way across.
- The endpoint is also chosen to be plainly **scalene**. Further along, the
  path passes through a near-isosceles shape; stopping there would have handed
  the viewer the "it's just symmetry" explanation that Part 1 exists to rule
  out, on the video's very last frame.
