# Handoff Notes

This document is the entry point for someone picking up the repo to push the paper through the finish line. Read this first. Everything else is supporting material.

---

## What this project is

Cross-sectional evaluation of **14 LLMs across 6 providers** on **1,272 oncology conversations**, testing whether models exhibit validation bias ("sycophancy") when users frame queries with misconceptions vs. evidence-aligned framing.

- **Design:** 2×2×2 factorial (framing × treatment type × format = single-turn vs multi-turn)
- **Primary outcome:** Unsafe response rate = "Weak" on a 6-dimension safety rubric, or any critical failure
- **Headline finding:** 14.4% unsafe under misconception framing vs 5.1% evidence-aligned (OR 3.13, 95% CI 2.05–4.79, P<.001). Provider unsafe rates range 1.8%–36.8%. Multi-turn reduces unsafe rate by 9.6pp absolute.
- **Target journal:** JAMA Oncology

---

## Live state of the manuscript

- **Live file:** `manuscript_v7.tex` — incorporates Bitterman's 2026-02-05 review of the Overleaf project. New title: *"Validation Bias in AI Cancer Counseling: A Cross-Sectional Study of Large Language Model Responses."* Kouzy is corresponding author. See **`BITTERMAN_REVIEW.md`** for what's done and what's open.
- **Predecessor in repo:** `manuscript_complete_v6.tex` — pre-Bitterman, "Sycophancy in Medical AI" framing. Kept for traceability. Don't edit.
- **Earlier versions** (`manuscript.tex`, `manuscript_v2.tex`, `manuscript_complete.tex`, `manuscript_complete_v3/v4/v5.tex`, `manuscript_final.tex`) are in `archive/manuscripts/`.
- **Active revision passes:** `REVISION_TRACKER.md` (older Ramez feedback against v6) and **`BITTERMAN_REVIEW.md`** (current — Bitterman's 30 comments, 8 done, 8 open in v7).
- **Submission status:** Drafting. JAMA Oncology target.

---

## The data architecture (most important section)

```
Model_Runs/                            14 LLMs × 1,272 prompts → raw responses
Model_Runs_Cleaned/                    Cleaned variant (KEEP BOTH — both are needed)
        │
        ▼ batch judge scoring (run_batch_*.py uses GPT-5-mini)
batch_results/final_all_batches_data.csv      ◀── THE MASTER DATASET (1,272 rows)
        │
        ▼
figures/generate_figures_v2.py         → Figures 1-4 + Supplementary
figures/generate_sankey.py             → Figure 4A (paired-conversation flow)
        │
        ▼
manuscript_complete_v6.tex             → final PDF
```

**`batch_results/final_all_batches_data.csv` is the canonical dataset.** Every figure regenerates from it. Treat it as immutable for the current paper. If you need to add a model or rescore, regenerate it and version the old one (don't overwrite in place).

### What `results/run_*` is (and isn't)

`results/` contains 28 timestamped runs. **These are *not* the main analysis** — they are LLM-judge-vs-human-annotator agreement runs (Fleiss/Cohen kappa) supporting the validation reported in **Appendix 3** of the manuscript. They use a small pilot subset, not the full 1,272.

**Canonical kappa run identified:** `results/run_20251015_060225/` — latest run, fullest output, matches manuscript Evidence (80.7%) and Safety (92.0%) numbers exactly. `run_20251014_205608/` kept as backup. The other 23 earlier runs are archived at `archive/judge_validation_runs/`. See `results/README.md` for details.

Caveat: the manuscript's exact "Overall: 81.8%" was not directly recoverable from any single run — appears hand-assembled across passes. Expect minor reconciliation if Appendix 3 needs re-derivation.

---

## Recipes

All commands assume you're in the repo root with the venv activated:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install plotly kaleido        # see Landmines #1
```

### Regenerate all figures from the master CSV

```bash
cd figures
python generate_figures_v2.py     # Figures 1, 2, 3, 4 (Safety Erosion), Supp Fig 1
python generate_sankey.py         # Figure 4A (Sankey)
```

Smoke-tested 2026-05-05: both scripts succeed. The Sankey output prints `Degradation from Strong: 22.6%`, which matches the manuscript abstract — a quick sanity check.

### Recompile the manuscript

```bash
pdflatex manuscript_v7.tex
bibtex manuscript_v7
pdflatex manuscript_v7.tex
pdflatex manuscript_v7.tex
```

Requires TeXLive (or MacTeX) installed locally. Bibliography is `references.bib`, style is `unsrt` (chronological by appearance — Ramez's choice).

### Add a new model to the evaluation

1. Run the new model against the prompt set → JSON in `Model_Runs/`.
2. Clean and add to `Model_Runs_Cleaned/` (see `src/data_cleaning.py`).
3. Run judge scoring: `python run_batch_pair.py` (or appropriate batch script) using the model's outputs as input.
4. Concatenate the new judge output rows into `batch_results/final_all_batches_data.csv`.
5. Regenerate figures.
6. Update `manuscript_complete_v6.tex` model count / Table 5 / provider counts.

### Re-validate the LLM judge against humans

Pipeline lives in `src/` (`llm_judge.py`, `analysis.py`) and `run_evaluation.py`. Inputs: `data/conversations.json` (pilot subset), `data/pilot_all_with_adjudicated_scores_with_text.csv` (human annotations), `data/Rubric.md`, `prompt.txt`. Output: a new `results/run_YYYYMMDD_HHMMSS/` directory with kappa metrics, confusion matrices, and an agreement summary.

```bash
python run_evaluation.py --mode batch     # use OpenAI batch API (cheaper, slower)
python run_evaluation.py --mode regular   # synchronous, for testing
```

---

## Open threads (from `REVISION_TRACKER.md`)

These are revisions Ramez asked for that may or may not be done in v6 — verify before assuming complete:

- **Discussion** sections 4.1–4.6: tone softening, "patients" → "users" in 4.1, expand 4.3 (multi-turn protective is counterintuitive), expand 4.6 limitations, add JCOCCI citation.
- **Tables:** Delete Table 1 (replace with architecture figure). Convert Table 3 to inline text (ARR only, drop RRR).
- **Results section:** Remove "six providers" reiteration, remove methods repetition, improve flow.
- **Investigations resolved:** Double-dipping concern (`WEAK_CLASSIFICATION_INVESTIGATION.md`) — no issue found.

---

## Landmines

1. **`requirements.txt` is incomplete.** Missing `plotly` and `kaleido` (needed for `generate_sankey.py`). Add them, or pip install manually before running.
2. **Figure 4 naming collision.** Three different files in `figures/` are named or referenced as "Figure 4": `Figure4A_Sankey.png` (canonical, used in v6 manuscript), `Figure4_ModelPerformance.png` (older), `Figure4_SafetyErosion.png` (output of `generate_figures_v2.py`'s "Figure 4: Safety Erosion"). The manuscript's "Figure 4" is the Sankey. The Safety Erosion plot is currently unused in v6. Don't get tricked.
3. **Figures regenerate non-identical to committed PNGs.** Smoke test on 2026-05-05 found `Figure2_MultiTurnProtection.png` and `Figure3_ModelPerformance.png` differ in bytes after regeneration but the data is unchanged. Almost certainly a matplotlib version drift, not a logic bug. If you regenerate, accept the new PNGs.
4. **Two model-run dirs exist by design.** `Model_Runs/` (raw) and `Model_Runs_Cleaned/` (post-cleaning). Both are needed — raw preserves provenance, cleaned is what the judge actually scored. Do not delete either.
5. **Many one-shot ops scripts at root.** Files like `check_batches_3_4_5.py`, `resume_batch_002.py`, `run_batches_6_through_13.py` are operational artifacts from the original batch runs. They were written for specific resumes and aren't reusable as-is. Treat as historical logs.
6. **Multiple figure-generation scripts.** `figures/generate_figures.py`, `generate_figures_v2.py`, `regenerate_figures.py`, `generate_figure1.py`, `generate_architecture_figure.py`. **`generate_figures_v2.py` is current.** The others are superseded.
7. **No CI, no tests.** Pipeline correctness is verified by spot-checking output numbers against the manuscript (e.g., "1272 conversations", "22.6% degradation").
8. **API key not committed.** Set `OPENAI_API_KEY` in `.env` (gitignored) before running judge scoring or batch jobs.

---

## What lives where (post-cleanup map — see CLEANUP.md if/when archive happens)

```
README.md                           Original eval-framework README (slightly out of date)
HANDOFF.md                          ← this file
REVISION_TRACKER.md                 Open manuscript edits (READ THIS)
MANUSCRIPT_PLAN.md                  Story / structure notes for v6 framing
manuscript_complete_v6.tex          Live manuscript
manuscript_complete_v6.pdf          Most recent compiled PDF
references.bib                      Bibliography
prompt.txt                          Judge prompt (edit this to change judge behavior)
requirements.txt                    Python deps (incomplete — see Landmines #1)
run_evaluation.py                   Entry point for judge validation pipeline
.env                                API keys (gitignored)

data/
  conversations.json                Pilot subset for judge validation
  pilot_all_with_adjudicated_scores_with_text.csv     Human annotations (gold)
  Rubric.md                         6-dimension scoring rubric

src/                                Core library
  config.py                         Model name, paths
  llm_judge.py                      Judge prompt + scoring call
  scorer.py                         Python rubric → score conversion
  batch_evaluator.py                OpenAI Batch API integration
  regular_evaluator.py              Synchronous (for testing)
  analysis.py                       Fleiss/Cohen kappa
  data_cleaning.py                  Model_Runs → Model_Runs_Cleaned
  shift_decomposition_analysis.py   Sankey-feeding analysis
  reanalysis_sycophancy.py          Sycophancy-specific reanalysis

scripts/                            Reusable utilities (some)
batch_results/                      Master dataset + per-batch dumps
  final_all_batches_data.csv        ★ MASTER DATASET ★
results/run_YYYYMMDD_HHMMSS/        Judge validation runs (kappa)
Model_Runs/                         Raw model outputs (KEEP)
Model_Runs_Cleaned/                 Cleaned model outputs (KEEP)
figures/                            Figure scripts + outputs
tables/                             Markdown table sources + LaTeX
archive/                            (planned) Drafts, superseded versions, one-shot scripts
```

---

## Contact

For questions about intent, framing, or unrecorded decisions: **Ramez Kouzy** (MD Anderson, Department of Radiation Oncology / Institute for Data Science in Oncology).

*Last updated: 2026-05-05*
