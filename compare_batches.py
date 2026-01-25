#!/usr/bin/env python3
"""
Compare results between batch 001 and batch 002 to identify shifts or consistency.
"""
import json
from pathlib import Path
from collections import defaultdict
from analyze_batch_results import (
    load_batch_data, count_classifications, calculate_percentages,
    analyze_by_dimension, analyze_by_model_category, analyze_critical_fails,
    format_breakdown_table
)


def compare_overall_distributions(data_001: list, data_002: list) -> str:
    """Compare overall classification distributions."""
    counts_001 = count_classifications(data_001)
    counts_002 = count_classifications(data_002)
    pcts_001 = calculate_percentages(counts_001)
    pcts_002 = calculate_percentages(counts_002)
    
    lines = [f"\n{'='*70}", "OVERALL CLASSIFICATION COMPARISON", f"{'='*70}"]
    lines.append(f"{'Classification':<15} {'Batch 001':>20} {'Batch 002':>20} {'Change':>15}")
    lines.append("-" * 70)
    
    for cls in ['Strong', 'Moderate', 'Weak']:
        count_001 = counts_001[cls]
        count_002 = counts_002[cls]
        pct_001 = pcts_001[cls]
        pct_002 = pcts_002[cls]
        change = pct_002 - pct_001
        change_str = f"{change:+.1f}%" if change != 0 else "0.0%"
        
        lines.append(
            f"{cls:<15} {count_001:>4} ({pct_001:>5.1f}%) {count_002:>4} ({pct_002:>5.1f}%) {change_str:>15}"
        )
    
    total_001 = sum(counts_001.values())
    total_002 = sum(counts_002.values())
    lines.append("-" * 70)
    lines.append(f"{'Total':<15} {total_001:>4} {'':>10} {total_002:>4} {'':>10} {'':>15}")
    
    return "\n".join(lines)


def compare_critical_fails(fail_001: dict, fail_002: dict) -> str:
    """Compare critical fails between batches."""
    lines = [f"\n{'='*70}", "CRITICAL FAILS COMPARISON", f"{'='*70}"]
    
    total_001 = fail_001['total_records']
    total_002 = fail_002['total_records']
    with_fails_001 = fail_001['records_with_any_fail']
    with_fails_002 = fail_002['records_with_any_fail']
    pct_001 = (with_fails_001 / total_001 * 100) if total_001 > 0 else 0
    pct_002 = (with_fails_002 / total_002 * 100) if total_002 > 0 else 0
    
    lines.append(f"\nRecords with Critical Fails:")
    lines.append(f"  Batch 001: {with_fails_001}/{total_001} ({pct_001:.1f}%)")
    lines.append(f"  Batch 002: {with_fails_002}/{total_002} ({pct_002:.1f}%)")
    lines.append(f"  Change: {pct_002 - pct_001:+.1f} percentage points")
    
    # Compare fail types
    all_fail_types = set(fail_001['fail_breakdown'].keys()) | set(fail_002['fail_breakdown'].keys())
    if all_fail_types:
        lines.append(f"\nFail Type Breakdown:")
        lines.append(f"{'Fail Type':<40} {'Batch 001':>12} {'Batch 002':>12} {'Change':>12}")
        lines.append("-" * 76)
        
        for fail_type in sorted(all_fail_types):
            count_001 = fail_001['fail_breakdown'].get(fail_type, 0)
            count_002 = fail_002['fail_breakdown'].get(fail_type, 0)
            change = count_002 - count_001
            change_str = f"{change:+d}" if change != 0 else "0"
            lines.append(f"{fail_type:<40} {count_001:>12} {count_002:>12} {change_str:>12}")
    
    return "\n".join(lines)


def compare_by_dimension(data_001: list, data_002: list, dimension: str, title: str) -> str:
    """Compare breakdowns by a specific dimension."""
    breakdown_001 = analyze_by_dimension(data_001, dimension)
    breakdown_002 = analyze_by_dimension(data_002, dimension)
    
    lines = [f"\n{'='*70}", f"{title} - COMPARISON", f"{'='*70}"]
    lines.append(f"{'Category':<30} {'Batch 001 Strong%':>18} {'Batch 002 Strong%':>18} {'Change':>12}")
    lines.append("-" * 78)
    
    all_categories = set(breakdown_001.keys()) | set(breakdown_002.keys())
    
    for category in sorted(all_categories):
        counts_001 = breakdown_001.get(category, {'Strong': 0, 'total': 0})
        counts_002 = breakdown_002.get(category, {'Strong': 0, 'total': 0})
        
        total_001 = counts_001['total']
        total_002 = counts_002['total']
        
        if total_001 > 0 and total_002 > 0:
            strong_pct_001 = (counts_001['Strong'] / total_001) * 100
            strong_pct_002 = (counts_002['Strong'] / total_002) * 100
            change = strong_pct_002 - strong_pct_001
            change_str = f"{change:+.1f}pp" if change != 0 else "0.0pp"
            
            lines.append(
                f"{category:<30} {strong_pct_001:>6.1f}% (n={total_001:>3}) {strong_pct_002:>6.1f}% (n={total_002:>3}) {change_str:>12}"
            )
    
    return "\n".join(lines)


def compare_treatment_valence(data_001: list, data_002: list) -> str:
    """Compare Treatment Type × Valence cross-tabs."""
    lines = [f"\n{'='*70}", "TREATMENT TYPE × VALENCE - COMPARISON", f"{'='*70}"]
    lines.append(f"{'Condition':<25} {'Batch 001 Strong%':>20} {'Batch 002 Strong%':>20} {'Change':>15}")
    lines.append("-" * 80)
    
    combinations = [
        ('alternative', 'positive', 'Alt+Pos (hardest)'),
        ('alternative', 'negative', 'Alt+Neg (easier)'),
        ('traditional', 'positive', 'Trad+Pos (baseline)'),
        ('traditional', 'negative', 'Trad+Neg (adversarial)'),
    ]
    
    for treatment_val, valence_val, label in combinations:
        subset_001 = [d for d in data_001 if d.get('treatment_type') == treatment_val and d.get('valence') == valence_val]
        subset_002 = [d for d in data_002 if d.get('treatment_type') == treatment_val and d.get('valence') == valence_val]
        
        if subset_001 and subset_002:
            counts_001 = count_classifications(subset_001)
            counts_002 = count_classifications(subset_002)
            pcts_001 = calculate_percentages(counts_001)
            pcts_002 = calculate_percentages(counts_002)
            
            total_001 = sum(counts_001.values())
            total_002 = sum(counts_002.values())
            change = pcts_002['Strong'] - pcts_001['Strong']
            change_str = f"{change:+.1f}pp" if change != 0 else "0.0pp"
            
            # Count critical fails
            fails_001 = len([d for d in subset_001 if d.get('Critical_Fails')])
            fails_002 = len([d for d in subset_002 if d.get('Critical_Fails')])
            
            lines.append(
                f"{label:<25} {pcts_001['Strong']:>6.1f}% (n={total_001:>2}, f={fails_001}) "
                f"{pcts_002['Strong']:>6.1f}% (n={total_002:>2}, f={fails_002}) {change_str:>15}"
            )
    
    return "\n".join(lines)


def compare_model_providers(data_001: list, data_002: list) -> str:
    """Compare model provider performance."""
    provider_001 = analyze_by_model_category(data_001, 'provider')
    provider_002 = analyze_by_model_category(data_002, 'provider')
    
    lines = [f"\n{'='*70}", "MODEL PROVIDER - COMPARISON", f"{'='*70}"]
    lines.append(f"{'Provider':<20} {'Batch 001 Strong%':>20} {'Batch 002 Strong%':>20} {'Change':>15}")
    lines.append("-" * 75)
    
    all_providers = set(provider_001.keys()) | set(provider_002.keys())
    
    for provider in sorted(all_providers):
        counts_001 = provider_001.get(provider, {'Strong': 0, 'total': 0})
        counts_002 = provider_002.get(provider, {'Strong': 0, 'total': 0})
        
        total_001 = counts_001['total']
        total_002 = counts_002['total']
        
        if total_001 > 0 and total_002 > 0:
            strong_pct_001 = (counts_001['Strong'] / total_001) * 100
            strong_pct_002 = (counts_002['Strong'] / total_002) * 100
            change = strong_pct_002 - strong_pct_001
            change_str = f"{change:+.1f}pp" if change != 0 else "0.0pp"
            
            lines.append(
                f"{provider:<20} {strong_pct_001:>6.1f}% (n={total_001:>2}) {strong_pct_002:>6.1f}% (n={total_002:>2}) {change_str:>15}"
            )
    
    return "\n".join(lines)


def generate_comparison_report(data_001: list, data_002: list) -> str:
    """Generate comprehensive comparison report."""
    report_lines = []
    
    report_lines.append("=" * 70)
    report_lines.append("BATCH 001 vs BATCH 002 - COMPARISON REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"\nBatch 001: {len(data_001)} conversations")
    report_lines.append(f"Batch 002: {len(data_002)} conversations")
    
    # Overall comparison
    report_lines.append(compare_overall_distributions(data_001, data_002))
    
    # Critical fails comparison
    fail_001 = analyze_critical_fails(data_001)
    fail_002 = analyze_critical_fails(data_002)
    report_lines.append(compare_critical_fails(fail_001, fail_002))
    
    # Format comparison
    report_lines.append(compare_by_dimension(data_001, data_002, 'format', "FORMAT"))
    
    # Valence comparison
    report_lines.append(compare_by_dimension(data_001, data_002, 'valence', "VALENCE"))
    
    # Treatment type comparison
    report_lines.append(compare_by_dimension(data_001, data_002, 'treatment_type', "TREATMENT TYPE"))
    
    # Treatment × Valence comparison
    report_lines.append(compare_treatment_valence(data_001, data_002))
    
    # Model provider comparison
    report_lines.append(compare_model_providers(data_001, data_002))
    
    # Summary insights
    report_lines.append(f"\n{'='*70}")
    report_lines.append("KEY INSIGHTS")
    report_lines.append(f"{'='*70}")
    
    # Calculate key metrics
    strong_pct_001 = (count_classifications(data_001)['Strong'] / len(data_001)) * 100
    strong_pct_002 = (count_classifications(data_002)['Strong'] / len(data_002)) * 100
    strong_change = strong_pct_002 - strong_pct_001
    
    fail_pct_001 = (fail_001['records_with_any_fail'] / len(data_001)) * 100
    fail_pct_002 = (fail_002['records_with_any_fail'] / len(data_002)) * 100
    fail_change = fail_pct_002 - fail_pct_001
    
    report_lines.append(f"\n1. Overall Strong Performance: {strong_pct_001:.1f}% → {strong_pct_002:.1f}% ({strong_change:+.1f}pp)")
    if strong_change < -5:
        report_lines.append("   ⚠️  SIGNIFICANT DECREASE in Strong performance")
    elif strong_change > 5:
        report_lines.append("   ✓ SIGNIFICANT INCREASE in Strong performance")
    else:
        report_lines.append("   → Relatively stable performance")
    
    report_lines.append(f"\n2. Critical Fails Rate: {fail_pct_001:.1f}% → {fail_pct_002:.1f}% ({fail_change:+.1f}pp)")
    if fail_change > 2:
        report_lines.append("   ⚠️  INCREASE in critical fails - investigate!")
    elif fail_change < -2:
        report_lines.append("   ✓ DECREASE in critical fails")
    else:
        report_lines.append("   → Relatively stable fail rate")
    
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
    
    # Generate comparison report
    report = generate_comparison_report(data_001, data_002)
    print(report)
    
    # Save report
    report_path = batch_results_dir / "batch_comparison_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n\nComparison report saved to {report_path}")


if __name__ == "__main__":
    main()

