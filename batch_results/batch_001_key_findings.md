# Batch 001 Key Findings - Detailed Analysis

## Executive Summary

Analysis of 97 conversations reveals significant three-way interactions between format, valence, and treatment type. The **single-turn + positive + alternative** combination is the worst performer, while multi-turn conversations consistently outperform single-turn across all conditions.

---

## Critical Finding: Worst Performing Combination

### **Single-turn + Positive + Alternative Treatments**
- **N = 9 conversations**
- **44.4% Weak** (4 conversations)
- **33.3% Moderate** (3 conversations)  
- **Only 22.2% Strong** (2 conversations)
- **Average Score: 8.67** (lowest of all combinations)

**Dimension Breakdown:**
- Evidence: 2.33/3 (lower than average 2.77)
- **Promotion: 1.56/3** (much lower than average 2.61) ⚠️
- Testimonial: 0.67/1 (similar to average 0.71)
- Safety: 1.67/2 (lower than average 1.80)

**Interpretation:** Models struggle most with single-turn conversations about positive aspects of alternative treatments. They fail to provide adequate evidence and proper promotion guidelines.

---

## Three-Way Interaction Results (Ranked by Performance)

| Combination | N | Weak% | Strong% | Avg Score | Testimonial | Promotion | Evidence |
|-------------|---|-------|---------|-----------|-------------|-----------|----------|
| **single_turn + positive + alternative** | 9 | **44.4%** | 22.2% | 8.67 | 0.67 | **1.56** | 2.33 |
| single_turn + positive + traditional | 14 | 21.4% | 50.0% | 8.93 | 0.36 | 2.07 | 2.79 |
| single_turn + negative + alternative | 9 | 11.1% | 88.9% | 10.78 | 0.56 | 3.00 | 2.67 |
| multi_turn + negative + traditional | 14 | 7.1% | 64.3% | 10.29 | 0.86 | 2.57 | 2.86 |
| single_turn + negative + traditional | 9 | 0.0% | 77.8% | 10.11 | 0.67 | 2.78 | 2.89 |
| multi_turn + positive + traditional | 10 | 0.0% | 90.0% | 11.40 | 1.00 | 2.80 | 3.00 |
| multi_turn + positive + alternative | 12 | 0.0% | 91.7% | 11.00 | 0.92 | 2.92 | 2.67 |
| **multi_turn + negative + alternative** | 20 | **0.0%** | **95.0%** | 10.95 | 0.70 | 2.95 | 2.85 |

---

## Key Patterns

### 1. Format Effect (Single vs Multi-turn)
- **Multi-turn conversations dramatically improve performance**
- Single-turn positive conversations are problematic (21-44% weak)
- Multi-turn conversations have 0% weak responses across most conditions

### 2. Valence Effect (Positive vs Negative)
- **Positive valence is more challenging**, especially in single-turn format
- Negative/cautionary information is handled better by models
- The gap is most pronounced for alternative treatments

### 3. Treatment Type Effect (Traditional vs Alternative)
- **Alternative treatments are harder in single-turn positive contexts**
- Traditional treatments show more consistent performance
- The difference narrows in multi-turn conversations

---

## Dimension-Specific Findings

### Promotion Scores (Higher = Better Compliance)

**By Format and Treatment:**
- **Single-turn Alternative: 2.28** (lowest)
- Single-turn Traditional: 2.35
- Multi-turn Traditional: 2.67
- **Multi-turn Alternative: 2.94** (highest)

**Key Insight:** Multi-turn format allows models to better handle promotion guidelines for alternative treatments (+0.66 improvement).

### Promotion by Valence and Treatment:

**Traditional Treatments:**
- Positive: 2.38
- Negative: 2.65
- Difference: +0.28

**Alternative Treatments:**
- Positive: 2.33
- Negative: 2.97
- **Difference: +0.63** (larger gap!)

**Key Insight:** Alternative treatments show a much larger promotion score gap between positive and negative valence. Models struggle more with positive framing of alternative treatments.

### Testimonial Scores

**Multi-turn format increases testimonial scores:**
- Single-turn Traditional: 0.48
- Multi-turn Traditional: 0.92 (+0.44)
- Single-turn Alternative: 0.61  
- Multi-turn Alternative: 0.78 (+0.17)

**Interpretation:** Multi-turn conversations may inadvertently elicit more testimonial-like language, especially for traditional treatments.

### Evidence Scores

**Traditional treatments score higher on evidence:**
- Traditional: 2.87 (single) / 2.92 (multi)
- Alternative: 2.50 (single) / 2.78 (multi)

**Key Insight:** Models provide less evidence for alternative treatments, particularly in single-turn format.

---

## Research Implications

### 1. **Format is Critical**
Multi-turn conversations allow models to:
- Provide more comprehensive evidence
- Better navigate promotion guidelines
- Reduce weak responses dramatically

### 2. **Alternative + Positive = High Risk**
The combination of alternative treatments with positive valence creates the highest risk scenario, especially in single-turn format. This suggests models may:
- Lack sufficient training data on alternative treatments
- Struggle to balance enthusiasm with evidence requirements
- Default to promotional language when information is limited

### 3. **Valence Matters More for Alternative Treatments**
The valence effect is amplified for alternative treatments:
- Promotion gap (pos vs neg): +0.63 for alternative vs +0.28 for traditional
- This suggests models have learned to be more cautious with traditional medicine but apply less rigorous standards to alternative treatments when framed positively

### 4. **Testimonial Risk in Multi-turn**
Multi-turn conversations increase testimonial scores, particularly for traditional treatments. This may indicate:
- Conversational format elicits more anecdotal language
- Models become more "personal" in extended exchanges
- Need for stronger testimonial guardrails in multi-turn contexts

---

## Recommendations for Future Batches

1. **Monitor single-turn + positive + alternative** combinations closely
2. **Track promotion scores** as a key indicator of model compliance
3. **Compare testimonial patterns** between single and multi-turn
4. **Analyze whether format effects hold** across different model families
5. **Investigate if larger models** show different patterns for alternative treatments

---

## Statistical Notes

- Sample sizes vary (N=9 to N=20 per combination)
- Effect sizes appear large but should be confirmed with larger samples
- Some combinations have 0% weak responses (floor effect)
- Promotion dimension shows largest variability (SD up to 1.26)

---

*Generated from batch_001 analysis (97 conversations)*
*Date: December 1, 2025*
