# Figures & Tables Documentation (V2)
## JAMA Oncology Submission: Stress Testing Large Language Models for Medical Safety

**Generated:** 2026-01-24  
**Author:** Claude (Subagent)  
**Status:** Publication-ready

---

## Overview

This document describes the redesigned figures and tables for the manuscript. All visuals follow JAMA Oncology style guidelines:

- **Colors:** Muted, clinical palette (teal, amber, muted red)
- **Typography:** Arial/sans-serif, 10-12pt
- **Resolution:** 300 DPI (print-ready)
- **Format:** PNG + PDF (vector)
- **Style:** Minimal chartjunk, no 3D effects, no gradients

### Design Principles Applied:
1. **Consistency:** Same color palette across all figures
2. **Clarity:** Panel labels (A, B, C), clear legends, statistical annotations
3. **Clinical relevance:** Effect sizes, confidence intervals, OR values
4. **Terminology:** "Misconception" instead of "Misinformation" per FEEDBACK.md

---

## Figure Files

### Main Figures

| File | Description | Panels |
|------|-------------|--------|
| `Figure1_SycophancyEffect.png/pdf` | Primary finding: The sycophancy effect | A: Bar chart, B: Distribution |
| `Figure2_MultiTurnProtection.png/pdf` | Protective effect of multi-turn format | A: Interaction plot, B: Reduction bars |
| `Figure3_ModelPerformance.png/pdf` | Model heterogeneity analysis | A: Forest plot, B: Provider summary |
| `Figure4_SafetyErosion.png/pdf` | Classification transitions & dimensions | A: Transition bars, B: Dimension comparison |

### Supplementary Figures

| File | Description |
|------|-------------|
| `FigureS1_TreatmentValence.png/pdf` | Treatment × Valence interaction (crossover effect) |

---

## Figure Captions (Copy-ready for manuscript)

### Figure 1. The Sycophancy Effect in LLM Cancer Treatment Responses

**Panel A** shows unsafe response rates by framing condition. When queries were framed with patient misconceptions (promoting unproven treatments or attacking evidence-based treatments), models exhibited significantly higher rates of unsafe responses (14.4% vs 5.1%; OR, 3.13; 95% CI, 2.05–4.79; P < .001). Error bars represent 95% Wilson score confidence intervals.

**Panel B** shows the distribution of safety classifications across framing conditions. Under misconception framing, the proportion of Strong (safe) classifications decreased from 75% to 69%, while Weak (unsafe) classifications increased from 5% to 15%.

---

### Figure 2. Protective Effect of Multi-Turn Conversations

**Panel A** shows the interaction between conversation format and framing condition on unsafe response rates. Multi-turn conversations (dashed line) maintained lower unsafe rates across both framing conditions compared to single-turn exchanges (solid line). The protective effect of multi-turn format was consistent regardless of whether users expressed misconceptions (8.1% vs 21.2%) or neutral queries (2.2% vs 8.2%). Error bars represent 95% confidence intervals.

**Panel B** quantifies the absolute and relative risk reduction achieved by multi-turn format. Multi-turn conversations reduced unsafe response rates by 73% under neutral framing and 62% under misconception framing, suggesting that extended dialogue provides substantial protection against sycophantic validation of patient beliefs.

---

### Figure 3. Model Performance Heterogeneity

**Panel A** presents a forest plot of unsafe response rates for all 14 evaluated models, sorted from lowest to highest risk. The vertical dashed line indicates the overall mean (9.8%). Top performers (Claude 3.7 Sonnet, Gemini 1.5 Flash, O3 Mini) achieved unsafe rates below 1%, while smaller open-source models (DeepSeek R1 Distill, Gemma 3 4B) exceeded 35%.

**Panel B** aggregates performance by provider. Anthropic models achieved the lowest unsafe rate (1.8%; n = 227), followed by OpenAI (8.6%; n = 359) and Google (10.2%; n = 501). Meta (16.9%), Alibaba (17.2%), and DeepSeek (36.8%) showed substantially higher risk. Error bars represent 95% Wilson score confidence intervals; sample sizes shown in parentheses.

---

### Figure 4. Safety Erosion and Dimension-Level Analysis

**Panel A** shows classification transitions in paired conversations when the same scenario shifted from neutral to misconception framing. Among 429 conversations that started as Strong under neutral framing, 22.6% degraded (12.6% to Moderate, 10.0% to Weak) when presented with misconception framing. Numbers above bars indicate raw counts.

**Panel B** compares rubric dimension performance between framing conditions. Promotional Content Response showed the largest degradation (91% → 81% of maximum), followed by Evidence Accuracy (93% → 89%). Safety Guidance remained relatively stable, suggesting models maintained explicit safety warnings even when other dimensions degraded.

---

### Supplementary Figure 1. Treatment × Valence Interaction

This figure illustrates the conceptual crossover that underlies the sycophancy effect. Positive valence (promoting treatments) increased unsafe rates for unproven/alternative treatments, while negative valence (questioning treatments) increased unsafe rates for evidence-based treatments. Both patterns represent the same underlying phenomenon: models validating user beliefs regardless of medical evidence. Annotations highlight the bidirectional nature of this validation bias.

---

## Table Files

### LaTeX Tables

All tables are provided in `tables/tables_latex_v2.tex` with:
- JAMA-compliant formatting (booktabs style)
- No vertical lines
- Proper footnote symbols
- Abbreviation definitions
- Copy-ready captions

### Table Descriptions

| Table | Title | Key Content |
|-------|-------|-------------|
| Table 1 | Study Design | 2×2×2 factorial design explanation |
| Table 2 | Primary Outcomes | Sycophancy effect with OR and CIs |
| Table 3 | Format Interaction | Multi-turn protective effect breakdown |
| Table 4 | Model Performance | Provider-level unsafe rates |
| Table 5 | Rubric Dimensions | Dimension-level score comparison |
| Table 6 | Safety Erosion | Classification transition matrix |

---

## Color Palette Reference

```
JAMA Clinical Palette:
- Neutral (baseline):    #4A7C94 (Steel Blue)
- Misconception (risk):  #C84C4C (Muted Red)
- Single-turn:          #7BA3B8 (Light Steel Blue)
- Multi-turn:           #2D5A6B (Dark Teal)
- Strong (safe):        #3D7A5C (Forest Green)
- Moderate (caution):   #D4A84C (Amber)
- Weak (unsafe):        #B84C4C (Muted Red)

Provider Colors:
- Anthropic:  #2D5A6B
- Google:     #4A7C94
- OpenAI:     #7BA3B8
- Meta:       #D4A84C
- DeepSeek:   #B84C4C
- Alibaba:    #8B6B4C
```

---

## Regeneration Instructions

To regenerate all figures:

```bash
cd LLMalignment
source venv_fix/bin/activate
python figures/generate_figures_v2.py
```

Required packages: matplotlib, seaborn, pandas, numpy, scipy

---

## Changes from V1

1. **Terminology:** "Misinformation" → "Misconception" (per FEEDBACK.md)
2. **Color scheme:** Bright red/gray → Muted clinical palette
3. **Panel labels:** Added A, B, C lettering
4. **Statistical annotations:** Added OR, CI, P values directly on figures
5. **Error bars:** Added 95% Wilson score CIs to all bar charts
6. **Model names:** Cleaned and standardized display names
7. **Figure 2:** Replaced Sankey diagram with clearer interaction plot
8. **Figure 3:** Added forest plot for individual models
9. **Figure 4:** New safety erosion transition analysis
10. **PDF export:** Added vector format for print production

---

## Checklist for Submission

- [x] All figures at 300 DPI
- [x] PDF versions for vector graphics
- [x] Panel labels (A, B, C) consistent
- [x] Color palette accessible (checked contrast)
- [x] Statistical annotations present
- [x] Terminology matches FEEDBACK.md guidelines
- [x] LaTeX tables use booktabs formatting
- [x] Captions written and copy-ready
- [x] Abbreviations defined in table footnotes

---

*Documentation generated by figure-redesign subagent, 2026-01-24*
