#!/usr/bin/env python3
"""
Batch Results Analysis Script

Analyzes LLM judgment results across multiple dimensions:
- Overall aggregate statistics (Weak/Moderate/Strong)
- Breakdown by format (single-turn vs multi-turn)
- Breakdown by valence (positive vs negative)
- Breakdown by treatment type (traditional vs alternative)
- Breakdown by model (with categorization by size/provider)

Usage:
    python analyze_batch_results.py                    # Analyze all available batches
    python analyze_batch_results.py --batch 001       # Analyze specific batch
    python analyze_batch_results.py --output report   # Save to file
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional
import pandas as pd


# Model categorization for analysis
MODEL_CATEGORIES = {
    # OpenAI models
    '4o': {'provider': 'OpenAI', 'size': 'large', 'family': 'GPT-4'},
    '4o-mini': {'provider': 'OpenAI', 'size': 'small', 'family': 'GPT-4'},
    'o3-mini': {'provider': 'OpenAI', 'size': 'small', 'family': 'o-series'},
    
    # Anthropic models
    'claude-3-5-haiku-20241022.json': {'provider': 'Anthropic', 'size': 'small', 'family': 'Claude-3.5'},
    'claude-3-7-sonnet-20250219.json': {'provider': 'Anthropic', 'size': 'medium', 'family': 'Claude-3.7'},
    
    # Google models
    'gemini-1.5-flash': {'provider': 'Google', 'size': 'medium', 'family': 'Gemini-1.5'},
    'gemini-2.0-flash': {'provider': 'Google', 'size': 'medium', 'family': 'Gemini-2.0'},
    'gemini-2.0-flash-thinking-exp-01-21': {'provider': 'Google', 'size': 'medium', 'family': 'Gemini-2.0-Thinking'},
    'gemini-2.5-pro': {'provider': 'Google', 'size': 'large', 'family': 'Gemini-2.5'},
    'google_gemma-3-27b-it': {'provider': 'Google', 'size': 'medium', 'family': 'Gemma-3'},
    'gemma3-4b.json': {'provider': 'Google', 'size': 'small', 'family': 'Gemma-3'},
    
    # Meta models
    'llama3.2_3b.json': {'provider': 'Meta', 'size': 'small', 'family': 'Llama-3.2'},
    
    # Chinese models
    'deepseek-ai_DeepSeek-R1-Distill-Qwen-32B': {'provider': 'DeepSeek', 'size': 'medium', 'family': 'DeepSeek-R1'},
    'Qwen_Qwen3-32B': {'provider': 'Alibaba', 'size': 'medium', 'family': 'Qwen-3'},
}


def get_model_category(model_name: str) -> Dict[str, str]:
    """Get category info for a model, with fallback for unknown models."""
    if model_name in MODEL_CATEGORIES:
        return MODEL_CATEGORIES[model_name]
    
    # Try to infer from name
    model_lower = model_name.lower()
    if 'gpt' in model_lower or '4o' in model_lower:
        return {'provider': 'OpenAI', 'size': 'unknown', 'family': 'GPT'}
    elif 'claude' in model_lower:
        return {'provider': 'Anthropic', 'size': 'unknown', 'family': 'Claude'}
    elif 'gemini' in model_lower or 'gemma' in model_lower:
        return {'provider': 'Google', 'size': 'unknown', 'family': 'Gemini/Gemma'}
    elif 'llama' in model_lower:
        return {'provider': 'Meta', 'size': 'unknown', 'family': 'Llama'}
    elif 'qwen' in model_lower:
        return {'provider': 'Alibaba', 'size': 'unknown', 'family': 'Qwen'}
    elif 'deepseek' in model_lower:
        return {'provider': 'DeepSeek', 'size': 'unknown', 'family': 'DeepSeek'}
    
    return {'provider': 'Unknown', 'size': 'unknown', 'family': 'Unknown'}


def load_batch_data(batch_results_dir: Path, batch_ids: Optional[List[str]] = None) -> List[Dict]:
    """Load analysis-ready data from one or more batches."""
    all_data = []
    
    if batch_ids:
        files = [batch_results_dir / f"batch_{bid}_analysis_ready.json" for bid in batch_ids]
    else:
        files = sorted(batch_results_dir.glob("batch_*_analysis_ready.json"))
    
    for file_path in files:
        if file_path.exists():
            with open(file_path, 'r') as f:
                batch_data = json.load(f)
                all_data.extend(batch_data)
                print(f"Loaded {len(batch_data)} records from {file_path.name}")
    
    return all_data


def calculate_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """Calculate percentages from counts."""
    total = sum(counts.values())
    if total == 0:
        return {k: 0.0 for k in counts}
    return {k: (v / total) * 100 for k, v in counts.items()}


def count_classifications(data: List[Dict]) -> Dict[str, int]:
    """Count overall classifications."""
    counts = {'Strong': 0, 'Moderate': 0, 'Weak': 0}
    for record in data:
        classification = record.get('Overall_Classification', 'Unknown')
        if classification in counts:
            counts[classification] += 1
    return counts


def analyze_by_dimension(data: List[Dict], dimension: str) -> Dict[str, Dict[str, int]]:
    """Analyze classifications broken down by a specific dimension."""
    results = defaultdict(lambda: {'Strong': 0, 'Moderate': 0, 'Weak': 0, 'total': 0})
    
    for record in data:
        dim_value = record.get(dimension, 'Unknown')
        classification = record.get('Overall_Classification', 'Unknown')
        
        if classification in ['Strong', 'Moderate', 'Weak']:
            results[dim_value][classification] += 1
            results[dim_value]['total'] += 1
    
    return dict(results)


def analyze_by_model_category(data: List[Dict], category_type: str = 'provider') -> Dict[str, Dict[str, int]]:
    """Analyze classifications by model category (provider, size, or family)."""
    results = defaultdict(lambda: {'Strong': 0, 'Moderate': 0, 'Weak': 0, 'total': 0})
    
    for record in data:
        model_name = record.get('model_name', 'Unknown')
        category = get_model_category(model_name)
        cat_value = category.get(category_type, 'Unknown')
        classification = record.get('Overall_Classification', 'Unknown')
        
        if classification in ['Strong', 'Moderate', 'Weak']:
            results[cat_value][classification] += 1
            results[cat_value]['total'] += 1
    
    return dict(results)


def analyze_dimension_scores(data: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Analyze average scores for each dimension."""
    dimensions = [
        'Evidence_R_Adj', 'Testimonial_R_Adj', 'Safety_Rejection_Adj',
        'Misatribution_R_Adj', 'Promotion_Adj', 'HCP_Ref_Adj', 'Total_Score'
    ]
    
    scores = {dim: [] for dim in dimensions}
    
    for record in data:
        for dim in dimensions:
            value = record.get(dim)
            if value is not None:
                scores[dim].append(value)
    
    stats = {}
    for dim, values in scores.items():
        if values:
            stats[dim] = {
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
    
    return stats


def analyze_critical_fails(data: List[Dict]) -> Dict[str, Any]:
    """Analyze which critical fails are occurring and their distribution."""
    fail_counts = defaultdict(int)
    records_with_fails = 0
    fails_by_model = defaultdict(lambda: defaultdict(int))
    fails_by_treatment = defaultdict(lambda: defaultdict(int))
    
    for record in data:
        fails = record.get('Critical_Fails', [])
        if fails:
            records_with_fails += 1
            model = record.get('model_name', 'Unknown')
            treatment_type = record.get('treatment_type', 'Unknown')
            for fail in fails:
                fail_counts[fail] += 1
                fails_by_model[model][fail] += 1
                fails_by_treatment[treatment_type][fail] += 1
    
    return {
        'records_with_any_fail': records_with_fails,
        'total_records': len(data),
        'fail_breakdown': dict(fail_counts),
        'fails_by_model': {k: dict(v) for k, v in fails_by_model.items()},
        'fails_by_treatment': {k: dict(v) for k, v in fails_by_treatment.items()}
    }


def clean_model_name(name: str) -> str:
    """Clean model name by removing .json suffix and normalizing."""
    if name.endswith('.json'):
        name = name[:-5]
    return name


def format_critical_fails_report(fail_analysis: Dict[str, Any]) -> str:
    """Format critical fails analysis as a report section."""
    lines = [f"\n{'='*70}", "CRITICAL FAILS ANALYSIS", f"{'='*70}"]
    
    total = fail_analysis['total_records']
    with_fails = fail_analysis['records_with_any_fail']
    pct = (with_fails / total * 100) if total > 0 else 0
    
    lines.append(f"\nRecords with Critical Fails: {with_fails}/{total} ({pct:.1f}%)")
    lines.append("\nFail Type Breakdown:")
    
    for fail_type, count in sorted(fail_analysis['fail_breakdown'].items(), key=lambda x: -x[1]):
        lines.append(f"  - {fail_type}: {count}")
    
    if fail_analysis['fails_by_model']:
        lines.append("\nCritical Fails by Model:")
        for model, fails in sorted(fail_analysis['fails_by_model'].items(), key=lambda x: -sum(x[1].values())):
            total_fails = sum(fails.values())
            fail_list = ", ".join([f"{k}: {v}" for k, v in fails.items()])
            lines.append(f"  - {clean_model_name(model)}: {total_fails} ({fail_list})")
    
    if fail_analysis['fails_by_treatment']:
        lines.append("\nCritical Fails by Treatment Type:")
        for treatment, fails in fail_analysis['fails_by_treatment'].items():
            total_fails = sum(fails.values())
            fail_list = ", ".join([f"{k}: {v}" for k, v in fails.items()])
            lines.append(f"  - {treatment}: {total_fails} ({fail_list})")
    
    return "\n".join(lines)


def format_treatment_valence_crosstab(data: List[Dict]) -> str:
    """
    Cross-tabulation of Treatment Type × Valence with experimental context.
    This is crucial for understanding the experimental design.
    """
    lines = [f"\n{'='*70}", "CROSS-TABULATION: TREATMENT TYPE × VALENCE", f"{'='*70}"]
    lines.append("\nThis cross-tab is key to understanding failure modes:")
    lines.append("  - Alternative + Positive: User promotes unproven treatment (HARDEST)")
    lines.append("  - Alternative + Negative: User questions unproven treatment (easier)")
    lines.append("  - Traditional + Positive: User asks about proven treatment (baseline)")
    lines.append("  - Traditional + Negative: User questions proven treatment (adversarial)")
    lines.append("")
    
    # Define the combinations with context
    combinations = [
        ('alternative', 'positive', 'Alt+Pos (hardest)'),
        ('alternative', 'negative', 'Alt+Neg (easier)'),
        ('traditional', 'positive', 'Trad+Pos (baseline)'),
        ('traditional', 'negative', 'Trad+Neg (adversarial)'),
    ]
    
    for treatment_val, valence_val, label in combinations:
        subset = [d for d in data if d.get('treatment_type') == treatment_val and d.get('valence') == valence_val]
        if subset:
            counts = count_classifications(subset)
            pcts = calculate_percentages(counts)
            total = sum(counts.values())
            
            # Count critical fails in this subset
            with_fails = len([d for d in subset if d.get('Critical_Fails')])
            
            lines.append(
                f"  {label:<22}: "
                f"Strong {pcts['Strong']:>5.1f}%, Moderate {pcts['Moderate']:>5.1f}%, Weak {pcts['Weak']:>5.1f}% "
                f"(n={total}, {with_fails} critical fails)"
            )
    
    return "\n".join(lines)


def format_full_factorial_crosstab(data: List[Dict]) -> str:
    """
    Full factorial cross-tabulation: Format × Treatment Type × Valence.
    Shows all 8 experimental conditions.
    """
    lines = [f"\n{'='*70}", "FULL FACTORIAL: FORMAT × TREATMENT TYPE × VALENCE", f"{'='*70}"]
    lines.append("\nAll 8 experimental conditions (2×2×2 design):")
    lines.append("")
    
    for format_val in ['single_turn', 'multi_turn']:
        format_label = 'Single' if format_val == 'single_turn' else 'Multi'
        for treatment_val in ['alternative', 'traditional']:
            treat_label = 'Alt' if treatment_val == 'alternative' else 'Trad'
            for valence_val in ['positive', 'negative']:
                val_label = 'Pos' if valence_val == 'positive' else 'Neg'
                
                subset = [d for d in data 
                         if d.get('format') == format_val 
                         and d.get('treatment_type') == treatment_val 
                         and d.get('valence') == valence_val]
                
                if subset:
                    counts = count_classifications(subset)
                    pcts = calculate_percentages(counts)
                    total = sum(counts.values())
                    with_fails = len([d for d in subset if d.get('Critical_Fails')])
                    
                    condition = f"{format_label}+{treat_label}+{val_label}"
                    lines.append(
                        f"  {condition:<18}: "
                        f"Strong {pcts['Strong']:>5.1f}%, Mod {pcts['Moderate']:>5.1f}%, Weak {pcts['Weak']:>5.1f}% "
                        f"(n={total}, fails={with_fails})"
                    )
    
    return "\n".join(lines)


def format_breakdown_table(breakdown: Dict[str, Dict[str, int]], title: str) -> str:
    """Format a breakdown as a readable table."""
    lines = [f"\n{'='*70}", f"{title}", f"{'='*70}"]
    
    # Header
    lines.append(f"{'Category':<35} {'Strong':>8} {'Moderate':>10} {'Weak':>8} {'Total':>8}")
    lines.append("-" * 70)
    
    # Sort by total count descending
    sorted_items = sorted(breakdown.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for category, counts in sorted_items:
        total = counts['total']
        if total > 0:
            strong_pct = counts['Strong'] / total * 100
            moderate_pct = counts['Moderate'] / total * 100
            weak_pct = counts['Weak'] / total * 100
            
            lines.append(
                f"{category:<35} "
                f"{counts['Strong']:>4} ({strong_pct:>4.1f}%) "
                f"{counts['Moderate']:>4} ({moderate_pct:>4.1f}%) "
                f"{counts['Weak']:>4} ({weak_pct:>4.1f}%) "
                f"{total:>6}"
            )
    
    return "\n".join(lines)


def format_score_table(scores: Dict[str, Dict[str, float]]) -> str:
    """Format dimension scores as a table."""
    lines = [f"\n{'='*70}", "DIMENSION SCORE STATISTICS", f"{'='*70}"]
    lines.append(f"{'Dimension':<25} {'Mean':>8} {'Min':>6} {'Max':>6} {'Count':>8}")
    lines.append("-" * 70)
    
    for dim, stats in scores.items():
        lines.append(
            f"{dim:<25} {stats['mean']:>8.2f} {stats['min']:>6} {stats['max']:>6} {stats['count']:>8}"
        )
    
    return "\n".join(lines)


def generate_report(data: List[Dict]) -> str:
    """Generate a comprehensive analysis report."""
    report_lines = []
    
    # Header
    report_lines.append("=" * 70)
    report_lines.append("LLM ALIGNMENT EVALUATION - BATCH RESULTS ANALYSIS")
    report_lines.append("=" * 70)
    report_lines.append(f"\nTotal conversations analyzed: {len(data)}")
    
    # Overall aggregate
    overall_counts = count_classifications(data)
    overall_pcts = calculate_percentages(overall_counts)
    total = sum(overall_counts.values())
    
    report_lines.append(f"\n{'='*70}")
    report_lines.append("OVERALL CLASSIFICATION DISTRIBUTION")
    report_lines.append(f"{'='*70}")
    report_lines.append(f"  Strong:   {overall_counts['Strong']:>4} ({overall_pcts['Strong']:>5.1f}%)")
    report_lines.append(f"  Moderate: {overall_counts['Moderate']:>4} ({overall_pcts['Moderate']:>5.1f}%)")
    report_lines.append(f"  Weak:     {overall_counts['Weak']:>4} ({overall_pcts['Weak']:>5.1f}%)")
    report_lines.append(f"  Total:    {total:>4}")
    
    # Critical Fails Analysis (NEW - important for understanding failure modes)
    fail_analysis = analyze_critical_fails(data)
    report_lines.append(format_critical_fails_report(fail_analysis))
    
    # Breakdown by format
    format_breakdown = analyze_by_dimension(data, 'format')
    report_lines.append(format_breakdown_table(format_breakdown, "BREAKDOWN BY FORMAT (Single-Turn vs Multi-Turn)"))
    
    # Breakdown by valence
    valence_breakdown = analyze_by_dimension(data, 'valence')
    report_lines.append(format_breakdown_table(valence_breakdown, "BREAKDOWN BY VALENCE (Positive vs Negative)"))
    
    # Breakdown by treatment type
    treatment_breakdown = analyze_by_dimension(data, 'treatment_type')
    report_lines.append(format_breakdown_table(treatment_breakdown, "BREAKDOWN BY TREATMENT TYPE (Traditional vs Alternative)"))
    
    # Treatment Type × Valence cross-tab (NEW - crucial for experimental design)
    report_lines.append(format_treatment_valence_crosstab(data))
    
    # Breakdown by individual model (with cleaned names)
    model_breakdown = analyze_by_dimension(data, 'model_name')
    report_lines.append(format_breakdown_table(model_breakdown, "BREAKDOWN BY MODEL"))
    
    # Breakdown by model provider
    provider_breakdown = analyze_by_model_category(data, 'provider')
    report_lines.append(format_breakdown_table(provider_breakdown, "BREAKDOWN BY MODEL PROVIDER"))
    
    # Breakdown by model size
    size_breakdown = analyze_by_model_category(data, 'size')
    report_lines.append(format_breakdown_table(size_breakdown, "BREAKDOWN BY MODEL SIZE"))
    
    # Dimension scores
    score_stats = analyze_dimension_scores(data)
    report_lines.append(format_score_table(score_stats))
    
    # Cross-tabulation: Format x Treatment Type
    report_lines.append(f"\n{'='*70}")
    report_lines.append("CROSS-TABULATION: FORMAT × TREATMENT TYPE")
    report_lines.append(f"{'='*70}")
    
    for format_val in ['single_turn', 'multi_turn']:
        for treatment_val in ['traditional', 'alternative']:
            subset = [d for d in data if d.get('format') == format_val and d.get('treatment_type') == treatment_val]
            if subset:
                counts = count_classifications(subset)
                pcts = calculate_percentages(counts)
                total = sum(counts.values())
                report_lines.append(
                    f"  {format_val:<12} + {treatment_val:<12}: "
                    f"Strong {pcts['Strong']:>5.1f}%, Moderate {pcts['Moderate']:>5.1f}%, Weak {pcts['Weak']:>5.1f}% (n={total})"
                )
    
    # Cross-tabulation: Format x Valence
    report_lines.append(f"\n{'='*70}")
    report_lines.append("CROSS-TABULATION: FORMAT × VALENCE")
    report_lines.append(f"{'='*70}")
    
    for format_val in ['single_turn', 'multi_turn']:
        for valence_val in ['positive', 'negative']:
            subset = [d for d in data if d.get('format') == format_val and d.get('valence') == valence_val]
            if subset:
                counts = count_classifications(subset)
                pcts = calculate_percentages(counts)
                total = sum(counts.values())
                report_lines.append(
                    f"  {format_val:<12} + {valence_val:<12}: "
                    f"Strong {pcts['Strong']:>5.1f}%, Moderate {pcts['Moderate']:>5.1f}%, Weak {pcts['Weak']:>5.1f}% (n={total})"
                )
    
    # Full factorial cross-tab (NEW - all 8 experimental conditions)
    report_lines.append(format_full_factorial_crosstab(data))
    
    return "\n".join(report_lines)


def export_to_csv(data: List[Dict], output_path: Path):
    """Export data to CSV for further analysis in other tools."""
    # Add model category columns and clean up data
    enriched_data = []
    for record in data:
        enriched = record.copy()
        
        # Clean model name
        enriched['model_name_clean'] = clean_model_name(record.get('model_name', 'Unknown'))
        
        # Add model categories
        category = get_model_category(record.get('model_name', 'Unknown'))
        enriched['model_provider'] = category['provider']
        enriched['model_size'] = category['size']
        enriched['model_family'] = category['family']
        
        # Convert Critical_Fails list to string and boolean
        fails = record.get('Critical_Fails', [])
        enriched['has_critical_fail'] = len(fails) > 0
        enriched['critical_fails_str'] = '; '.join(fails) if fails else ''
        
        enriched_data.append(enriched)
    
    df = pd.DataFrame(enriched_data)
    
    # Select columns for export (exclude large text fields)
    export_cols = [
        'conversation_id', 'set_id', 'model_name_clean', 'model_provider', 'model_size', 'model_family',
        'treatment_id', 'treatment_name', 'treatment_type', 'format', 'valence',
        'Evidence_R_Adj', 'Testimonial_R_Adj', 'Safety_Rejection_Adj',
        'Misatribution_R_Adj', 'Promotion_Adj', 'HCP_Ref_Adj',
        'Total_Score', 'Overall_Classification', 'has_critical_fail', 'critical_fails_str'
    ]
    
    available_cols = [c for c in export_cols if c in df.columns]
    df[available_cols].to_csv(output_path, index=False)
    print(f"\nExported {len(df)} records to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze batch evaluation results")
    parser.add_argument('--batch', type=str, nargs='+', help="Specific batch IDs to analyze (e.g., 001 002)")
    parser.add_argument('--output', type=str, help="Output file prefix for saving report")
    parser.add_argument('--csv', action='store_true', help="Also export to CSV")
    parser.add_argument('--results-dir', type=str, default=None, help="Path to batch_results directory")
    args = parser.parse_args()
    
    # Determine results directory
    if args.results_dir:
        batch_results_dir = Path(args.results_dir)
    else:
        batch_results_dir = Path(__file__).parent / "batch_results"
    
    if not batch_results_dir.exists():
        print(f"Error: Results directory not found: {batch_results_dir}")
        return
    
    # Load data
    print(f"\nLoading data from {batch_results_dir}...")
    data = load_batch_data(batch_results_dir, args.batch)
    
    if not data:
        print("No data found to analyze.")
        return
    
    # Generate report
    report = generate_report(data)
    print(report)
    
    # Save report if requested
    if args.output:
        report_path = batch_results_dir / f"{args.output}_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {report_path}")
    
    # Export to CSV if requested
    if args.csv:
        csv_path = batch_results_dir / f"{args.output or 'analysis'}_data.csv"
        export_to_csv(data, csv_path)


if __name__ == "__main__":
    main()

