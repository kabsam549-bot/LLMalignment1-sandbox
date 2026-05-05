# Architecture Figure Generation Prompt

## For AI Image Generation (Gemini/DALL-E/Midjourney)

### Prompt v1 (Detailed)

```
Create a clean, professional scientific figure for a medical journal showing an experimental study design. The figure should have TWO PANELS arranged vertically:

PANEL A (TOP) - "Experimental Design: 2×2×2 Factorial"
Show a 3D cube or branching tree diagram with 3 factors:
- Factor 1 (X-axis): "Format" with levels "Single-turn" and "Multi-turn"  
- Factor 2 (Y-axis): "Treatment Type" with levels "Evidence-based" (green) and "Alternative" (red)
- Factor 3 (Z-axis): "Valence" with levels "Positive" and "Negative"
The 8 corners/endpoints represent the 8 experimental conditions.
Use clean geometric shapes, minimal design, muted scientific color palette.

PANEL B (BOTTOM) - "Evaluation Pipeline"
Show a horizontal flow diagram with arrows:
[User Query] → [14 LLMs] → [6-Dimension Safety Rubric] → [Classification]

The Classification box should show three outcomes:
- "Strong" (green, checkmark)
- "Moderate" (yellow/orange)  
- "Weak/Unsafe" (red, warning symbol)

Style: BioRender or Nature-style scientific illustration. White background. Sans-serif fonts (Arial/Helvetica). Clean lines, no gradients or 3D effects except for the cube. Professional, publication-ready.
```

### Prompt v2 (Simplified)

```
Scientific figure for medical journal. Two-panel layout:

TOP PANEL: 3D cube showing 2×2×2 study design with three factors (Format, Treatment Type, Valence). Eight conditions at cube corners. Clean geometric style.

BOTTOM PANEL: Horizontal flowchart: "User Query" → "14 LLMs" → "Safety Rubric (6 dimensions)" → Classification outputs (Strong=green, Moderate=yellow, Weak=red).

Style: BioRender, Nature journal, white background, sans-serif fonts, minimal professional design.
```

### Prompt v3 (For Gemini Imagen)

```
Create a two-panel scientific diagram:

Panel A shows a 2x2x2 factorial experimental design as a cube with labeled axes: Format (single vs multi-turn), Treatment (evidence-based vs alternative), and Valence (positive vs negative).

Panel B shows an evaluation flowchart: user query flows to 14 LLM models, then to a 6-dimension rubric, then to classification (Strong/Moderate/Weak with traffic light colors).

Professional medical journal style, clean white background, vector-like graphics.
```

---

## Key Visual Elements Needed

1. **The Cube (Panel A)**
   - 3D isometric cube
   - 3 labeled axes
   - 8 labeled corners or condition boxes
   - Color coding: green = safe/evidence, red = risky/alternative

2. **The Pipeline (Panel B)**
   - Left: Chat bubble icon with "User Query"
   - Arrow pointing right
   - Center: Stack of model icons or box saying "14 LLMs"
   - Arrow pointing right  
   - Center-right: Checklist icon with "6-Dimension Rubric"
   - Arrow pointing right
   - Right: Three boxes stacked (Strong/Moderate/Weak) with traffic light colors

3. **Overall Style**
   - White/light gray background
   - Thin black or dark gray lines
   - Sans-serif typography
   - No decorative elements
   - High contrast for print

---

## Figure Caption (for manuscript)

**Figure 1. Experimental Design and Evaluation Pipeline.** 
(A) The 2×2×2 factorial design varied conversation format (single-turn vs multi-turn), treatment type (evidence-based vs unproven/alternative), and user framing valence (positive vs negative), yielding 8 experimental conditions. 
(B) Each conversation was processed through 14 large language models and evaluated using a 6-dimension safety rubric, resulting in classification as Strong (safe), Moderate, or Weak (unsafe).
