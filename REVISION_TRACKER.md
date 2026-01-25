# Manuscript Revision Tracker
**Date:** 2026-01-24
**Feedback Source:** Email from Ramez Kouzy

## Completed Tasks ✅

### Abstract
- [x] Converted to IMRAD format (Intro/Methods/Results/Conclusions)
- [x] Changed "non-consensus views" → "non-evidence-based views"
- [x] Softened "increased mortality" → "worse outcomes"
- [x] Fixed sycophancy definition framing

### Introduction
- [x] Shortened to 4 paragraphs
- [x] Removed section 1.1 (Purpose of Study) - incorporated into intro
- [x] Ends with hypothesis
- [x] Added Mo et al. 2026 citation (Faithfulness vs Safety)
- [x] Changed bibliography style to `unsrt` (chronological by appearance)

### Methods
- [x] Fixed section 2.1 "prior literature" paragraph
- [x] Added note about multi-turn being more vulnerable in prior literature
- [x] Fixed threshold definitions: Weak = 0-5 (not 0-6), Moderate = 6-9 (not 7-9)

### Title Page
- [x] Reduced spacing between reference count and running title
- [x] Updated reference count to 36 (now 37 with JCOCCI)

### Data Analysis
- [x] Double-dipping investigation completed - no issue found
- [x] Report saved: WEAK_CLASSIFICATION_INVESTIGATION.md

---

## In Progress 🔄

### Sub-agent: Discussion Rewrite
- [ ] Section 4.1: Change "patients" → "users"
- [ ] Section 4.1: Soften symmetry sentence
- [ ] Section 4.2: Soften/remove strong last sentence
- [ ] Section 4.2: Shorten section
- [ ] Section 4.3: Expand (multi-turn protective is counterintuitive)
- [ ] Section 4.4: Reframe for model development
- [ ] Section 4.4: Add healthcare provider awareness point
- [ ] Section 4.4: Cite Kouzy JCOCCI paper (kouzy2025llmpatient)
- [ ] Section 4.5: Emphasize companies pushing into healthcare
- [ ] Section 4.5: Add point about institutions not evaluating prompting style
- [ ] Section 4.6: Note bulk responses were safe, but 20%+ unsafe is unacceptable
- [ ] Section 4.6: Expand limitations
- [ ] Section 4.6: End with "to our knowledge, first comprehensive evaluation"
- [ ] Conclusion: Soften first part, answer "so what" and "what's next"

### Sub-agent: Results Restructure
- [ ] Remove "six providers" reiteration
- [ ] Remove methods repetition throughout
- [ ] Make flow better (less disjointed)

### Sub-agent: Tables/Figures
- [ ] Table 1: DELETE (replace with architecture figure)
- [ ] Table 3: Convert to text (ARR only, not RRR)
- [ ] Table 4: Move to appendix
- [ ] Table 5: Move to appendix
- [ ] Figure 2 Panel B: Consider removing
- [ ] Figure 3: Move to appendix (Supplementary Figure 1)
- [ ] Figure 4A: Create Sankey diagram
- [ ] Figure 4B: Move to appendix (Supplementary Figure 2)
- [ ] NEW: Add example response figure (positive vs negative valence)

### Sub-agent: Architecture Figure
- [ ] Create BioRender-style figure specification
- [ ] Show 2×2×2 experimental design
- [ ] Flow: User query → LLM → Evaluation → Classification

### Sub-agent: Sankey Diagram
- [ ] Extract transition data from paired conversations
- [ ] Generate Plotly Sankey figure

---

## Clarifications Needed ❓

1. Email section 4.1 has garbled voice-to-text ("national observation... model that I understand is very popular...") - waiting for clarification

---

## References Added
- Mo et al. 2026 - Faithfulness vs Safety (arXiv)
- Kouzy et al. 2025 - Review of LLMs for Patient/Caregiver Support (JCO CCI, PMID 41213099)

---

## Files Modified
- manuscript_complete_v3.tex
- references.bib
- WEAK_CLASSIFICATION_INVESTIGATION.md
- MANUSCRIPT_CORRECTIONS_NEEDED.md
