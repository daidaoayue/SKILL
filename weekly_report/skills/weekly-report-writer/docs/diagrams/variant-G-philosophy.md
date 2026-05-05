# Variant G · Design Philosophy: "Studio Friday Evening"

A design philosophy for visualizing the weekly-report-writer workflow.

## Manifesto

The PhD's Friday evening is not a sprint. It is a deceleration. The lab has emptied; the printer has cooled; the only sound is the ventilation. **What this skill replaces is not work — it is the dread of staring at fifty file changes and not knowing where to start the report.** A good visualization of this skill should feel like that quiet evening: the moment when the chaos of the week has just begun to settle into a shape you can describe.

The composition reads top to bottom — the way a person reviews their week. Each band is a horizontal register, like the strata of a sediment sample, each one representing one phase. **Spatial generosity is not waste; it is breath.** The diagram is mostly empty. The eye must travel between phases, and the travel itself communicates the small mental shifts the user makes: from automation (scan) to introspection (interview) to delivery (report).

Color is rationed to four hues. A deep ink — the structural element, the rules, the connective lines. A warm graphite — for secondary modules, the things that work behind the scenes. A single accent of muted ember — reserved exclusively for the deliverables, the two artifacts that leave the system: the markdown report and the PDF. **The eye, scanning, knows instantly where the value lands.** A paper-cream ground holds everything at a temperature warmer than office daylight.

Typography is dual-grammar. A humanist serif for headings — the moments where the reader is supposed to slow down. A monospaced engineering face — JetBrains Mono — for paths, scripts, identifiers; the parts that the operator needs to find precisely. Chinese characters in Microsoft YaHei at restrained size, never competing with the Latin grid but conversing alongside it. **Every kerning decision is a quiet act of respect.**

Hierarchy emerges through scale and silence, not decoration. The pipeline at the top occupies the full width because it is the only thing the reader needs to see if they read nothing else. The architecture below is set in finer type, because it is for the engineer. The footer ledger — Init time, Weekly time, Tests, License — is the smallest type, but the most important, because those four numbers are what you would tell another PhD over coffee. **The page is also a calling card.**

What the diagram refuses to do: bright colors competing for attention; gradients pretending to be depth; arrows that loop just to prove the system is "alive"; cute icons that turn an engineering tool into a children's app. **This skill solves a real problem for a serious user. The visualization should match that register.** Like a watchmaker's exploded view, every line is placed with the conviction of someone who has spent a lifetime measuring small things, and intends the work to remain legible for a decade.

## Visual Specification

- **Canvas**: A4 portrait, 210 × 297 mm, paper-cream ground (#F5F1E8)
- **Type**:
  - Display & headings: Source Serif 4 (or Charter / Iowan Old Style fallback)
  - Monospaced labels: JetBrains Mono
  - Chinese: Microsoft YaHei
- **Color palette** (four hues only):
  - Ink: #1A2332
  - Pencil: #6B6F76
  - Ember (deliverables only): #C4541C
  - Paper: #F5F1E8
- **Composition**: top-to-bottom, three registers — pipeline · architecture · ledger
- **Spacing**: line-height 1.55, generous margins (60 px / 48 px), no inner shadows
- **Lines**: structural elements 1.5 px solid; rules between registers 3 px double in ink
- **No**: drop shadows, gradients, decorative icons, bright fills

See `variant-G-render.py` for the matplotlib implementation that expresses this philosophy as a static .png.
