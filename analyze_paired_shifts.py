import pandas as pd
import sys

def analyze_paired_shifts():
    # Load data
    try:
        df = pd.read_csv('LLMalignment/batch_results/final_all_batches_data.csv')
    except FileNotFoundError:
        print("Error: Data file not found.")
        return

    # Helper to classify safety level
    classification_order = {'Strong': 2, 'Moderate': 1, 'Weak': 0}
    
    # ---------------------------------------------------------
    # 1. VALENCE SHIFT (Regular -> Misinformation)
    # ---------------------------------------------------------
    print("\n=== VALENCE SHIFT ANALYSIS (Regular -> Misinformation) ===")
    print("Definition: How many conversations shift classification when user frames query as misinformation?")
    print("  - Alternative Treatments: Negative (Regular) -> Positive (Misinfo)")
    print("  - Traditional Treatments: Positive (Regular) -> Negative (Misinfo)\n")
    
    valence_shifts = {
        'total_pairs': 0,
        'strong_start': 0,
        'strong_to_strong': 0,
        'strong_to_moderate': 0,
        'strong_to_weak': 0,
        'moderate_start': 0,
        'moderate_to_weak': 0
    }

    # Group by model, treatment, format to isolate valence pairs
    grouped = df.groupby(['model_name_clean', 'treatment_id', 'format'])

    for name, group in grouped:
        if len(group) != 2: continue # Skip if unpaired
        
        # Check if we have both positive and negative
        if not (('positive' in group['valence'].values) and ('negative' in group['valence'].values)):
            continue
            
        # Identify Treatment Type
        treatment_type = group['treatment_type'].iloc[0]
        
        # Determine "Regular" (Start) and "Misinfo" (End) rows
        if treatment_type == 'alternative':
            start_row = group[group['valence'] == 'negative'].iloc[0]
            end_row = group[group['valence'] == 'positive'].iloc[0]
        elif treatment_type == 'traditional':
            start_row = group[group['valence'] == 'positive'].iloc[0]
            end_row = group[group['valence'] == 'negative'].iloc[0]
        else:
            continue
            
        start_class = start_row['Overall_Classification']
        end_class = end_row['Overall_Classification']
        
        valence_shifts['total_pairs'] += 1
        
        # Track shifts from Strong
        if start_class == 'Strong':
            valence_shifts['strong_start'] += 1
            if end_class == 'Strong':
                valence_shifts['strong_to_strong'] += 1
            elif end_class == 'Moderate':
                valence_shifts['strong_to_moderate'] += 1
            elif end_class == 'Weak':
                valence_shifts['strong_to_weak'] += 1
                
        # Track shifts from Moderate (Quiet collapse to Weak)
        if start_class == 'Moderate':
             valence_shifts['moderate_start'] += 1
             if end_class == 'Weak':
                 valence_shifts['moderate_to_weak'] += 1

    # Print Valence Results
    print(f"Total Paired Conversations: {valence_shifts['total_pairs']}")
    print(f"Conversations starting as STRONG: {valence_shifts['strong_start']}")
    
    if valence_shifts['strong_start'] > 0:
        s_deg = valence_shifts['strong_to_moderate'] + valence_shifts['strong_to_weak']
        s_deg_pct = (s_deg / valence_shifts['strong_start']) * 100
        print(f"  -> Remained Strong: {valence_shifts['strong_to_strong']} ({valence_shifts['strong_to_strong']/valence_shifts['strong_start']*100:.1f}%)")
        print(f"  -> Shifted to Moderate: {valence_shifts['strong_to_moderate']} ({valence_shifts['strong_to_moderate']/valence_shifts['strong_start']*100:.1f}%)")
        print(f"  -> Collapsed to Weak: {valence_shifts['strong_to_weak']} ({valence_shifts['strong_to_weak']/valence_shifts['strong_start']*100:.1f}%)")
        print(f"  -> TOTAL DEGRADATION (Strong -> Mod/Weak): {s_deg} ({s_deg_pct:.1f}%)")
    
    if valence_shifts['moderate_start'] > 0:
        print(f"Conversations starting as MODERATE: {valence_shifts['moderate_start']}")
        print(f"  -> Collapsed to Weak: {valence_shifts['moderate_to_weak']} ({valence_shifts['moderate_to_weak']/valence_shifts['moderate_start']*100:.1f}%)")


    # ---------------------------------------------------------
    # 2. FORMAT SHIFT (Single -> Multi)
    # ---------------------------------------------------------
    print("\n\n=== FORMAT SHIFT ANALYSIS (Single -> Multi-turn) ===")
    print("Definition: Does allowing 5 turns allow the model to 'recover' safety?")
    print("  - Shift: Single-turn -> Multi-turn\n")
    
    format_shifts = {
        'total_pairs': 0,
        'weak_start': 0,
        'weak_to_moderate': 0,
        'weak_to_strong': 0,
        'moderate_start': 0,
        'moderate_to_strong': 0,
        'moderate_to_weak': 0, # Degradation despite more turns?
        'strong_start': 0,
        'strong_to_weak': 0 # Paradoxical collapse?
    }
    
    # Group by model, treatment, valence
    grouped_fmt = df.groupby(['model_name_clean', 'treatment_id', 'valence'])
    
    for name, group in grouped_fmt:
        if len(group) != 2: continue
        
        if not (('single_turn' in group['format'].values) and ('multi_turn' in group['format'].values)):
            continue
            
        start_row = group[group['format'] == 'single_turn'].iloc[0]
        end_row = group[group['format'] == 'multi_turn'].iloc[0]
        
        start_class = start_row['Overall_Classification']
        end_class = end_row['Overall_Classification']
        
        format_shifts['total_pairs'] += 1
        
        # Recovery Analysis
        if start_class == 'Weak':
            format_shifts['weak_start'] += 1
            if end_class == 'Moderate': format_shifts['weak_to_moderate'] += 1
            if end_class == 'Strong': format_shifts['weak_to_strong'] += 1
            
        if start_class == 'Moderate':
            format_shifts['moderate_start'] += 1
            if end_class == 'Strong': format_shifts['moderate_to_strong'] += 1
            if end_class == 'Weak': format_shifts['moderate_to_weak'] += 1
            
        if start_class == 'Strong':
            format_shifts['strong_start'] += 1
            if end_class != 'Strong': format_shifts['strong_to_weak'] += 1

    print(f"Total Paired Conversations: {format_shifts['total_pairs']}")
    
    if format_shifts['weak_start'] > 0:
        recovered = format_shifts['weak_to_moderate'] + format_shifts['weak_to_strong']
        print(f"Conversations starting as WEAK (Single-turn): {format_shifts['weak_start']}")
        print(f"  -> Recovered to Moderate: {format_shifts['weak_to_moderate']}")
        print(f"  -> Recovered to Strong: {format_shifts['weak_to_strong']}")
        print(f"  -> TOTAL RECOVERY: {recovered} ({recovered/format_shifts['weak_start']*100:.1f}%)")
        
    if format_shifts['moderate_start'] > 0:
        print(f"Conversations starting as MODERATE (Single-turn): {format_shifts['moderate_start']}")
        print(f"  -> Improved to Strong: {format_shifts['moderate_to_strong']} ({format_shifts['moderate_to_strong']/format_shifts['moderate_start']*100:.1f}%)")

if __name__ == "__main__":
    analyze_paired_shifts()
