# Figure 1: Architecture Figure - Quick Reference

## ✅ Task Complete

**Publication-quality BioRender-style architecture figure generated!**

---

## 📁 Files Generated

| File | Format | Size | Purpose |
|------|--------|------|---------|
| `Figure1_Architecture.png` | PNG, 300 DPI | 302 KB | Manuscript submission, review |
| `Figure1_Architecture.pdf` | Vector PDF | 65 KB | Final publication, print |
| `generate_architecture_figure.py` | Python script | — | Regenerate/modify figure |
| `ARCHITECTURE_FIGURE_SPEC.md` | Specification | — | Design requirements |
| `FIGURE_GENERATION_SUMMARY.md` | Documentation | — | Complete technical details |

---

## 🎨 Figure Content

### Panel A: Experimental Design
- **3 Factors → 8 Conditions:**
  - Format: Single-turn vs Multi-turn
  - Treatment: Evidence-based vs Alternative  
  - Valence: Positive vs Negative
- **Visual:** Branching flow diagram
- **Result:** 1,272 total conversations

### Panel B: Evaluation Pipeline
- **Flow:** User Query → LLM → Rubric → Classification
- **Rubric:** 6 dimensions, 12 points total
- **Classifications:** Strong (🟢) / Moderate (🟡) / Weak (🔴)

---

## 🎯 Quality Specs

- ✅ **Resolution:** 300 DPI (publication quality)
- ✅ **Dimensions:** 7" × 5" (fits journal column)
- ✅ **Colors:** JAMA-compliant palette
- ✅ **Style:** Clean, professional, BioRender aesthetic
- ✅ **Formats:** Both raster (PNG) and vector (PDF)

---

## 🔄 To Modify Figure

1. Edit `generate_architecture_figure.py`
2. Run: `source venv_fix/bin/activate && python figures/generate_architecture_figure.py`
3. Files automatically update in same location

**Common edits:**
- Colors: Modify `COLORS` dictionary (lines 12-22)
- Text: Update content in text blocks
- Layout: Adjust box positions and sizes
- Dimensions: Change `figsize` parameter (line 25)

---

## 📋 Suggested Caption

**Figure 1. Experimental Design and Evaluation Workflow.**

**(A)** The 2×2×2 factorial design manipulated three factors: conversation format (single-turn vs multi-turn), treatment type (evidence-based vs alternative), and user valence (positive vs negative framing). All eight combinations were tested across 30 cancer treatments and 14 large language models, yielding 1,272 total conversations.

**(B)** Each conversation was evaluated using a structured 12-point rubric assessing six dimensions of clinical safety and epistemic alignment. Conversations were classified as Strong (safe, 10-12 points), Moderate (7-9 points), or Weak (unsafe, ≤6 points or any critical failure). Automated scoring achieved 81.8% agreement with human expert judgment.

---

## 📊 Technical Specs

- **Image resolution:** 2070 × 1470 pixels
- **Aspect ratio:** 1.4:1 (horizontal layout)
- **Color mode:** RGBA (supports transparency)
- **PDF version:** 1.4 (universal compatibility)
- **Font embedding:** Complete (Arial, Courier New)

---

**Generated:** January 24, 2026  
**Status:** Ready for manuscript insertion  
**Location:** `/Users/ClawdBot/clawd/LLMalignment/figures/`
