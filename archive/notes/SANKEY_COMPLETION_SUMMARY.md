# Sankey Diagram Creation - Task Completion Summary

**Task:** Create Sankey Diagram Data for Figure 4A  
**Date:** 2026-01-24  
**Status:** ✅ COMPLETE

## What Was Created

### 1. Data Extraction Script
**File:** `/Users/ClawdBot/clawd/LLMalignment/extract_sankey_data.py`

Extracts complete transition matrix from the batch results CSV:
- Analyzes 569 paired conversations
- Tracks all 9 possible transitions (Strong→Strong, Strong→Moderate, etc.)
- Outputs structured JSON data for Sankey diagram

**Output:** `figures/sankey_data.json`

### 2. Sankey Data File
**File:** `/Users/ClawdBot/clawd/LLMalignment/figures/sankey_data.json`

Complete transition data showing classification changes from Evidence-aligned → Misconception framing:

```json
{
  "Strong→Strong": 332 (77.4%),
  "Strong→Moderate": 54 (12.6%),
  "Strong→Weak": 43 (10.0%),
  "Moderate→Strong": 48 (43.6%),
  "Moderate→Moderate": 35 (31.8%),
  "Moderate→Weak": 27 (24.5%),
  "Weak→Strong": 13 (43.3%),
  "Weak→Moderate": 9 (30.0%),
  "Weak→Weak": 8 (26.7%)
}
```

### 3. Sankey Diagram Generator
**File:** `/Users/ClawdBot/clawd/LLMalignment/figures/generate_sankey.py`

Python script using Plotly to create publication-ready Sankey diagrams:
- Interactive HTML version
- High-resolution PNG (1800×1200px, 2x scale)
- Vector PDF for publication
- Custom color scheme (Green=Strong, Orange=Moderate, Red=Weak)
- Hover tooltips with percentages
- Annotation with key statistics

### 4. Generated Figures
**Location:** `/Users/ClawdBot/clawd/LLMalignment/figures/`

Three output formats:
- **Figure4A_Sankey.html** (4.6 MB) - Interactive, can be opened in browser
- **Figure4A_Sankey.png** (277 KB) - Publication-ready image
- **Figure4A_Sankey.pdf** (127 KB) - Vector format for LaTeX

### 5. Updated Root Script
**File:** `/Users/ClawdBot/clawd/LLMalignment/generate_sankey.py`

Updated the existing script to:
- Default to generating Figure 4A
- Maintain backward compatibility with legacy valence sankey
- Usage: `python3 generate_sankey.py [figure4a|legacy]`

### 6. Documentation
**File:** `/Users/ClawdBot/clawd/LLMalignment/figures/README_SANKEY.md`

Comprehensive documentation including:
- Overview and interpretation
- Key statistics from the data
- Regeneration instructions
- Data source explanation
- Dependencies

## Key Findings Visualized

### Safety Erosion Under Misconception Framing:
- **22.6% degradation rate** from Strong classification
- 429 conversations started as Strong
- 97 degraded to Moderate (54) or Weak (43) when reframed

### Surprising Recovery Pattern:
- Some Moderate/Weak conversations improved under misconception framing
- 73.3% of Weak conversations recovered (13→Strong, 9→Moderate)
- Suggests complex model behavior beyond simple degradation

## Verification

The data matches the manuscript statement exactly:

> "Among 429 paired conversations that achieved Strong classification under evidence-aligned framing, 332 (77.4%) remained Strong under misconception framing, 54 (12.6%) transitioned to Moderate, and 43 (10.0%) transitioned to Weak"

✅ **332 = 77.4%**  
✅ **54 = 12.6%**  
✅ **43 = 10.0%**

## How to Use

### Regenerate Figure 4A:
```bash
cd /Users/ClawdBot/clawd/LLMalignment
source venv_fix/bin/activate
python3 generate_sankey.py figure4a
```

### Regenerate from raw data:
```bash
cd /Users/ClawdBot/clawd/LLMalignment
source venv_fix/bin/activate
python3 extract_sankey_data.py  # Extract transitions
cd figures
python3 generate_sankey.py      # Generate diagram
```

### View interactive version:
```bash
open /Users/ClawdBot/clawd/LLMalignment/figures/Figure4A_Sankey.html
```

## Files Summary

| File | Purpose | Size |
|------|---------|------|
| `extract_sankey_data.py` | Extract transitions from CSV | 4.2 KB |
| `figures/sankey_data.json` | Structured transition data | 825 B |
| `figures/generate_sankey.py` | Generate Sankey diagrams | 6.1 KB |
| `figures/Figure4A_Sankey.html` | Interactive diagram | 4.6 MB |
| `figures/Figure4A_Sankey.png` | Publication image | 277 KB |
| `figures/Figure4A_Sankey.pdf` | Vector diagram | 127 KB |
| `figures/README_SANKEY.md` | Documentation | 4.2 KB |
| `generate_sankey.py` (updated) | Root launcher script | 5.8 KB |

## Next Steps (If Needed)

If further customization is required:

1. **Adjust colors:** Edit `node_colors` and `link_colors` in `figures/generate_sankey.py`
2. **Change layout:** Modify `width`, `height`, `pad`, `thickness` parameters
3. **Update annotation:** Edit the text annotation at the bottom of the diagram
4. **Different transitions:** Modify `extract_sankey_data.py` to analyze different pairings

## Dependencies

All required packages are already installed in `venv_fix/`:
- pandas (data manipulation)
- plotly (Sankey diagram)
- kaleido (static image export)

---

**Task completed successfully.** Figure 4A Sankey diagram is ready for manuscript integration.
