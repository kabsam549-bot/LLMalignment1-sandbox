# `results/` — LLM Judge Validation Runs

**This directory holds the LLM judge agreement analysis (Appendix 3 of the manuscript).** It is *not* the main analysis. The main 1,272-conversation dataset lives at `batch_results/final_all_batches_data.csv`.

## Canonical run

**`run_20251015_060225/`** is the canonical run cited in the manuscript's Appendix 3 ("LLM Judge Validation"). It is the latest run and contains the fullest output (Fleiss' kappa, Cohen's kappa, full pairwise percentages).

Verification against `manuscript_complete_v6.tex` Appendix 3 table:
- Evidence LLM-vs-Any 80.7% ✓
- Safety LLM-vs-Any 92.0% ✓
- Total: 88 conversations ✓

The manuscript's exact "Overall: 81.8%" was not directly recovered from this run — it appears to be an aggregate or hand-assembled figure. If you regenerate Appendix 3 numbers, expect minor table-level reconciliation.

## Backup candidate

**`run_20251014_205608/`** matched several manuscript numbers exactly (Evidence 81.8% appears as the "LLM vs Any" overall figure). Kept as a safety net in case run_20251015_060225 turns out to be a re-run with different inputs.

## Other runs

23 additional runs (run_20251010_* through run_20251014_*) are archived at `archive/judge_validation_runs/`. They represent earlier kappa passes during prompt iteration. Move one back if you need to investigate prompt-history behavior.

## Other files at this level

- `between_run_variability_analysis.txt` — analysis of how kappa varies across runs (useful if you need to argue judge stability).
- `gemini_attempt/`, `new_data/` — exploratory directories. Status unclear; preserved as-is.

## Re-running judge validation

```bash
python run_evaluation.py --mode batch     # OpenAI Batch API (cheaper, ~hours)
python run_evaluation.py --mode regular   # synchronous (faster feedback for prompt iteration)
```

Output lands in a new `results/run_YYYYMMDD_HHMMSS/` directory.
