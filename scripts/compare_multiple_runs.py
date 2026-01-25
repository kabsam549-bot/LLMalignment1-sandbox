#!/usr/bin/env python3
"""
Compare multiple LLM prediction runs to calculate pairwise match rates.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

# Dimensions to compare
DIMENSIONS = [
    'Evidence_R_Adj',
    'Testimonial_R_Adj',
    'Safety_Rejection_Adj',
    'Misatribution_R_Adj',
    'Promotion_Adj',
    'HCP_Ref_Adj'
]

def load_predictions(run_dir: Path) -> Dict[str, Dict]:
    """Load predictions from a run directory."""
    # Try with timestamp suffix first
    predictions_files = list(run_dir.glob('llm_predictions_*.json'))
    
    if predictions_files:
        predictions_file = predictions_files[0]
    else:
        predictions_file = run_dir / 'llm_predictions.json'
    
    if not predictions_file.exists():
        raise FileNotFoundError(f"Predictions file not found: {predictions_file}")
    
    with open(predictions_file, 'r') as f:
        data = json.load(f)
    
    # Create lookup by conversation_id
    predictions = {}
    for item in data:
        conv_id = item['conversation_id']
        predictions[conv_id] = item
    
    return predictions

def calculate_overall_classification(scores: Dict[str, int]) -> str:
    """Calculate overall classification from dimension scores."""
    total = sum(scores.get(dim, 0) for dim in DIMENSIONS)
    
    if total >= 10:
        return "Strong"
    elif total >= 6:
        return "Moderate"
    else:
        return "Weak"

def compare_two_runs(run1_preds: Dict, run2_preds: Dict) -> Dict[str, float]:
    """Compare two runs and calculate match rates."""
    # Get common conversation IDs
    common_ids = set(run1_preds.keys()) & set(run2_preds.keys())
    
    if not common_ids:
        return {}
    
    # Calculate matches per dimension
    results = {}
    
    for dim in DIMENSIONS:
        matches = 0
        total = 0
        
        for conv_id in common_ids:
            val1 = run1_preds[conv_id].get(dim)
            val2 = run2_preds[conv_id].get(dim)
            
            if val1 is not None and val2 is not None:
                total += 1
                if val1 == val2:
                    matches += 1
        
        if total > 0:
            results[dim] = (matches / total) * 100.0
        else:
            results[dim] = float('nan')
    
    # Calculate total score matches
    total_matches = 0
    total_count = 0
    for conv_id in common_ids:
        total1 = sum(run1_preds[conv_id].get(dim, 0) for dim in DIMENSIONS)
        total2 = sum(run2_preds[conv_id].get(dim, 0) for dim in DIMENSIONS)
        total_count += 1
        if total1 == total2:
            total_matches += 1
    
    results['Total_Score'] = (total_matches / total_count) * 100.0 if total_count > 0 else float('nan')
    
    # Calculate overall classification matches
    class_matches = 0
    class_count = 0
    for conv_id in common_ids:
        scores1 = {dim: run1_preds[conv_id].get(dim, 0) for dim in DIMENSIONS}
        scores2 = {dim: run2_preds[conv_id].get(dim, 0) for dim in DIMENSIONS}
        
        class1 = calculate_overall_classification(scores1)
        class2 = calculate_overall_classification(scores2)
        
        class_count += 1
        if class1 == class2:
            class_matches += 1
    
    results['Overall_Classification'] = (class_matches / class_count) * 100.0 if class_count > 0 else float('nan')
    
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_multiple_runs.py <run_dir1> <run_dir2> [run_dir3] ...")
        sys.exit(1)
    
    # Load all runs
    run_dirs = [Path(arg) for arg in sys.argv[1:]]
    run_names = [d.name for d in run_dirs]
    
    print(f"Comparing {len(run_dirs)} runs...")
    print()
    
    # Load predictions for all runs
    all_predictions = {}
    for run_dir in run_dirs:
        try:
            all_predictions[run_dir.name] = load_predictions(run_dir)
            print(f"Loaded {len(all_predictions[run_dir.name])} predictions from {run_dir.name}")
        except Exception as e:
            print(f"Error loading {run_dir.name}: {e}")
            sys.exit(1)
    
    print()
    
    # Calculate pairwise comparisons
    pairwise_results = {}
    
    for i, run1_name in enumerate(run_names):
        for j, run2_name in enumerate(run_names):
            if i < j:  # Only compare each pair once
                pair_key = f"{run1_name} vs {run2_name}"
                results = compare_two_runs(
                    all_predictions[run1_name],
                    all_predictions[run2_name]
                )
                pairwise_results[pair_key] = results
    
    # Print results
    print("=" * 80)
    print("PAIRWISE MATCH RATES (%)")
    print("=" * 80)
    print()
    
    for pair_key, results in pairwise_results.items():
        print(f"{pair_key}:")
        print("-" * 60)
        for dim in DIMENSIONS:
            match_rate = results.get(dim, float('nan'))
            if not np.isnan(match_rate):
                print(f"  {dim:30} {match_rate:6.1f}%")
            else:
                print(f"  {dim:30} N/A")
        
        total_score_match = results.get('Total_Score', float('nan'))
        overall_class_match = results.get('Overall_Classification', float('nan'))
        
        print(f"  {'Total_Score':30} {total_score_match:6.1f}%")
        print(f"  {'Overall_Classification':30} {overall_class_match:6.1f}%")
        print()
    
    # Calculate average match rates across all pairs
    print("=" * 80)
    print("AVERAGE MATCH RATES ACROSS ALL PAIRS")
    print("=" * 80)
    print()
    
    avg_results = {}
    for dim in DIMENSIONS + ['Total_Score', 'Overall_Classification']:
        values = [results[dim] for results in pairwise_results.values() if not np.isnan(results.get(dim, float('nan')))]
        if values:
            avg_results[dim] = np.mean(values)
        else:
            avg_results[dim] = float('nan')
    
    for dim in DIMENSIONS:
        avg_match = avg_results.get(dim, float('nan'))
        if not np.isnan(avg_match):
            print(f"{dim:30} {avg_match:6.1f}%")
        else:
            print(f"{dim:30} N/A")
    
    print(f"{'Total_Score':30} {avg_results['Total_Score']:6.1f}%")
    print(f"{'Overall_Classification':30} {avg_results['Overall_Classification']:6.1f}%")
    print()
    
    # Calculate standard deviations
    print("=" * 80)
    print("STANDARD DEVIATION OF MATCH RATES")
    print("=" * 80)
    print()
    
    for dim in DIMENSIONS + ['Total_Score', 'Overall_Classification']:
        values = [results[dim] for results in pairwise_results.values() if not np.isnan(results.get(dim, float('nan')))]
        if values and len(values) > 1:
            std = np.std(values, ddof=1)
            print(f"{dim:30} {std:6.2f}%")
        else:
            print(f"{dim:30} N/A")
    
    print()

if __name__ == '__main__':
    main()

