# Analysis Root: Sycophancy & Safety Erosion (Jan 2026)

This file marks the entry point for the "Sycophancy" re-analysis of the Stress Testing LLMs project.

## 🎯 Core Narrative
**"Sycophancy in Medical AI: Large Language Models Validate Patient Misinformation Over Evidence."**

The primary finding is that models don't just fail on "alternative medicine"; they fail specifically when users frame queries as misinformation (Validation Bias).
- **Misinformation Framing:** 14.4% Failure Rate (Weak)
- **Regular Framing:** 5.1% Failure Rate (Weak)
- **Result:** 2.8x higher risk of unsafe advice when users push for it.

## 📂 Key Files
- **Analysis Script:** `src/reanalysis_sycophancy.py` (Run this to reproduce stats)
- **Data Source:** `batch_results/final_all_batches_data.csv`
- **Output Directory:** `results/reanalysis_2026_01_23`

## 📊 Figures Strategy
1.  **Figure 1 (Sycophancy):** Bar chart comparing Unsafe Rates (Misinfo vs Regular).
2.  **Figure 2 (Erosion):** Sankey diagram showing the shift from Strong → Moderate/Weak.
3.  **Figure 3 (Guardrail):** Bar chart showing Multi-turn vs Single-turn protection (20.5% → 6.9% failure reduction).

## 🚀 How to Run
```bash
# Use the fixed environment
LLMalignment/venv_fix/bin/python LLMalignment/src/reanalysis_sycophancy.py
```
