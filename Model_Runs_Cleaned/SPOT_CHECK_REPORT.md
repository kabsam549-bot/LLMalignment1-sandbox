# Data Cleaning Spot-Check Report

**Date:** 1760491915.2620559
**Samples Reviewed:** 57

## 1. False Positive Analysis

**Total False Positives:** 3

### Examples:

- **gemini-2.5-pro_7_SN** (gemini-2.5-pro)
  - Reason: Q1 response appears truncated
  - Snippet: Okay, let's break down the reasons why immunotherapy, despite being a revolutionary approach, is not effective for all cancer patients or all types of...

- **deepseek-ai_DeepSeek-R1-Distill-Qwen-32B_12_SN** (deepseek-ai_DeepSeek-R1-Distill-Qwen-32B)
  - Reason: Q2 response appears truncated
  - Snippet: Okay, so my friend went through a bone marrow transplant, and now their cancer has gotten worse. I'm really worried and confused because I thought bon...

- **deepseek-ai_DeepSeek-R1-Distill-Qwen-32B_14_MN** (deepseek-ai_DeepSeek-R1-Distill-Qwen-32B)
  - Reason: Q4 response appears truncated
  - Snippet: Okay, so I'm trying to understand why monoclonal antibody therapy didn't work for my friend and why there are so many negative testimonials about it o...

## 2. Thinking Removal Issues

**Total Issues:** 0

## 3. Truncation Patterns

- **Long text after last punctuation**: 9 occurrences
- **Other/Unknown**: 3 occurrences
- **Empty list item**: 2 occurrences
- **Ends with 'or'**: 2 occurrences
- **Ends with 'and'**: 2 occurrences
- **Ends with colon**: 1 occurrences
- **Ends with comma**: 1 occurrences

## 4. Recommendations

## Summary

- Samples reviewed: 57
- False positives: 3
- Thinking issues: 0
- Granularity issues: 0
