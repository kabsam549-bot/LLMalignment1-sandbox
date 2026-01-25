# Analysis Plan

## Analysis Plan for JAMA Oncology Manuscript

**Date:** January 2026

**Goal:** Expand analytical scope beyond critical failure rates to capture the full spectrum of safety degradation and identify dimension-level drivers.

---

## Priority 1: Classification Shift Analysis

**Rationale:** The current framing emphasizes critical failures (8.7%), but the more compelling story may be in the ~28% of conversations that aren't "Strong." We need to understand how conversations shift between classification levels when experimental factors change.

**Methods:**

- Paired comparisons: Same model + same treatment, flip ONE variable → track classification transitions
- Create transition matrices for each factor manipulation (e.g., positive → negative valence)
- Calculate: "When we switch from positive to negative valence for alternative treatments, X% of conversations shift from Moderate → Strong"

**Visualization:** Sankey diagrams showing classification flows between conditions

---

## Priority 2: Multinomial/Ordinal Logistic Regression

**Rationale:** Current logistic regression only models critical failure (binary). This misses the ordinal structure of Strong/Moderate/Weak.

**Methods:**

- Fit ordinal logistic regression with Strong/Moderate/Weak as ordered outcome
- Predictors: Format, Treatment Type, Valence, and interactions
- Report odds ratios for each classification transition (Moderate vs Strong, Weak vs Strong)

**Expected output:**

- "Single-turn increases odds of Moderate (vs Strong) by X, and odds of Weak (vs Strong) by Y"
- Compare effect sizes across classification boundaries

---

## Priority 3: Dimension-Level Decomposition

**Rationale:** When a conversation drops from Strong → Moderate, which rubric dimensions drove it? This identifies specific safety vulnerabilities.

**Methods:**

- Conditional analysis: Among Moderate-classified conversations, calculate mean dimension scores
- Compare dimension profiles across Strong/Moderate/Weak
- Identify which dimensions differentiate classifications
- Calculate dimension-specific effect sizes for each experimental factor

**Questions to answer:**

- Is Promotional Content Response the main driver of classification drops?
- Do HCP References and Evidence Accuracy show different vulnerability patterns?
- Which dimension shows the largest condition × classification interaction?

---

## Priority 4: Turn-Level Analysis (Multi-turn Only)

**Rationale:** At which turn (T1–T5) do safety failures emerge? If T5 (promotional request) accounts for most critical failures, that's a different intervention target than failures at T1.

**Methods:**

- Score each turn independently (where possible from rubric mapping)
- Track "safety maintenance" through conversation progression
- Identify the modal failure point

**Visualization:** Survival-curve-like plot of "safety maintained through turn X"

**Questions to answer:**

- Does T5 (promotional) account for >90% of critical failures?
- Do models that "pass" T1–T4 but fail T5 have a distinct profile?
- Is there cumulative degradation or sudden failure?

---

## Priority 5: Model Heterogeneity Analysis

**Rationale:** Do all models show the same sycophancy pattern, or is it driven by specific models? Important for generalizability claims.

**Methods:**

- Add Model × Condition interaction terms to regression models
- Fit mixed-effects model with model as random effect to separate condition effects from model effects
- Stratified analysis: Does the misinformation effect hold for top-5 vs bottom-5 models?

**Questions to answer:**

- Is sycophancy a universal LLM phenomenon or concentrated in certain architectures?
- Do small models show qualitatively different failure patterns?
- Are Google/Anthropic models systematically different from open-source?

---

## Secondary Analyses

### 6. Treatment-Level Variation

- Rank treatments by failure rate within each category
- Test whether politicized treatments (ivermectin) differ from obscure ones (cesium chloride)
- Identify if specific treatments are driving aggregate effects

### 7. Dimension Correlation Structure

- Calculate pairwise correlations between dimension scores
- Run PCA on dimension scores to identify latent "safety factors"
- Determine if dimensions are independent or clustered

### 8. Threshold Sensitivity Analysis

- Re-run analyses with Strong = 11–12 (instead of 10–12)
- Assess robustness of main findings to classification cutoffs
- Report range of effect sizes across reasonable thresholds

### 9. Number Needed to Harm (NNH) Framing

- Calculate NNH for each condition
- "For every X conversations in single-turn + alternative + positive, 1 results in critical failure"
- More intuitive for clinical audience than odds ratios

### 10. Qualitative Case Analysis

- Select exemplar conversations for each classification level
- Document "near misses" (scored 9 vs 10)
- Include representative examples in supplementary materials

---

## Implementation Notes

**Data requirements:**

- Dimension-level scores for all 1,275 conversations ✓
- Turn-level mapping to rubric dimensions (may need clarification)
- Model metadata (provider, size category, open-source status) ✓

**Statistical packages:**

- Ordinal regression: `statsmodels` or `mord` (Python)
- Mixed-effects: `statsmodels.mixedlm` or `pymer4`
- Sankey diagrams: `plotly` or `matplotlib-sankey`

**Timeline:** TBD

---

## Revised Paper Framing (Draft)

**Current framing:** "Critical failures occur in 8.7% of conversations; misinformation framing increases risk 4-fold."

**Proposed framing:** "Models don't dramatically fail—they quietly degrade. Under misinformation framing, X% of conversations shift from Strong to Moderate safety classification, primarily driven by weakened [Evidence Accuracy / Promotional Response / etc.]. Critical failures are the tip of the iceberg; the larger concern is the systematic softening of safety guidance affecting far more patient interactions."