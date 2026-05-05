# Sankey Diagram for Figure 4A: Classification Transitions Under Misconception Framing

## Overview

This directory contains the data and scripts to generate Figure 4A, which shows how safety classifications transition when the same scenarios shift from evidence-aligned framing to misconception framing.

## Generated Files

### Data File
- **`sankey_data.json`** - Complete transition matrix with all flows from Evidence-aligned → Misconception framing

### Figure Outputs
- **`Figure4A_Sankey.html`** - Interactive version (can be opened in browser)
- **`Figure4A_Sankey.png`** - High-resolution PNG for publication (1800×1200px)
- **`Figure4A_Sankey.pdf`** - Vector PDF for publication

### Scripts
- **`generate_sankey.py`** - Main script to generate the Sankey diagram
- **`../extract_sankey_data.py`** - Extract transition data from raw CSV

## Key Statistics

From the manuscript and data analysis:

**Total Paired Conversations: 569**

### Starting Classification Distribution:
- Strong: 429 (75.4%)
- Moderate: 110 (19.3%)
- Weak: 30 (5.3%)

### Transitions from Strong (Evidence-aligned → Misconception):
- Strong → Strong: 332 (77.4%)
- Strong → Moderate: 54 (12.6%)
- Strong → Weak: 43 (10.0%)
- **Total Degradation: 97 (22.6%)**

### Transitions from Moderate:
- Moderate → Strong: 48 (43.6%)
- Moderate → Moderate: 35 (31.8%)
- Moderate → Weak: 27 (24.5%)

### Transitions from Weak:
- Weak → Strong: 13 (43.3%)
- Weak → Moderate: 9 (30.0%)
- Weak → Weak: 8 (26.7%)
- **Total Recovery: 22 (73.3%)**

## How to Regenerate

### From the figures/ directory:
```bash
cd /Users/ClawdBot/clawd/LLMalignment/figures
source ../venv_fix/bin/activate
python3 generate_sankey.py
```

### From the root LLMalignment directory:
```bash
cd /Users/ClawdBot/clawd/LLMalignment
source venv_fix/bin/activate
python3 generate_sankey.py figure4a
```

### To regenerate the data from scratch:
```bash
cd /Users/ClawdBot/clawd/LLMalignment
source venv_fix/bin/activate
python3 extract_sankey_data.py  # Creates figures/sankey_data.json
cd figures
python3 generate_sankey.py      # Creates the diagram
```

## Data Source

The transitions are calculated from:
- **Input CSV:** `batch_results/final_all_batches_data.csv`
- **Analysis:** Pairs of conversations that differ only in valence (positive vs negative)
- **Framing Definition:**
  - **Evidence-aligned:** For alternative treatments = negative valence (questioning); For traditional treatments = positive valence (asking about)
  - **Misconception:** For alternative treatments = positive valence (promoting); For traditional treatments = negative valence (attacking)

## Interpretation

The Sankey diagram visually demonstrates:

1. **Safety Erosion:** 22.6% of conversations that were Strong under evidence-aligned framing degraded (to Moderate or Weak) when the same scenario was presented with misconception framing

2. **Paradoxical Improvement:** Interestingly, some Moderate and Weak conversations improved under misconception framing, suggesting complex interactions between user framing and model responses

3. **Validation Bias:** The degradation from Strong → Moderate/Weak represents the "sycophancy effect" where models validate patient misconceptions rather than maintaining safety standards

## Citation

This figure appears in the manuscript as **Figure 4A** with the caption:

> "Classification transitions when scenarios shifted from evidence-aligned to misconception framing. Among 429 conversations that achieved Strong classification under evidence-aligned framing, 332 (77.4%) remained Strong under misconception framing, 54 (12.6%) transitioned to Moderate, and 43 (10.0%) transitioned to Weak."

## Dependencies

Required Python packages (included in venv_fix):
- `pandas` - Data manipulation
- `plotly` - Sankey diagram generation
- `kaleido` - Static image export (PNG, PDF)

## Files Created

- 2026-01-24: Initial creation of Sankey diagram for Figure 4A
  - Data extraction script: `extract_sankey_data.py`
  - Diagram generator: `figures/generate_sankey.py`
  - Data file: `figures/sankey_data.json`
  - Updated root script: `generate_sankey.py` (now routes to Figure 4A)
