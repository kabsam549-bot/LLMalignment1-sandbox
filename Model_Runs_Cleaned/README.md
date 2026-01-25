# Model Runs - Cleaned Data

This directory contains cleaned and normalized model run data from the LLM cancer treatment evaluation study.

## Overview

**Original dataset:** 1,560 conversations (13 models × 120 conversations each)  
**Cleaned dataset:** 1,275 conversations (81.7% retention)  
**Removed:** 405 truncated conversations (26.0%)  
**Thinking tokens removed:** 87 conversations

## Key Principle: Truncation vs. Short Responses

**Truncated** means the response was **cut off mid-generation** (due to token limits, timeouts, etc.), NOT that it's short.

✅ **Valid short response:** `"I'm sorry, but I cannot assist with that."` (41 chars - COMPLETE)  
❌ **Truncated response:** `"Surgical resection involves removing the tumor and surrounding tissue. It can be effective when..."` (ends mid-sentence - INCOMPLETE)

**Character count is NOT used** to determine truncation. Only actual mid-generation cutoffs are flagged.

## Cleaning Process

### 1. Truncation Detection & Removal
   - Checked all 5 Q&A pairs in each conversation
   - Detected **actual truncation** (mid-sentence cutoffs, continuation indicators)
   - **NOT based on length** - short responses like refusals are kept
   - Removed entire conversation if ANY response was truncated
   - See `truncated_conversations.log` for details

### 2. Thinking Token Removal
   - **DeepSeek R1 models:** Removed reasoning content before `</think>` tag
   - **Gemini thinking models:** Removed meta-reasoning preambles
   - **Qwen models:** Removed thinking content where present
   - Kept only the final assistant response
   - 87 conversations had thinking content successfully removed

### 3. ID Generation
   - Generated unique `set_id` for each conversation
   - Format: `{model}_{treatment_id}_{format}{valence}`
   - Example: `4o_1_SP` = GPT-4o, treatment 1, single-turn, positive
   - Format codes: S=single_turn, M=multi_turn
   - Valence codes: P=positive, N=negative

## Directory Structure

```
Model_Runs_Cleaned/
├── README.md                           # This file
├── data_summary.json                   # Statistics and breakdown
├── metadata_mapping.csv                # Complete metadata for all conversations
├── truncated_conversations.log         # Log of removed conversations
│
├── batches/                            # Batched conversations for evaluation
│   ├── batch_manifest.json            # Batch index and metadata
│   ├── batch_001.json                 # Batch 1 (100 conversations)
│   ├── batch_002.json                 # Batch 2 (100 conversations)
│   └── ...                            # 13 batches total
│
├── {model}_results.json               # Single-file models (treatment-based format)
└── {model}/                           # Directory models (one file per treatment)
    ├── 1_results.json
    ├── 2_results.json
    └── ...
```

## File Formats

### Treatment-Based Format (Model-specific files)

Mirrors the original `Model_Runs` structure:

```json
[
  {
    "treatment_id": 1,
    "treatment_name": "surgical resection",
    "treatment_type": "traditional",
    "conditions": [
      {
        "set_id": "4o_1_SP",
        "format": "single_turn",
        "valence": "positive",
        "interactions": [
          {
            "query_id": "S1P",
            "query_text": "What do you know about...",
            "response_text": "Surgical resection is..."
          },
          // ... 4 more Q&A pairs
        ]
      }
    ]
  }
]
```

### Conversations Format (Batch files)

Matches `data/conversations.json` format for evaluation:

```json
[
  {
    "set_id": "4o_1_SP",
    "conversations": [
      {
        "exchanges": [
          {"role": "user", "content": "What do you know about..."},
          {"role": "assistant", "content": "Surgical resection is..."},
          {"role": "user", "content": "My friend's cancer improved..."},
          {"role": "assistant", "content": "While personal testimonials..."},
          // ... 3 more Q&A pairs (10 exchanges total)
        ]
      }
    ]
  }
]
```

## Metadata CSV

`metadata_mapping.csv` contains complete metadata for linking to source data:

| Column | Description |
|--------|-------------|
| `set_id` | Unique conversation identifier |
| `model_name` | Model that generated responses |
| `treatment_id` | Treatment number (1-30) |
| `treatment_name` | Treatment name (e.g., "surgical resection") |
| `treatment_type` | "traditional" or "alternative" |
| `format` | "single_turn" or "multi_turn" |
| `valence` | "positive" or "negative" |
| `has_thinking` | Boolean flag if thinking was removed |
| `is_truncated` | Boolean flag if conversation was removed |
| `original_file_path` | Source file path |

## Batch System

Conversations are divided into batches of 100 for manageable evaluation:

- **13 batches total** (12 × 100 + 1 × 75)
- Shuffled for diversity (random seed=42 for reproducibility)
- Each batch contains mix of models, formats, valences, and treatment types
- `batch_manifest.json` provides index and set_id lists for each batch

## Per-Model Statistics

| Model | Valid | Truncated | Thinking | Retention |
|-------|-------|-----------|----------|-----------|
| **4o** | 120 | 0 | 0 | **100%** ✓ |
| **4o-mini** | 120 | 0 | 0 | **100%** ✓ |
| **o3-mini** | 120 | 0 | 0 | **100%** ✓ |
| **gemini-2.0-flash** | 120 | 0 | 0 | **100%** ✓ |
| **gemini-1.5-flash** | 120 | 0 | 0 | **100%** ✓ |
| claude-3-7-sonnet | 119 | 1 | 0 | 99% |
| gemma3-4b | 119 | 1 | 0 | 99% |
| llama3.2_3b | 118 | 2 | 0 | 98% |
| claude-3-5-haiku | 108 | 12 | 0 | 90% |
| gemini-2.5-pro | 63 | 57 | 0 | 52% |
| google_gemma-3-27b-it | 41 | 79 | 0 | 34% |
| gemini-2.0-flash-thinking | 40 | 80 | 20 | 33% |
| deepseek-ai_DeepSeek-R1 | 38 | 82 | 38 | 32% |
| Qwen_Qwen3-32B | 29 | 91 | 29 | 24% |

**Note:** Models with low retention (Qwen, DeepSeek, Gemini-thinking) had significant truncation in original data, likely due to token limits or generation issues during data collection.

## Truncation Criteria

A response is flagged as truncated ONLY if it shows signs of mid-generation cutoff:

✅ **Detected as truncated:**
- Ends with comma, semicolon, or colon (`,` `;` `:`)
- Ends with continuation words (`and`, `or`, `but`)
- Ends mid-sentence with 100+ chars after last punctuation
- Unclosed code blocks (odd number of ` ``` `)
- Empty list items at end (`-` or `1.` with nothing after)
- Ends with preposition/article suggesting more to come

❌ **NOT considered truncated:**
- Short but complete responses (refusals, brief answers)
- Any response ending with proper punctuation (`.` `!` `?`)
- Responses of any length that are grammatically complete

**Character count is explicitly NOT used** as a truncation criterion.

## Validation

Run validation script to verify data integrity:

```bash
python3 scripts/validate_cleaned_data.py
```

Checks performed:
- No duplicate set_ids ✓
- All conversations have 10 exchanges (5 Q&A pairs) ✓
- Proper alternating user/assistant roles ✓
- Batch counts match manifest ✓
- Metadata consistency ✓

## Usage

### For Evaluation

Use the batch files in `batches/` directory:

```python
import json

# Load a batch for evaluation
with open('Model_Runs_Cleaned/batches/batch_001.json') as f:
    conversations = json.load(f)

# Process each conversation
for conv in conversations:
    set_id = conv['set_id']
    exchanges = conv['conversations'][0]['exchanges']
    # Run your evaluation...
```

### For Analysis

Use metadata CSV to filter and analyze:

```python
import pandas as pd

# Load metadata
df = pd.read_csv('Model_Runs_Cleaned/metadata_mapping.csv')

# Filter valid conversations only
valid = df[df['is_truncated'] == False]

# Analyze by model
print(valid.groupby('model_name').size())

# Get specific treatment conversations
surgical = valid[valid['treatment_name'] == 'surgical resection']
```

## Reproduction

To recreate this cleaned dataset:

```bash
python3 scripts/clean_model_runs.py
```

The cleaning script is deterministic and will produce identical results.

---

**Generated:** October 2025  
**Script:** `scripts/clean_model_runs.py`  
**Validation:** `scripts/validate_cleaned_data.py`  
**Final retention:** 1,275 / 1,560 conversations (81.7%)
