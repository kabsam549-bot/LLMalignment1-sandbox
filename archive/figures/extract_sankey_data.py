import pandas as pd
import json

def extract_all_transitions():
    """
    Extract all classification transitions from Evidence-aligned to Misconception framing.
    This is the valence shift analysis (Regular -> Misinformation).
    """
    # Load data
    df = pd.read_csv('batch_results/final_all_batches_data.csv')
    
    # Initialize transition matrix
    transitions = {
        'Strong->Strong': 0,
        'Strong->Moderate': 0,
        'Strong->Weak': 0,
        'Moderate->Strong': 0,
        'Moderate->Moderate': 0,
        'Moderate->Weak': 0,
        'Weak->Strong': 0,
        'Weak->Moderate': 0,
        'Weak->Weak': 0
    }
    
    # Group by model, treatment, format to isolate valence pairs
    grouped = df.groupby(['model_name_clean', 'treatment_id', 'format'])
    
    for name, group in grouped:
        if len(group) != 2:
            continue
        
        # Check if we have both positive and negative valence
        if not (('positive' in group['valence'].values) and ('negative' in group['valence'].values)):
            continue
        
        # Identify Treatment Type
        treatment_type = group['treatment_type'].iloc[0]
        
        # Determine "Evidence-aligned" (Start) and "Misconception" (End) rows
        # For alternative treatments: negative = evidence-aligned (questioning), positive = misconception (promoting)
        # For traditional treatments: positive = evidence-aligned (asking about), negative = misconception (attacking)
        if treatment_type == 'alternative':
            start_row = group[group['valence'] == 'negative'].iloc[0]  # Evidence-aligned
            end_row = group[group['valence'] == 'positive'].iloc[0]    # Misconception
        elif treatment_type == 'traditional':
            start_row = group[group['valence'] == 'positive'].iloc[0]  # Evidence-aligned
            end_row = group[group['valence'] == 'negative'].iloc[0]    # Misconception
        else:
            continue
        
        start_class = start_row['Overall_Classification']
        end_class = end_row['Overall_Classification']
        
        # Record transition
        transition_key = f"{start_class}->{end_class}"
        if transition_key in transitions:
            transitions[transition_key] += 1
    
    # Calculate totals for each starting classification
    totals = {
        'Strong': sum(v for k, v in transitions.items() if k.startswith('Strong')),
        'Moderate': sum(v for k, v in transitions.items() if k.startswith('Moderate')),
        'Weak': sum(v for k, v in transitions.items() if k.startswith('Weak'))
    }
    
    # Create structured output for Sankey diagram
    sankey_data = {
        'title': 'Classification Transitions Under Misconception Framing',
        'description': 'Flow from Evidence-aligned classification to Misconception framing classification',
        'transitions': transitions,
        'totals': totals,
        'flows': []
    }
    
    # Add individual flows for Sankey
    for transition_key, count in transitions.items():
        if count > 0:  # Only include non-zero flows
            start, end = transition_key.split('->')
            sankey_data['flows'].append({
                'source': start,
                'target': end,
                'value': count
            })
    
    return sankey_data

if __name__ == "__main__":
    data = extract_all_transitions()
    
    # Print summary
    print("\n=== CLASSIFICATION TRANSITIONS: Evidence-aligned → Misconception Framing ===\n")
    print(f"Total conversations by starting classification:")
    for classification, total in data['totals'].items():
        print(f"  {classification}: {total}")
    
    print("\nAll transitions:")
    for transition, count in data['transitions'].items():
        if count > 0:
            start, end = transition.split('->')
            total = data['totals'][start]
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {transition}: {count} ({percentage:.1f}%)")
    
    # Save to JSON
    output_path = 'figures/sankey_data.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Data saved to {output_path}")
