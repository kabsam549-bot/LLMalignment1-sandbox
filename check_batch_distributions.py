#!/usr/bin/env python3
"""
Check distributions of models, valence, and treatment type between Batch 001 and Batch 002.
This helps determine if performance differences are due to different batch compositions.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict
from analyze_batch_results import load_batch_data


def analyze_distributions(data: list, batch_name: str) -> dict:
    """Analyze distributions of key factors."""
    distributions = {
        'models': Counter(),
        'valence': Counter(),
        'treatment_type': Counter(),
        'format': Counter(),
        'model_provider': Counter(),
        'model_size': Counter(),
    }
    
    # Model categorization (simplified version)
    model_providers = {
        '4o': 'OpenAI', '4o-mini': 'OpenAI', 'o3-mini': 'OpenAI',
        'claude-3-5-haiku-20241022.json': 'Anthropic', 'claude-3-7-sonnet-20250219.json': 'Anthropic',
        'gemini-1.5-flash': 'Google', 'gemini-2.0-flash': 'Google', 
        'gemini-2.0-flash-thinking-exp-01-21': 'Google', 'gemini-2.5-pro': 'Google',
        'google_gemma-3-27b-it': 'Google', 'gemma3-4b.json': 'Google',
        'llama3.2_3b.json': 'Meta',
        'deepseek-ai_DeepSeek-R1-Distill-Qwen-32B': 'DeepSeek',
        'Qwen_Qwen3-32B': 'Alibaba',
    }
    
    model_sizes = {
        '4o': 'large', '4o-mini': 'small', 'o3-mini': 'small',
        'claude-3-5-haiku-20241022.json': 'small', 'claude-3-7-sonnet-20250219.json': 'medium',
        'gemini-1.5-flash': 'medium', 'gemini-2.0-flash': 'medium',
        'gemini-2.0-flash-thinking-exp-01-21': 'medium', 'gemini-2.5-pro': 'large',
        'google_gemma-3-27b-it': 'medium', 'gemma3-4b.json': 'small',
        'llama3.2_3b.json': 'small',
        'deepseek-ai_DeepSeek-R1-Distill-Qwen-32B': 'medium',
        'Qwen_Qwen3-32B': 'medium',
    }
    
    for record in data:
        # Models
        model = record.get('model_name', 'Unknown')
        distributions['models'][model] += 1
        
        # Valence
        valence = record.get('valence', 'Unknown')
        distributions['valence'][valence] += 1
        
        # Treatment type
        treatment = record.get('treatment_type', 'Unknown')
        distributions['treatment_type'][treatment] += 1
        
        # Format
        format_val = record.get('format', 'Unknown')
        distributions['format'][format_val] += 1
        
        # Model provider
        provider = model_providers.get(model, 'Unknown')
        distributions['model_provider'][provider] += 1
        
        # Model size
        size = model_sizes.get(model, 'Unknown')
        distributions['model_size'][size] += 1
    
    return distributions


def format_distribution_comparison(dist_001: dict, dist_002: dict, factor_name: str, total_001: int, total_002: int) -> str:
    """Format a comparison of distributions for a specific factor."""
    lines = [f"\n{'='*70}", f"{factor_name.upper()} DISTRIBUTION COMPARISON", f"{'='*70}"]
    lines.append(f"{'Category':<40} {'Batch 001':>15} {'Batch 002':>15} {'Difference':>15}")
    lines.append("-" * 85)
    
    all_categories = set(dist_001.keys()) | set(dist_002.keys())
    
    for category in sorted(all_categories):
        count_001 = dist_001.get(category, 0)
        count_002 = dist_002.get(category, 0)
        pct_001 = (count_001 / total_001 * 100) if total_001 > 0 else 0
        pct_002 = (count_002 / total_002 * 100) if total_002 > 0 else 0
        diff = count_002 - count_001
        pct_diff = pct_002 - pct_001
        
        diff_str = f"{diff:+d} ({pct_diff:+.1f}pp)" if diff != 0 else "0 (0.0pp)"
        
        lines.append(
            f"{str(category):<40} {count_001:>4} ({pct_001:>5.1f}%) {count_002:>4} ({pct_002:>5.1f}%) {diff_str:>15}"
        )
    
    return "\n".join(lines)


def format_cross_tab_comparison(data_001: list, data_002: list, factor1: str, factor2: str, title: str) -> str:
    """Compare cross-tabulations between batches."""
    lines = [f"\n{'='*70}", f"{title} - CROSS-TABULATION COMPARISON", f"{'='*70}"]
    
    # Get all unique values
    values_1 = set(d.get(factor1, 'Unknown') for d in data_001 + data_002)
    values_2 = set(d.get(factor2, 'Unknown') for d in data_001 + data_002)
    
    lines.append(f"\n{'Combination':<30} {'Batch 001':>15} {'Batch 002':>15} {'Difference':>15}")
    lines.append("-" * 75)
    
    for val1 in sorted(values_1):
        for val2 in sorted(values_2):
            count_001 = len([d for d in data_001 if d.get(factor1) == val1 and d.get(factor2) == val2])
            count_002 = len([d for d in data_002 if d.get(factor1) == val1 and d.get(factor2) == val2])
            
            if count_001 > 0 or count_002 > 0:
                diff = count_002 - count_001
                diff_str = f"{diff:+d}" if diff != 0 else "0"
                combination = f"{val1} × {val2}"
                lines.append(f"{combination:<30} {count_001:>4} {count_002:>4} {diff_str:>15}")
    
    return "\n".join(lines)


def generate_distribution_report(data_001: list, data_002: list) -> str:
    """Generate comprehensive distribution comparison report."""
    report_lines = []
    
    report_lines.append("=" * 70)
    report_lines.append("BATCH 001 vs BATCH 002 - DISTRIBUTION ANALYSIS")
    report_lines.append("=" * 70)
    report_lines.append(f"\nBatch 001: {len(data_001)} conversations")
    report_lines.append(f"Batch 002: {len(data_002)} conversations")
    report_lines.append("\nThis analysis checks if performance differences might be due to")
    report_lines.append("different compositions of models, valence, and treatment types.")
    
    # Analyze distributions
    dist_001 = analyze_distributions(data_001, "Batch 001")
    dist_002 = analyze_distributions(data_002, "Batch 002")
    
    total_001 = len(data_001)
    total_002 = len(data_002)
    
    # Model distribution
    report_lines.append(format_distribution_comparison(
        dist_001['models'], dist_002['models'], "MODELS", total_001, total_002
    ))
    
    # Model provider distribution
    report_lines.append(format_distribution_comparison(
        dist_001['model_provider'], dist_002['model_provider'], "MODEL PROVIDER", total_001, total_002
    ))
    
    # Model size distribution
    report_lines.append(format_distribution_comparison(
        dist_001['model_size'], dist_002['model_size'], "MODEL SIZE", total_001, total_002
    ))
    
    # Valence distribution
    report_lines.append(format_distribution_comparison(
        dist_001['valence'], dist_002['valence'], "VALENCE", total_001, total_002
    ))
    
    # Treatment type distribution
    report_lines.append(format_distribution_comparison(
        dist_001['treatment_type'], dist_002['treatment_type'], "TREATMENT TYPE", total_001, total_002
    ))
    
    # Format distribution
    report_lines.append(format_distribution_comparison(
        dist_001['format'], dist_002['format'], "FORMAT", total_001, total_002
    ))
    
    # Cross-tabulations
    report_lines.append(format_cross_tab_comparison(
        data_001, data_002, 'treatment_type', 'valence', 'TREATMENT TYPE × VALENCE'
    ))
    
    report_lines.append(format_cross_tab_comparison(
        data_001, data_002, 'format', 'treatment_type', 'FORMAT × TREATMENT TYPE'
    ))
    
    report_lines.append(format_cross_tab_comparison(
        data_001, data_002, 'format', 'valence', 'FORMAT × VALENCE'
    ))
    
    # Summary
    report_lines.append(f"\n{'='*70}")
    report_lines.append("DISTRIBUTION SUMMARY")
    report_lines.append(f"{'='*70}")
    
    # Check for major imbalances
    imbalances = []
    
    # Check model provider balance
    for provider in set(dist_001['model_provider'].keys()) | set(dist_002['model_provider'].keys()):
        count_001 = dist_001['model_provider'].get(provider, 0)
        count_002 = dist_002['model_provider'].get(provider, 0)
        pct_001 = (count_001 / total_001 * 100) if total_001 > 0 else 0
        pct_002 = (count_002 / total_002 * 100) if total_002 > 0 else 0
        diff = abs(pct_002 - pct_001)
        if diff > 10:  # More than 10 percentage points difference
            imbalances.append(f"{provider}: {pct_001:.1f}% → {pct_002:.1f}% ({diff:.1f}pp difference)")
    
    # Check valence balance
    for valence in ['positive', 'negative']:
        count_001 = dist_001['valence'].get(valence, 0)
        count_002 = dist_002['valence'].get(valence, 0)
        pct_001 = (count_001 / total_001 * 100) if total_001 > 0 else 0
        pct_002 = (count_002 / total_002 * 100) if total_002 > 0 else 0
        diff = abs(pct_002 - pct_001)
        if diff > 10:
            imbalances.append(f"{valence} valence: {pct_001:.1f}% → {pct_002:.1f}% ({diff:.1f}pp difference)")
    
    # Check treatment type balance
    for treatment in ['traditional', 'alternative']:
        count_001 = dist_001['treatment_type'].get(treatment, 0)
        count_002 = dist_002['treatment_type'].get(treatment, 0)
        pct_001 = (count_001 / total_001 * 100) if total_001 > 0 else 0
        pct_002 = (count_002 / total_002 * 100) if total_002 > 0 else 0
        diff = abs(pct_002 - pct_001)
        if diff > 10:
            imbalances.append(f"{treatment} treatment: {pct_001:.1f}% → {pct_002:.1f}% ({diff:.1f}pp difference)")
    
    if imbalances:
        report_lines.append("\n⚠️  MAJOR DISTRIBUTION IMBALANCES DETECTED:")
        for imbalance in imbalances:
            report_lines.append(f"  - {imbalance}")
        report_lines.append("\nThese imbalances may explain performance differences between batches.")
    else:
        report_lines.append("\n✓ Distributions are relatively balanced between batches.")
        report_lines.append("Performance differences are likely due to actual model behavior, not composition.")
    
    return "\n".join(report_lines)


def main():
    batch_results_dir = Path(__file__).parent / "batch_results"
    
    print("Loading batch data...")
    data_001 = load_batch_data(batch_results_dir, ['001'])
    data_002 = load_batch_data(batch_results_dir, ['002'])
    
    if not data_001 or not data_002:
        print("Error: Could not load both batches")
        return
    
    print(f"Loaded {len(data_001)} records from batch 001")
    print(f"Loaded {len(data_002)} records from batch 002")
    
    # Generate distribution report
    report = generate_distribution_report(data_001, data_002)
    print(report)
    
    # Save report
    report_path = batch_results_dir / "batch_distribution_analysis.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n\nDistribution analysis saved to {report_path}")


if __name__ == "__main__":
    main()

