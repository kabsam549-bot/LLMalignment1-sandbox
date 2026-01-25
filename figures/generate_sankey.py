#!/usr/bin/env python3
"""
Generate Sankey Diagram for Figure 4A: Classification Transitions Under Misconception Framing
Shows flow from Evidence-aligned classification → Misconception framing classification
"""

import json
import plotly.graph_objects as go
from pathlib import Path

def generate_sankey_diagram():
    """Generate Sankey diagram showing classification transitions"""
    
    # Load data
    data_path = Path(__file__).parent / 'sankey_data.json'
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Define node labels and colors
    # Source nodes (left): Evidence-aligned classification
    # Target nodes (right): Misconception framing classification
    node_labels = [
        'Strong\n(Evidence-aligned)',
        'Moderate\n(Evidence-aligned)', 
        'Weak\n(Evidence-aligned)',
        'Strong\n(Misconception)',
        'Moderate\n(Misconception)',
        'Weak\n(Misconception)'
    ]
    
    # Color scheme: Green (Strong) → Orange (Moderate) → Red (Weak)
    node_colors = [
        '#2E7D32',  # Strong (left) - Green
        '#F57C00',  # Moderate (left) - Orange
        '#C62828',  # Weak (left) - Red
        '#2E7D32',  # Strong (right) - Green
        '#F57C00',  # Moderate (right) - Orange
        '#C62828'   # Weak (right) - Red
    ]
    
    # Map classification names to node indices
    class_to_idx = {
        'Strong': 0,
        'Moderate': 1,
        'Weak': 2
    }
    
    # Build link data
    sources = []
    targets = []
    values = []
    link_colors = []
    
    for flow in data['flows']:
        source_class = flow['source']
        target_class = flow['target']
        value = flow['value']
        
        # Source node index (0-2 for left side)
        source_idx = class_to_idx[source_class]
        # Target node index (3-5 for right side)
        target_idx = class_to_idx[target_class] + 3
        
        sources.append(source_idx)
        targets.append(target_idx)
        values.append(value)
        
        # Color links based on SOURCE classification (with transparency)
        if source_idx == 0:  # Strong
            link_colors.append('rgba(46, 125, 50, 0.4)')   # Green with transparency
        elif source_idx == 1:  # Moderate
            link_colors.append('rgba(245, 124, 0, 0.4)')   # Orange with transparency
        else:  # Weak
            link_colors.append('rgba(198, 40, 40, 0.4)')   # Red with transparency
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='black', width=1),
            label=node_labels,
            color=node_colors,
            customdata=[[data['totals']['Strong']], 
                       [data['totals']['Moderate']], 
                       [data['totals']['Weak']],
                       [0], [0], [0]],  # Right side totals calculated from flows
            hovertemplate='%{label}<br>n=%{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            customdata=[[f"{v/data['totals'][['Strong','Moderate','Weak'][s]]:.1%}"] 
                       for s, v in zip(sources, values)],
            hovertemplate='%{source.label} → %{target.label}<br>' +
                         'n=%{value} (%{customdata[0]})<extra></extra>'
        )
    )])
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Classification Transitions Under Misconception Framing',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        font=dict(size=11, family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=900,
        height=600,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Add annotation explaining the diagram
    fig.add_annotation(
        text='Flow shows how classifications changed when same scenarios shifted from evidence-aligned to misconception framing.<br>' +
             f'Among {data["totals"]["Strong"]} Strong conversations under evidence-aligned framing, ' +
             f'{data["transitions"]["Strong->Strong"]} (77.4%) remained Strong, ' +
             f'{data["transitions"]["Strong->Moderate"]} (12.6%) declined to Moderate, ' +
             f'and {data["transitions"]["Strong->Weak"]} (10.0%) fell to Weak under misconception framing.',
        xref='paper', yref='paper',
        x=0.5, y=-0.12,
        xanchor='center',
        showarrow=False,
        font=dict(size=10, color='#666'),
        align='center'
    )
    
    # Save outputs
    output_dir = Path('.')
    
    # Save as HTML (interactive)
    html_path = output_dir / 'Figure4A_Sankey.html'
    fig.write_html(str(html_path))
    print(f"✓ Interactive HTML saved to {html_path}")
    
    # Save as PNG (for publication)
    png_path = output_dir / 'Figure4A_Sankey.png'
    fig.write_image(str(png_path), width=900, height=600, scale=2)
    print(f"✓ PNG image saved to {png_path}")
    
    # Save as PDF (for publication)
    pdf_path = output_dir / 'Figure4A_Sankey.pdf'
    fig.write_image(str(pdf_path), width=900, height=600)
    print(f"✓ PDF saved to {pdf_path}")
    
    print("\n=== Summary Statistics ===")
    print(f"Total paired conversations: {sum(data['totals'].values())}")
    print(f"  Starting as Strong: {data['totals']['Strong']}")
    print(f"  Starting as Moderate: {data['totals']['Moderate']}")
    print(f"  Starting as Weak: {data['totals']['Weak']}")
    print(f"\nDegradation from Strong: {data['transitions']['Strong->Moderate'] + data['transitions']['Strong->Weak']} " +
          f"({(data['transitions']['Strong->Moderate'] + data['transitions']['Strong->Weak'])/data['totals']['Strong']*100:.1f}%)")
    print(f"Improvement from Weak: {data['transitions']['Weak->Strong'] + data['transitions']['Weak->Moderate']} " +
          f"({(data['transitions']['Weak->Strong'] + data['transitions']['Weak->Moderate'])/data['totals']['Weak']*100:.1f}%)")

if __name__ == "__main__":
    generate_sankey_diagram()
