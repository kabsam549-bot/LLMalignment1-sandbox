import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

# Ensure output directory exists
os.makedirs('LLMalignment/figures', exist_ok=True)

# Set style for JAMA (clean, sans-serif)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
sns.set_context("paper", font_scale=1.4)
sns.set_style("ticks")

# --- Figure 1: Sycophancy Gap ---
def plot_fig1():
    print("Generating Figure 1...")
    conditions = ['Regular Framing', 'Misinformation Framing']
    rates = [5.1, 14.4]
    ci_lower = [3.6, 12.0]
    ci_upper = [7.1, 17.2]
    
    # Calculate error bar lengths (matplotlib wants relative values)
    yerr_lower = [r - l for r, l in zip(rates, ci_lower)]
    yerr_upper = [u - r for r, u in zip(rates, ci_upper)]
    yerr = [yerr_lower, yerr_upper]
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Colors: Neutral Gray vs Alarm Red (but JAMA friendly)
    colors = ['#B0B0B0', '#D32F2F'] # Light gray, Dark red
    
    bars = ax.bar(conditions, rates, yerr=yerr, capsize=8, color=colors, 
                  edgecolor='black', linewidth=1, width=0.6)
    
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_ylim(0, 20)
    
    # Add values on top
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2.5,
                f'{rate}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('LLMalignment/figures/Figure1_SycophancyGap.png', bbox_inches='tight')
    plt.close()

# --- Figure 2: Safety Erosion (Sankey) ---
def plot_fig2():
    print("Generating Figure 2...")
    # Data from generate_sankey.py logic (approximated based on text description of flows)
    # We know 429 Strong(Reg). 
    # Flows:
    # Strong(Reg) -> Strong(Mis): 332
    # Strong(Reg) -> Moderate(Mis): 54
    # Strong(Reg) -> Weak(Mis): 43
    
    # We need the other flows to balance the diagram.
    # Total Reg: Strong 919 (Wait, text says "Of 429 paired conversations that started as Strong")
    # Ah, the 429 must be the subset of PAIRS where we have both conditions.
    # Text says "We evaluated 1,272 conversations". 628 Reg + 644 Misinfo.
    # Paired subset might be smaller or the 429 refers to specific matched pairs.
    # I will load the full data to get accurate Sankey flows.
    
    try:
        df = pd.read_csv('LLMalignment/batch_results/final_all_batches_data.csv')
        
        # Helper for indexing
        class_map = {'Strong': 0, 'Moderate': 1, 'Weak': 2}
        
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
                start_row = group[group['valence'] == 'negative'].iloc[0] # Regular
                end_row = group[group['valence'] == 'positive'].iloc[0]   # Misinfo
            elif treatment_type == 'traditional':
                start_row = group[group['valence'] == 'positive'].iloc[0] # Regular
                end_row = group[group['valence'] == 'negative'].iloc[0]   # Misinfo
            else:
                continue
                
            start_idx = class_map.get(start_row['Overall_Classification'])
            end_idx = class_map.get(end_row['Overall_Classification'])
            
            if start_idx is None or end_idx is None: continue
    
            key = (start_idx, end_idx)
            flows[key] = flows.get(key, 0) + 1
            
        sources = []
        targets = []
        values = []
        
        for (start, end), count in flows.items():
            sources.append(start)
            targets.append(end + 3) # Offset target nodes
            values.append(count)
            
        # Colors: Green, Orange, Red
        colors = ['#2E7D32', '#F57C00', '#C62828'] # JAMA-ish palette
        node_colors = colors + colors
        
        link_colors = []
        for src in sources:
            if src == 0: link_colors.append('rgba(46, 125, 50, 0.3)')
            elif src == 1: link_colors.append('rgba(245, 124, 0, 0.3)')
            else: link_colors.append('rgba(198, 40, 40, 0.3)')
            
        fig = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15, thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = ["Strong (Reg)", "Mod (Reg)", "Weak (Reg)", "Strong (Mis)", "Mod (Mis)", "Weak (Mis)"],
              color = node_colors
            ),
            link = dict(
              source = sources, target = targets, value = values, color = link_colors
            ))])
            
        fig.update_layout(title_text="Safety Erosion: Regular vs Misinformation Framing", font_size=14, width=800, height=500)
        
        # Save static image
        try:
            fig.write_image("LLMalignment/figures/Figure2_SafetyErosion.png", scale=2)
        except Exception as e:
            print(f"Could not save static Sankey: {e}")
            fig.write_html("LLMalignment/figures/Figure2_SafetyErosion.html")
            
    except Exception as e:
        print(f"Skipping Sankey generation due to error: {e}")

# --- Figure 3: Guardrail Effect ---
def plot_fig3():
    print("Generating Figure 3...")
    # Single-Regular (8.2%), Single-Misinfo (21.2%)
    # Multi-Regular (2.2%), Multi-Misinfo (8.1%)
    
    labels = ['Regular Framing', 'Misinformation Framing']
    single_turn = [8.2, 21.2]
    multi_turn = [2.2, 8.1]
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(7, 6))
    
    rects1 = ax.bar(x - width/2, single_turn, width, label='Single-Turn', color='#E0E0E0', edgecolor='black')
    rects2 = ax.bar(x + width/2, multi_turn, width, label='Multi-Turn (Guardrail)', color='#212121', edgecolor='black')
    
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontweight='bold')
    ax.legend(title='Conversation Format')
    ax.set_ylim(0, 25)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=11)
                        
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    plt.savefig('LLMalignment/figures/Figure3_GuardrailEffect.png', bbox_inches='tight')
    plt.close()

# --- Figure 4: Model Performance ---
def plot_fig4():
    print("Generating Figure 4...")
    # Anthropic (1.8%), Google (10.2%), OpenAI (8.6%), Meta (16.9%), DeepSeek (36.8%)
    # Ordered by unsafe rate: Anthropic < OpenAI < Google < Meta < DeepSeek
    # Wait, OpenAI 8.6 is LESS than Google 10.2.
    
    providers = ['Anthropic', 'OpenAI', 'Google', 'Meta', 'DeepSeek']
    rates = [1.8, 8.6, 10.2, 16.9, 36.8]
    
    # Reverse for horizontal bar chart (top to bottom)
    providers = providers[::-1]
    rates = rates[::-1]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    y_pos = np.arange(len(providers))
    
    # Color coding: Best (Low unsafe) -> Dark Gray, Worst -> Red?
    # Or just simple grayscale
    colors = ['#D32F2F', '#D32F2F', '#757575', '#757575', '#2E7D32'] # DeepSeek/Meta (Red), Google/OpenAI (Gray), Anthropic (Green)
    # Actually JAMA prefers cleaner. Let's use gray scale with shading.
    colors = ['#404040'] * 5
    
    bars = ax.barh(y_pos, rates, align='center', color=colors, edgecolor='black', height=0.6)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(providers, fontsize=12, fontweight='bold')
    ax.set_xlabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlim(0, 45)
    
    # Add values
    for i, v in enumerate(rates):
        ax.text(v + 1, i, f'{v}%', va='center', fontsize=11)
        
    plt.tight_layout()
    plt.savefig('LLMalignment/figures/Figure4_ModelPerformance.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_fig1()
    plot_fig2()
    plot_fig3()
    plot_fig4()
