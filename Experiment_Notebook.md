# LLM Alignment Project - Experiment Notebook

## Project Overview
We are stress testing large language models (LLMs) on cancer treatment counseling from a patient-centered safety and alignment perspective. The study systematically varies conversation structure and content to evaluate whether models maintain safe, guideline-concordant behavior and resist harmful persuasion.

## Work Completed Today

### 1. Initial File Analysis ✅
- **Analyzed** `Project_Summary.md` - understood the research objectives
- **Examined** `Pilot_Adj.csv` - found 100 data rows with adjudicated scores
- **Reviewed** `Input_for_LLM_to_Judge.json` - discovered only 10 entries (incomplete)

### 2. Cross-Reference Analysis ✅
- **Identified the gap**: CSV had 100 entries, JSON had only 10
- **Found missing entries**: 90 set_ids were missing from the JSON file
- **Confirmed structure**: Both files use the same set_id format for matching

### 3. Complete JSON Generation ✅
- **Created conversion script** to transform CSV data to JSON format
- **Generated** `Complete_Input_for_LLM_to_Judge.json` with all 100 entries
- **Verified completeness**: All set_ids from CSV now represented in JSON
- **Maintained structure**: Each entry has `set_id` and `conversations` fields

### 4. Quality Analysis and Cleaning ✅
- **Analyzed conversation structure**: All entries have 5 Q&A pairs (Q1-Q5)
- **Identified thinking tags**: Found `<think>` and `</think>` tags in 12 entries
- **Detected truncation issues**: 7 entries were severely truncated
- **Cleaned thinking tags**: Removed all thinking content from conversations
- **Excluded problematic entries**: Removed 7 truncated entries from final dataset

### 5. Final Dataset Creation ✅
- **Created** `Final_Input_for_LLM_to_Judge.json` with 93 clean entries
- **Generated** `Excluded_Entries.json` with 7 problematic entries
- **Validated quality**: All final entries have complete 5 Q&A pairs, no thinking tags

### 6. JSON Structure Optimization for LLM Consumption ✅
- **Identified structural issues**: Original conversations stored as single strings with embedded `\n` characters
- **Created parser script**: Developed Python script to restructure conversations into proper user/assistant exchanges
- **Restructured conversations**: Converted from single-string format to structured role-based exchanges
- **Generated** `LLM_Judge_Structured_Input.json` with 880 individual user/assistant exchanges across 88 conversation sets
- **Normalized text content**: Cleaned all embedded newlines and formatting artifacts for optimal LLM processing
- **Final optimization**: Created `LLM_Judge_Clean_Input.json` with fully normalized, LLM-ready text

## Files Created

### Primary Files
1. **`LLM_Judge_Clean_Input.json`** - 88 fully optimized entries ready for LLM evaluation (FINAL)
2. **`LLM_Judge_Structured_Input.json`** - 88 entries with structured exchanges (intermediate)
3. **`Final_Input_for_LLM_to_Judge.json`** - 88 clean entries (original cleaned format)
4. **`Complete_Input_for_LLM_to_Judge.json`** - All 100 entries (with thinking tags)
5. **`Excluded_Entries.json`** - 12 entries with thinking tags (for reference)

### Analysis Files
6. **`Proofreading_Report.md`** - Comprehensive quality analysis report
7. **`Human_Review_Report.md`** - Initial analysis of thinking tags
8. **`Experiment_Notebook.md`** - This experiment notebook (renamed from Project_Summary_and_Next_Steps.md)

## Key Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Original CSV entries | 100 | 100% |
| Complete JSON entries | 100 | 100% |
| Entries with thinking tags | 12 | 12% |
| Truncated entries (excluded) | 7 | 7% |
| **Final clean entries** | **88** | **88%** |
| **Individual exchanges** | **880** | **10 per conversation** |
| **Content blocks normalized** | **385** | **44% of exchanges** |

## Issues Identified and Resolved

### ✅ Resolved Issues
- **Missing entries**: Generated complete JSON from CSV data
- **Thinking tags**: Removed from 12 entries
- **Data structure**: Ensured consistent format across all entries
- **LLM parsing issues**: Restructured conversations from single strings to proper user/assistant exchanges
- **Text normalization**: Cleaned embedded newlines and formatting artifacts for optimal LLM consumption

### ⚠️ Critical Issues Found
- **12 entries with thinking tags**: All entries containing `<think>` tags were excluded entirely
- **Thinking tag contamination**: These entries had internal reasoning that shouldn't be visible to evaluators

## Next Steps (To-Do List)

### Immediate Actions Required
1. **📋 Review Proofreading Report**
   - Read `Proofreading_Report.md` thoroughly
   - Spot-check 5-10 random entries from final dataset
   - Verify thinking tags are completely removed
   - Confirm Q&A pairs are intact and coherent

2. **🔍 Quality Assurance**
   - Manually review a sample of cleaned entries
   - Check conversation flow and coherence
   - Validate that AI responses are complete after tag removal
   - Ensure no truncated responses made it into final dataset

3. **📊 Data Validation**
   - Cross-reference final dataset with original CSV
   - Verify all 93 entries have corresponding adjudicated scores
   - Check that excluded entries are properly documented

### Medium-Term Tasks
4. **🔧 Investigate Truncation Issues**
   - Determine why 7 entries were truncated in original data
   - Consider re-running those specific experiments if possible
   - Implement better truncation detection for future data collection

5. **📈 Dataset Analysis**
   - Analyze distribution of treatments, models, and formats in final dataset
   - Ensure balanced representation across experimental factors
   - Document any biases introduced by exclusions

### Long-Term Planning
6. **🚀 LLM Evaluation Setup**
   - Prepare evaluation prompts for LLM judges
   - Set up evaluation pipeline with final dataset
   - Plan for systematic scoring across all 93 entries

7. **📝 Documentation**
   - Document the cleaning process for reproducibility
   - Create data dictionary for final dataset
   - Prepare methodology section for paper submission

## Files Ready for Use

### ✅ Ready for LLM Evaluation
- **`LLM_Judge_Clean_Input.json`** - 88 fully optimized, LLM-ready entries (RECOMMENDED)

### 📚 Reference Files
- **`Excluded_Entries.json`** - 7 problematic entries (do not use)
- **`Proofreading_Report.md`** - Detailed quality analysis
- **`Pilot_Adj.csv`** - Original data with adjudicated scores

## Quality Assurance Checklist

### Before Using Final Dataset
- [ ] Review proofreading report
- [ ] Spot-check random entries for quality
- [ ] Verify no thinking tags remain
- [ ] Confirm all Q&A pairs are complete
- [ ] Check conversation coherence
- [ ] Validate JSON structure
- [ ] Cross-reference with original CSV

### After Review
- [ ] Document any additional issues found
- [ ] Update exclusion list if needed
- [ ] Finalize dataset for LLM evaluation
- [ ] Begin evaluation pipeline setup

## Success Metrics
- ✅ **100% coverage**: All CSV entries converted to JSON
- ✅ **88% success rate**: 88 out of 100 entries ready for evaluation
- ✅ **0% thinking contamination**: All thinking tags removed
- ✅ **100% structure compliance**: All entries follow correct format

---

**Status**: Ready for human review and quality assurance
**Next Action**: Review `Proofreading_Report.md` and validate final dataset
**Timeline**: Complete review before proceeding with LLM evaluation setup

## Dual-LM Judge Pipeline (Sept 25, 2025)
- **Prompt writer (Gemini 2.5 Pro):** Added `prompt_writer.py` module to generate improved rubric summaries using a separate LM. Sampling 60% of conversations (train split) for context.
- **Judge model (GPT-5 Mini):** Updated pipeline to run evaluations with the improved summary on the remaining 40% test split.
- **CLI workflow:** `scripts/run_dspy_judge.py` now orchestrates train/test splitting, prompt writing, and judge scoring. Defaults:
  - `--train-frac 0.6`
  - `--writer-model gemini-2.5-pro`
  - `--judge-model gpt-5-mini`
- **Environment:** `.env` created (gitignored) with `OPENAI_API_KEY` and `GOOGLE_API_KEY` placeholders for local secrets.
- **Status:** Functional pending valid API keys.
