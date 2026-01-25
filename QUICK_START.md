# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify OpenAI API key is in .env
cat .env
```

## Your First Evaluation

### 1. Review the Prompt

```bash
cat prompt.txt
```

This is the prompt that will be sent to GPT-5-mini to evaluate conversations. Edit it to customize the evaluation approach.

### 2. Run a Test Evaluation (Regular Mode)

For quick testing, use regular mode (processes conversations one-by-one):

```bash
python run_evaluation.py --mode regular
```

This will:
- Load conversations from `data/conversations.json`
- Send each to GPT-5-mini for evaluation
- Score each conversation using Python
- Calculate agreement metrics with human annotations
- Generate visualizations and reports

Results will be saved to `results/run_YYYYMMDD_HHMMSS/`

### 3. Review Results

```bash
# Find your latest run
ls -lt results/ | head -5

# View the summary
cat results/run_YYYYMMDD_HHMMSS/agreement_summary_YYYYMMDD_HHMMSS.txt
```

### 4. Iterate on the Prompt

1. Edit `prompt.txt`
2. Run evaluation again: `python run_evaluation.py --mode regular`
3. Compare results across different timestamps

## Production Evaluation (Batch Mode)

For final evaluations, use batch mode (50% cheaper, processes in parallel):

```bash
python run_evaluation.py --mode batch
```

**Note**: Batch jobs can take 10 minutes to several hours depending on OpenAI's queue.

## Understanding the Output

Each run creates a timestamped directory with:

- **`prompt_YYYYMMDD_HHMMSS.txt`** - Exact prompt used (for reproducibility)
- **`agreement_summary_YYYYMMDD_HHMMSS.txt`** - Human-readable metrics ⭐ START HERE
- **`llm_predictions_YYYYMMDD_HHMMSS.csv`** - LLM scores for each conversation
- **`fleiss_kappa_YYYYMMDD_HHMMSS.json`** - 3-way agreement (ML, RA, LLM)
- **`cohens_kappa_YYYYMMDD_HHMMSS.json`** - LLM vs Gold Standard
- **`confusion_matrices_YYYYMMDD_HHMMSS.png`** - Visual confusion matrices
- **`agreement_heatmap_YYYYMMDD_HHMMSS.png`** - Kappa heatmap

## Key Metrics Explained

### Fleiss' Kappa (3-way)
Agreement between ML annotator, RA annotator, and LLM judge:
- **0.61-0.80**: Substantial agreement ✅
- **0.41-0.60**: Moderate agreement
- **< 0.40**: Fair/poor agreement ⚠️

### Cohen's Kappa (LLM vs Gold)
Agreement between LLM and adjudicated gold standard:
- Same interpretation as Fleiss' kappa
- This is the primary metric for LLM performance

### 3-way Match %
Percentage where all three (ML, RA, LLM) agree exactly

### LLM vs Any Human %
Percentage where LLM matches at least one human annotator

## Troubleshooting

**"Prompt file not found"**
```bash
touch prompt.txt
# Add your evaluation prompt
```

**Batch job takes too long**
```bash
# Use regular mode for testing
python run_evaluation.py --mode regular
```

**Want to re-run analysis only**
```bash
python run_evaluation.py --mode analyze --results results/run_20241011_143022/llm_predictions_20241011_143022.csv
```

## Next Steps

1. Read the full `README.md` for detailed information
2. Review `data/Rubric.md` to understand the evaluation criteria
3. Experiment with different prompts
4. Compare results across runs to optimize your prompt

## Support

For questions or issues, refer to:
- `README.md` - Comprehensive documentation
- `data/Rubric.md` - Detailed scoring criteria
- Example output files in `results/` directories

