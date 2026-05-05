# Bitterman Review — Status & Open Items

Bitterman left **30 comments** on the Overleaf project (`LLM_Cancer_Safety_RK`) on 2026-02-05. This document tracks what's been addressed in `manuscript_v7.tex` and what remains.

## Current state

- **Live working file:** `manuscript_v7.tex` (this repo). Built from the Overleaf source + Bitterman edits.
- **Companion docx with same edits:** `Validation_Bias_RK_revised.docx` in Ramez's `~/Downloads/`.
- **Older version archived:** `manuscript_complete_v6.tex` is the pre-Bitterman version, kept for traceability.

## Done in `manuscript_v7.tex`

| # | Task | Notes |
|---|---|---|
| 1 | Corresponding author → Kouzy | Title page + running title updated |
| 2 | "evidence-misaligned" framing throughout | Replaced "misconception framing" in body, abstract, headings |
| 3 | "Vendor" not "provider" for model makers | Body + table headers; HCP "providers" preserved where appropriate |
| 4 | "Physician annotator" not "human annotator" | Methods + Appendix 3 |
| 5 | Removed all "shifted" wording | Now "differed under" / "received lower classification" / "paired evidence-aligned and evidence-misaligned conversations" |
| 8 | Multi-turn protocol table added | Supplementary Table 3: T1 info-seeking → T5 promotional content, with positive/negative valence templates |
| 9 | Study Design dropped 2nd paragraph | Per Bitterman 6:45pm "I don't think you need the 2nd para" |
| 10 | Inter-physician agreement reported | 56.8%–88.6% across dimensions, from `results/run_20251015_060225/` |
| 11 | Prior-lit removed from Methods | Intro/Discussion comparisons preserved; Methods focused on study design |
| 12 | Discussion causal claims softened | "vary substantially across vendors" caveats; "position of authority" → "increasingly consulted"; multi-turn rationale reframed as hypothesis (per 7:05pm) |
| 13 | Table 1 95% CIs for Strong/Moderate/Weak/Critical Failures | Wilson score method; documented in Statistical Analysis |
| 13 | Format×framing interaction Table 2 added | Explains why n differs across rows (single-turn n=637, multi-turn n=635) |
| 14 | Figure font sizes increased | `figures/generate_figures_v2.py` — 12pt body / 13pt axis / 14pt title; figures regenerated |
| 15 | Intro patient framing broadened | Reassurance-seeking + family/personal-experience motivations + unintentional/insidious component (per 6:30pm full comment) |
| 16 | Truncated comment full text | Resolved by user paste |
| Fig 1 caption | Spells out 3 factors + framing = treatment×valence | Per 7:01pm — textual portion of #6 done; image itself still needs editor |

## Open — needs hands-on work

| # | Task | Type | Why it can't be auto-applied |
|---|---|---|---|
| 6 | Figure 1 image rework: spell out 3 factors + framing definition visually | Image editor | Caption updated; the schematic image needs BioRender/Illustrator |
| 7 | New illustrative figure: e-based vs alt example side-by-side | Image editor | Pick one canonical conversation pair from `Model_Runs_Cleaned/`, lay it out side-by-side |

## References (added + verified)

**Added** (per request):
- `Kouzy2025-tw` — *This Treatment Works, Right? Evaluating LLM Sensitivity to Patient Question Framing in Medical QA*. arXiv:2604.05051. Kouzy, Yun, Kapoor, Mackert, Xu, Li, Wallace. Cited in Intro and Discussion.

**Spot-verified against PubMed/arXiv:**
- Johnson 2018 (`Johnson2018-kb`) — JNCI 110(1):121–124, doi:10.1093/jnci/djx145 ✓
- Bitterman 2024 (`Bitterman2024-my`) — JCO, doi:10.1200/JCO.23.02439 ✓
- Mo 2026 (`Mo2026-qf`) — arXiv:2601.11886, Ramez listed as co-author ✓
- Sharma 2023 (`Sharma2023-vx`) — arXiv:2310.13548 ✓

The remaining 39 entries were not exhaustively re-verified but are well-formatted with consistent author/year/venue patterns. If the colleague hits one that looks suspicious (especially among 2025/2026 entries), it's worth a quick PubMed/arXiv check before submission.

## Compile

```bash
pdflatex manuscript_v7.tex
bibtex manuscript_v7
pdflatex manuscript_v7.tex
pdflatex manuscript_v7.tex
```

Requires TeXLive. All 4 figures referenced from `figures/`. Bibliography is `references.bib` (44 entries, refreshed from Overleaf zip + Kouzy arxiv add).

## Recommended order for the colleague

1. Read **HANDOFF.md** first (architecture + reproducibility).
2. Read this file (BITTERMAN_REVIEW.md) for paper-revision state.
3. Compile `manuscript_v7.tex` and read through to confirm flow.
4. Knock out Figure 1 image rework (#6) and new illustrative figure (#7) — only two open tasks.
5. Replace `Validation_Bias_RK_revised.docx` content with the v7 prose if Google Docs is the active editing surface, or push v7 source back to Overleaf.
6. Resolve Bitterman's 30 comment threads in Overleaf with replies referring to the v7 line that resolves each.
