#!/usr/bin/env python3
"""
Generate Sankey Diagrams for LLM Alignment Study
- Figure 4A: Classification transitions under misconception framing (NEW)
- Legacy: Valence shift sankey (original version)

Usage:
    python generate_sankey.py [figure4a|legacy]
    
Default: Generates Figure 4A (uses figures/generate_sankey.py)
"""

import sys
from pathlib import Path

def main():
    # Determine which diagram to generate
    mode = sys.argv[1] if len(sys.argv) > 1 else "figure4a"
    
    if mode == "figure4a":
        print("Generating Figure 4A: Classification Transitions Under Misconception Framing")
        print("=" * 70)
        
        # Import and run the Figure 4A generator
        import subprocess
        result = subprocess.run(
            ["python3", "figures/generate_sankey.py"],
            cwd=str(Path(__file__).parent),
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✓ Figure 4A generated successfully!")
            print("  Files created in figures/ directory:")
            print("    - Figure4A_Sankey.html (interactive)")
            print("    - Figure4A_Sankey.png (publication)")
            print("    - Figure4A_Sankey.pdf (publication)")
        else:
            print("\n✗ Error generating Figure 4A")
            sys.exit(1)
            
    elif mode == "legacy":
        print("Generating Legacy Valence Shift Sankey")
        print("=" * 70)
        generate_valence_sankey_legacy()
        
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python generate_sankey.py [figure4a|legacy]")
        sys.exit(1)

def generate_valence_sankey_legacy():
    """Legacy function - kept for backwards compatibility"""
    import pandas as pd
    import plotly.graph_objects as go
    
    # Load data
    try:
        df = pd.read_csv('batch_results/final_all_batches_data.csv')
    except FileNotFoundError:
        print("Error: Data file not found.")
        return

    # Helper for indexing
    class_map = {'Strong': 0, 'Moderate': 1, 'Weak': 2}
    class_labels = ['Strong', 'Moderate', 'Weak']
    
    # Initialize flow counts
    flows = {} # key: (start_idx, end_idx), value: count

    # Group by model, treatment, format to isolate valence pairs
    grouped = df.groupby(['model_name_clean', 'treatment_id', 'format'])

    for name, group in grouped:
        if len(group) != 2: continue 
        
        if not (('positive' in group['valence'].values) and ('negative' in group['valence'].values)):
            continue
            
        treatment_type = group['treatment_type'].iloc[0]
        
        # Determine Regular (Source) -> Misinfo (Target)
        if treatment_type == 'alternative':
            start_row = group[group['valence'] == 'negative'].iloc[0] # Regular (Questioning Alt)
            end_row = group[group['valence'] == 'positive'].iloc[0]   # Misinfo (Promoting Alt)
        elif treatment_type == 'traditional':
            start_row = group[group['valence'] == 'positive'].iloc[0] # Regular (Asking Trad)
            end_row = group[group['valence'] == 'negative'].iloc[0]   # Misinfo (Attacking Trad)
        else:
            continue
            
        start_idx = class_map.get(start_row['Overall_Classification'])
        end_idx = class_map.get(end_row['Overall_Classification'])
        
        if start_idx is None or end_idx is None: continue

        key = (start_idx, end_idx)
        flows[key] = flows.get(key, 0) + 1

    # Prepare Sankey Data
    # Source nodes: 0, 1, 2 (Regular: Strong, Mod, Weak)
    # Target nodes: 3, 4, 5 (Misinfo: Strong, Mod, Weak)
    
    sources = []
    targets = []
    values = []
    
    # Map flows to node indices
    for (start, end), count in flows.items():
        sources.append(start)      # 0-2
        targets.append(end + 3)    # 3-5
        values.append(count)

    # Colors
    # Strong: Green, Mod: Orange, Weak: Red
    node_colors = [
        '#2E7D32', '#F57C00', '#C62828',  # Regular (Left)
        '#2E7D32', '#F57C00', '#C62828'   # Misinfo (Right)
    ]
    
    link_colors = []
    for src in sources:
        # Color links by their SOURCE state
        if src == 0: link_colors.append('rgba(46, 125, 50, 0.4)')   # Greenish
        elif src == 1: link_colors.append('rgba(245, 124, 0, 0.4)') # Orangish
        else: link_colors.append('rgba(198, 40, 40, 0.4)')          # Reddish

    # Create Plot
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = ["Strong", "Moderate", "Weak", "Strong", "Moderate", "Weak"],
          color = node_colors
        ),
        link = dict(
          source = sources,
          target = targets,
          value = values,
          color = link_colors
        ))])

    fig.update_layout(
        title_text="Safety Classification Shift: Regular vs. Misinformation Framing",
        font_size=12,
        width=800,
        height=500
    )

    # Save
    output_path = "valence_shift_sankey.png"
    fig.write_image(output_path)
    print(f"✓ Sankey diagram saved to {output_path}")

if __name__ == "__main__":
    main()
