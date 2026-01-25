
import pandas as pd
import numpy as np
import os
import sys

# Define constants based on repo nomenclature
DATA_PATH = 'LLMalignment/batch_results/final_all_batches_data.csv'
OUTPUT_DIR = 'LLMalignment/results/reanalysis_2026_01_23'

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        sys.exit(1)
    return pd.read_csv(DATA_PATH)

def define_groups(df):
    """
    Define analysis groups based on the 2x2x2 design.
    """
    # Create explicit flags if they don't exist
    if 'is_misinfo' not in df.columns:
        # Misinformation = (Alternative + Positive) OR (Traditional + Negative)
        # Regular = (Alternative + Negative) OR (Traditional + Positive)
        
        # Helper conditions
        cond_alt_pos = (df['treatment_type'] == 'alternative') & (df['valence'] == 'positive')
        cond_trad_neg = (df['treatment_type'] == 'traditional') & (df['valence'] == 'negative')
        
        df['is_misinfo'] = cond_alt_pos | cond_trad_neg
    
    return df

def analyze_sycophancy(df):
    """
    Fig 1: Misinformation vs Regular Information
    Primary Metric: 'Weak' rate (Combined Unsafe)
    """
    print("\n=== SYCOPHANCY ANALYSIS (Fig 1) ===")
    
    # Group by Misinfo Status
    grouped = df.groupby('is_misinfo')['Overall_Classification'].value_counts(normalize=True).unstack().fillna(0)
    
    # Calculate 'Unsafe' (Weak) rate
    # Assuming 'Weak' captures Critical Failures as per scorer.py logic
    unsafe_rates = grouped['Weak'] * 100
    
    print("Unsafe (Weak) Rates:")
    print(f"  Regular Info:       {unsafe_rates[False]:.2f}%")
    print(f"  Misinformation:     {unsafe_rates[True]:.2f}%")
    
    # Calculate Odds Ratio
    misinfo_n = df['is_misinfo'].sum()
    regular_n = (~df['is_misinfo']).sum()
    
    misinfo_weak = df[df['is_misinfo']]['Overall_Classification'].eq('Weak').sum()
    regular_weak = df[~df['is_misinfo']]['Overall_Classification'].eq('Weak').sum()
    
    print(f"\n  Counts (Unsafe / Total):")
    print(f"  Regular:    {regular_weak}/{regular_n}")
    print(f"  Misinfo:    {misinfo_weak}/{misinfo_n}")
    
    return unsafe_rates

def analyze_guardrails(df):
    """
    Fig 3: Single-turn vs Multi-turn (The Guardrail)
    Metric: 'Weak' rate
    """
    print("\n=== GUARDRAIL ANALYSIS (Fig 3) ===")
    
    grouped = df.groupby('format')['Overall_Classification'].value_counts(normalize=True).unstack().fillna(0)
    unsafe_rates = grouped['Weak'] * 100
    
    print("Unsafe (Weak) Rates by Format:")
    print(f"  Single-turn: {unsafe_rates.get('single_turn', 0):.2f}%")
    print(f"  Multi-turn:  {unsafe_rates.get('multi_turn', 0):.2f}%")
    
    # Interaction: Does Multi-turn protect specifically against Misinfo?
    print("\n  Interaction: Format x Misinfo Framing")
    interaction = df.groupby(['format', 'is_misinfo'])['Overall_Classification'].value_counts(normalize=True).unstack().fillna(0)
    
    # Check if 'Weak' exists in the interaction columns (it might be missing if 0 errors)
    if 'Weak' in interaction.columns:
        print(interaction['Weak'] * 100)
    else:
        print("  No 'Weak' classifications found in one or more subgroups.")

def analyze_safety_erosion(df):
    """
    Fig 2: Erosion (Shift from Strong -> Moderate/Weak)
    This requires paired data (same model, same treatment, diff valence).
    """
    print("\n=== EROSION ANALYSIS (Fig 2 - Paired) ===")
    
    # Only keep paired rows (we need to pivot)
    # Pivot on valence: We want to see shift from 'Safe' (Regular) -> 'Misinfo' (Framing)
    # But Regular/Misinfo valence depends on treatment type.
    
    erosion_stats = {
        'strong_to_strong': 0,
        'strong_to_mod': 0,
        'strong_to_weak': 0,
        'total_strong_start': 0
    }
    
    # We need to iterate groups to find pairs
    grouped_pairs = df.groupby(['model_name_clean', 'treatment_id', 'format'])
    
    for _, group in grouped_pairs:
        if len(group) != 2: continue
        
        # Identify the "Regular" and "Misinfo" rows
        if group['treatment_type'].iloc[0] == 'alternative':
            reg = group[group['valence'] == 'negative']
            mis = group[group['valence'] == 'positive']
        else: # Traditional
            reg = group[group['valence'] == 'positive']
            mis = group[group['valence'] == 'negative']
            
        if reg.empty or mis.empty: continue
        
        reg_class = reg['Overall_Classification'].iloc[0]
        mis_class = mis['Overall_Classification'].iloc[0]
        
        if reg_class == 'Strong':
            erosion_stats['total_strong_start'] += 1
            if mis_class == 'Strong': erosion_stats['strong_to_strong'] += 1
            elif mis_class == 'Moderate': erosion_stats['strong_to_mod'] += 1
            elif mis_class == 'Weak': erosion_stats['strong_to_weak'] += 1
            
    print(f"Total starting as Strong (Regular context): {erosion_stats['total_strong_start']}")
    if erosion_stats['total_strong_start'] > 0:
        print(f"  -> Stayed Strong: {erosion_stats['strong_to_strong']} ({erosion_stats['strong_to_strong']/erosion_stats['total_strong_start']:.1%})")
        print(f"  -> Eroded to Moderate: {erosion_stats['strong_to_mod']} ({erosion_stats['strong_to_mod']/erosion_stats['total_strong_start']:.1%})")
        print(f"  -> Collapsed to Weak: {erosion_stats['strong_to_weak']} ({erosion_stats['strong_to_weak']/erosion_stats['total_strong_start']:.1%})")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading data...")
    df = load_data()
    df = define_groups(df)
    
    analyze_sycophancy(df)
    analyze_erosion(df) # Fixed function name call
    analyze_guardrails(df)
    
    print(f"\nAnalysis complete. Results ready for visualization.")

# Fix function name alias for the call
analyze_erosion = analyze_safety_erosion

if __name__ == "__main__":
    main()
