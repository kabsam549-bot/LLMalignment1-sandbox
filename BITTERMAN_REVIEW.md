# Bitterman Review — Status & Open Items

Bitterman left **30 comments** on the Overleaf project (`LLM_Cancer_Safety_RK`) on 2026-02-05. This document tracks what's been addressed in `manuscript_v7.tex` and what remains.

## Current state

- **Live working file:** `manuscript_v7.tex` (this repo). Built from the Overleaf source + Bitterman edits.
- **Companion docx with same edits:** the colleague has it as `Validation_Bias_RK_revised.docx` (out-of-tree, in Ramez's Downloads).
- **Older version archived:** `manuscript_complete_v6.tex` is the pre-Bitterman version, kept for traceability.

## Done in `manuscript_v7.tex`

| # | Task | Notes |
|---|---|---|
| 1 | Corresponding author → Kouzy | Title page + running title updated |
| 2 | "evidence-misaligned" framing throughout | 16 instances; replaced "misconception framing" |
| 3 | "Vendor" not "provider" for model makers | 5× vendor; HCP "providers" preserved where appropriate |
| 4 | "Physician annotator" not "human annotator" | Methods + Appendix 3 |
| 5 | Removed all "shifted" wording | Was confusing — now "differed under" / "received lower classification" |
| 10 | Inter-physician agreement reported | 56.8%–88.6% across dimensions, from `results/run_20251015_060225/` |
| 12 | Discussion causal claims softened | "vary substantially across vendors" caveats; "position of authority" → "increasingly consulted" |
| 15 | Intro patient framing broadened | Now includes reassurance-seeking and family/personal-experience motivations |

## Open — needs hands-on work

| # | Task | Type | Blocker |
|---|---|---|---|
| 6 | Figure 1 rework: spell out 3 factors + framing = treatment×valence | Image editor | None — start in BioRender/Illustrator |
| 7 | New illustrative figure: e-based vs alt example side-by-side | Image editor | None — pick canonical pair from dataset |
| 8 | Turn-topics table (T1–T5) | Table content | Extract from prompt set |
| 9 | Methods → Study Design restructure | Prose | Full text of Bitterman 6:45pm comment (truncated) |
| 11 | Move misconception context Methods → Intro / prior-lit → Discussion | Prose | Identify which paragraph the comment was pinned to |
| 13 | Tables: 95% CI methodology, n footnote, formatting | Stats + table | Document Wilson interval; add n column footnote (matched-pair n=569 vs total n=1272) |
| 14 | Figure polish: x-axis 100%, larger text, missing data | Image editor | Multiple figures |
| 16 | Get full text of 6 truncated comments | Trivial | Click "show more" in Overleaf, screenshot |

## Truncated comments blocking 5 of the open tasks

- 6:30pm "...This can also be framed in a bit..." (was Intro broadening — partially handled)
- 6:45pm "...repetitive wi..." (Study Design restructure)
- 6:51pm "...the therapy is e-..." (Discussion causal-claim softening — partially handled)
- 6:54pm "...Perhaps bette..." (shift-wording final pass)
- 7:05pm "...We also didn't do expts to be able..." (Discussion overgeneralization)
- 7:11pm "...The text for the mean..." (Figure A polish)

## Compile

```bash
pdflatex manuscript_v7.tex
bibtex manuscript_v7
pdflatex manuscript_v7.tex
pdflatex manuscript_v7.tex
```

Requires TeXLive. All 4 figures referenced from `figures/`. Bibliography is `references.bib` (refreshed from Overleaf zip).

## Recommended order for the colleague

1. Read **HANDOFF.md** first (architecture + reproducibility).
2. Read this file (BITTERMAN_REVIEW.md) for paper-revision state.
3. Get truncated comments unblocked (#16) — one quick Overleaf trip, unlocks 5 other tasks.
4. Knock out figure work (#6, #7, #14) and turn-topics table (#8) — these don't need Bitterman context.
5. Apply remaining prose changes (#9, #11, partial #5/#12) once #16 is done.
6. Re-export to Overleaf, resolve all comment threads with replies referring to the line in `manuscript_v7.tex` that resolves them.
