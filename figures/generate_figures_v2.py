#!/usr/bin/env python3
"""
Professional Figure Generation for JAMA Oncology Submission
"Stress Testing Large Language Models for Medical Safety"

Design principles:
- JAMA Oncology color palette (muted, professional)
- High resolution (300 DPI)
- Sans-serif fonts (Arial)
- Minimal chartjunk (no 3D, no gradients)
- Panel lettering (A, B, C)
- Statistical annotations where appropriate
- Error bars with 95% CIs

Author: Claude (Subagent)
Date: 2026-01-24
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# JAMA ONCOLOGY STYLE CONFIGURATION
# =============================================================================

# Color palette - clinical, muted, professional
COLORS = {
    'neutral': '#4A7C94',      # Steel blue (baseline/control)
    'misconception': '#C84C4C', # Muted red (risk/concern)
    'single_turn': '#7BA3B8',   # Light steel blue
    'multi_turn': '#2D5A6B',    # Dark teal
    'strong': '#3D7A5C',        # Forest green (safe)
    'moderate': '#D4A84C',      # Amber (caution)
    'weak': '#B84C4C',          # Muted red (unsafe)
    'gray_light': '#E8E8E8',
    'gray_dark': '#404040',
    'accent': '#1A5276',
}

# Model-specific colors for consistency
MODEL_COLORS = {
    'Anthropic': '#2D5A6B',
    'Google': '#4A7C94',
    'OpenAI': '#7BA3B8',
    'Meta': '#D4A84C',
    'DeepSeek': '#B84C4C',
    'Alibaba': '#8B6B4C',
}

def setup_jama_style():
    """Configure matplotlib for JAMA Oncology publication style."""
    plt.rcParams.update({
        # Font
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica Neue', 'DejaVu Sans'],
        'font.size': 12,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 11,
        
        # Axes
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 1.0,
        'axes.labelweight': 'bold',
        
        # Grid
        'axes.grid': False,
        
        # Figure
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        
        # Lines and patches
        'patch.linewidth': 1.0,
        'lines.linewidth': 1.5,
    })
    sns.set_context("paper", font_scale=1.1)

def add_panel_label(ax, label, x=-0.15, y=1.08):
    """Add panel label (A, B, C) in bold."""
    ax.text(x, y, label, transform=ax.transAxes, 
            fontsize=14, fontweight='bold', va='top', ha='left')

def add_significance_bracket(ax, x1, x2, y, height, text, fontsize=9):
    """Add significance bracket between two bars."""
    ax.plot([x1, x1, x2, x2], [y, y+height, y+height, y], 
            lw=1.2, c='black')
    ax.text((x1+x2)/2, y+height+0.003, text, ha='center', va='bottom', 
            fontsize=fontsize, fontweight='bold')

def wilson_ci(p, n, z=1.96):
    """Wilson score confidence interval for proportion."""
    denominator = 1 + z**2/n
    centre = (p + z**2/(2*n))/denominator
    spread = z * np.sqrt((p*(1-p) + z**2/(4*n))/n)/denominator
    return max(0, centre - spread), min(1, centre + spread)

# =============================================================================
# FIGURE 1: THE SYCOPHANCY EFFECT (PRIMARY FINDING)
# =============================================================================

def figure1_sycophancy_effect(df, output_dir):
    """
    Figure 1: The Sycophancy Effect
    
    Panel A: Bar chart showing unsafe response rates by framing condition
    Panel B: Classification distribution shift (stacked bars)
    """
    print("Generating Figure 1: The Sycophancy Effect...")
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # ----- PANEL A: Unsafe Response Rates -----
    ax = axes[0]
    
    # Calculate framing conditions
    # Misconception = (alternative + positive) OR (traditional + negative)
    df['is_misconception'] = (
        ((df['treatment_type'] == 'alternative') & (df['valence'] == 'positive')) |
        ((df['treatment_type'] == 'traditional') & (df['valence'] == 'negative'))
    )
    
    neutral = df[~df['is_misconception']]
    misconception = df[df['is_misconception']]
    
    # Calculate rates with CIs
    n_neutral = len(neutral)
    n_miscon = len(misconception)
    rate_neutral = (neutral['Overall_Classification'] == 'Weak').mean()
    rate_miscon = (misconception['Overall_Classification'] == 'Weak').mean()
    
    ci_neutral = wilson_ci(rate_neutral, n_neutral)
    ci_miscon = wilson_ci(rate_miscon, n_miscon)
    
    rates = [rate_neutral * 100, rate_miscon * 100]
    yerr_lower = [rates[0] - ci_neutral[0]*100, rates[1] - ci_miscon[0]*100]
    yerr_upper = [ci_neutral[1]*100 - rates[0], ci_miscon[1]*100 - rates[1]]
    
    conditions = ['Neutral\nFraming', 'Misconception\nFraming']
    colors = [COLORS['neutral'], COLORS['misconception']]
    
    bars = ax.bar(conditions, rates, 
                  yerr=[yerr_lower, yerr_upper], 
                  capsize=6, 
                  color=colors,
                  edgecolor='black', 
                  linewidth=1.2, 
                  width=0.55,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})
    
    # Add value labels
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + yerr_upper[bars.index(bar)] + 0.8,
                f'{rate:.1f}%', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    # Add odds ratio annotation
    ax.annotate('OR = 3.13\n(95% CI: 2.05–4.79)\nP < .001', 
                xy=(0.5, max(rates) + 5), 
                ha='center', va='bottom',
                fontsize=9, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.9))
    
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_ylim(0, 22)
    ax.set_xlim(-0.6, 1.6)
    add_panel_label(ax, 'A')
    
    # ----- PANEL B: Classification Distribution -----
    ax = axes[1]
    
    # Get classification counts
    classifications = ['Strong', 'Moderate', 'Weak']
    neutral_counts = [
        (neutral['Overall_Classification'] == c).sum() / len(neutral) * 100 
        for c in classifications
    ]
    miscon_counts = [
        (misconception['Overall_Classification'] == c).sum() / len(misconception) * 100 
        for c in classifications
    ]
    
    x = np.arange(2)
    width = 0.6
    
    # Stacked bars
    bottom_neutral = 0
    bottom_miscon = 0
    
    class_colors = [COLORS['strong'], COLORS['moderate'], COLORS['weak']]
    
    for i, (classification, color) in enumerate(zip(classifications, class_colors)):
        ax.bar(0, neutral_counts[i], width, bottom=bottom_neutral, 
               color=color, edgecolor='white', linewidth=0.5, label=classification)
        ax.bar(1, miscon_counts[i], width, bottom=bottom_miscon, 
               color=color, edgecolor='white', linewidth=0.5)
        
        # Add percentage labels in center of each segment
        if neutral_counts[i] > 5:
            ax.text(0, bottom_neutral + neutral_counts[i]/2, 
                    f'{neutral_counts[i]:.0f}%', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')
        if miscon_counts[i] > 5:
            ax.text(1, bottom_miscon + miscon_counts[i]/2, 
                    f'{miscon_counts[i]:.0f}%', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')
        
        bottom_neutral += neutral_counts[i]
        bottom_miscon += miscon_counts[i]
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Neutral\nFraming', 'Misconception\nFraming'])
    ax.set_ylabel('Classification Distribution (%)', fontweight='bold')
    ax.set_ylim(0, 105)
    ax.legend(title='Safety\nClassification', loc='upper right', frameon=True, 
              edgecolor='gray', fancybox=False)
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure1_SycophancyEffect.png'), 
                facecolor='white', edgecolor='none')
    plt.savefig(os.path.join(output_dir, 'Figure1_SycophancyEffect.pdf'), 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Figure 1 saved")

# =============================================================================
# FIGURE 2: PROTECTIVE EFFECT OF MULTI-TURN CONVERSATIONS
# =============================================================================

def figure2_multiturn_protection(df, output_dir):
    """
    Figure 2: Multi-Turn Protective Effect
    
    Panel A: Interaction plot (Format × Framing)
    Panel B: Reduction in unsafe rates (waterfall/forest plot style)
    """
    print("Generating Figure 2: Multi-Turn Protective Effect...")
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # Calculate framing condition
    df['is_misconception'] = (
        ((df['treatment_type'] == 'alternative') & (df['valence'] == 'positive')) |
        ((df['treatment_type'] == 'traditional') & (df['valence'] == 'negative'))
    )
    df['framing'] = df['is_misconception'].map({False: 'Neutral', True: 'Misconception'})
    
    # ----- PANEL A: Interaction Plot -----
    ax = axes[0]
    
    # Calculate rates for each condition
    conditions = []
    for fmt in ['single_turn', 'multi_turn']:
        for framing in [False, True]:
            subset = df[(df['format'] == fmt) & (df['is_misconception'] == framing)]
            n = len(subset)
            rate = (subset['Overall_Classification'] == 'Weak').mean() * 100
            ci = wilson_ci(rate/100, n)
            conditions.append({
                'format': 'Single-Turn' if fmt == 'single_turn' else 'Multi-Turn',
                'framing': 'Misconception' if framing else 'Neutral',
                'rate': rate,
                'ci_lower': ci[0] * 100,
                'ci_upper': ci[1] * 100,
                'n': n
            })
    
    cond_df = pd.DataFrame(conditions)
    
    # Plot interaction
    x_positions = {'Neutral': 0, 'Misconception': 1}
    format_styles = {
        'Single-Turn': {'color': COLORS['single_turn'], 'marker': 's', 'linestyle': '-'},
        'Multi-Turn': {'color': COLORS['multi_turn'], 'marker': 'o', 'linestyle': '--'}
    }
    
    for fmt in ['Single-Turn', 'Multi-Turn']:
        fmt_data = cond_df[cond_df['format'] == fmt]
        x = [x_positions[f] for f in fmt_data['framing']]
        y = fmt_data['rate'].values
        yerr_lower = y - fmt_data['ci_lower'].values
        yerr_upper = fmt_data['ci_upper'].values - y
        
        style = format_styles[fmt]
        ax.errorbar(x, y, yerr=[yerr_lower, yerr_upper], 
                    label=fmt, color=style['color'], 
                    marker=style['marker'], markersize=10,
                    linestyle=style['linestyle'], linewidth=2.5,
                    capsize=5, capthick=2)
        
        # Add rate labels
        for xi, yi in zip(x, y):
            offset = 1.5 if fmt == 'Single-Turn' else -2.5
            va = 'bottom' if fmt == 'Single-Turn' else 'top'
            ax.text(xi, yi + offset, f'{yi:.1f}%', ha='center', va=va, 
                    fontsize=10, fontweight='bold', color=style['color'])
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Neutral\nFraming', 'Misconception\nFraming'])
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_ylim(0, 26)
    ax.set_xlim(-0.3, 1.3)
    ax.legend(title='Conversation\nFormat', loc='upper left', frameon=True, edgecolor='gray')
    add_panel_label(ax, 'A')
    
    # ----- PANEL B: Relative Risk Reduction -----
    ax = axes[1]
    
    # Calculate relative risk reduction
    single_neutral = cond_df[(cond_df['format'] == 'Single-Turn') & (cond_df['framing'] == 'Neutral')]['rate'].values[0]
    single_miscon = cond_df[(cond_df['format'] == 'Single-Turn') & (cond_df['framing'] == 'Misconception')]['rate'].values[0]
    multi_neutral = cond_df[(cond_df['format'] == 'Multi-Turn') & (cond_df['framing'] == 'Neutral')]['rate'].values[0]
    multi_miscon = cond_df[(cond_df['format'] == 'Multi-Turn') & (cond_df['framing'] == 'Misconception')]['rate'].values[0]
    
    # Bars showing absolute rates
    categories = ['Single-Turn\nNeutral', 'Multi-Turn\nNeutral', 
                  'Single-Turn\nMisconception', 'Multi-Turn\nMisconception']
    values = [single_neutral, multi_neutral, single_miscon, multi_miscon]
    colors = [COLORS['single_turn'], COLORS['multi_turn'], 
              COLORS['single_turn'], COLORS['multi_turn']]
    
    bars = ax.barh(range(4), values, color=colors, edgecolor='black', linewidth=1, height=0.6)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 0.5, i, f'{val:.1f}%', ha='left', va='center', 
                fontsize=10, fontweight='bold')
    
    # Add reduction arrows and percentages
    # Neutral: 8.2% → 2.2% = 73% reduction
    # Misconception: 21.2% → 8.1% = 62% reduction
    ax.annotate('', xy=(multi_neutral, 0.5), xytext=(single_neutral, 0.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text((single_neutral + multi_neutral)/2, 0.9, '−73%', ha='center', va='bottom',
            fontsize=9, fontweight='bold', color=COLORS['multi_turn'])
    
    ax.annotate('', xy=(multi_miscon, 2.5), xytext=(single_miscon, 2.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text((single_miscon + multi_miscon)/2, 2.9, '−62%', ha='center', va='bottom',
            fontsize=9, fontweight='bold', color=COLORS['multi_turn'])
    
    ax.set_yticks(range(4))
    ax.set_yticklabels(categories)
    ax.set_xlabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlim(0, 27)
    ax.invert_yaxis()
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['single_turn'], edgecolor='black', label='Single-Turn'),
        mpatches.Patch(facecolor=COLORS['multi_turn'], edgecolor='black', label='Multi-Turn'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, edgecolor='gray')
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure2_MultiTurnProtection.png'),
                facecolor='white', edgecolor='none')
    plt.savefig(os.path.join(output_dir, 'Figure2_MultiTurnProtection.pdf'),
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Figure 2 saved")

# =============================================================================
# FIGURE 3: MODEL PERFORMANCE COMPARISON
# =============================================================================

def figure3_model_performance(df, output_dir):
    """
    Figure 3: Model Performance Comparison
    
    Panel A: Forest plot of unsafe rates by model (sorted)
    Panel B: Provider-level performance with sample sizes
    """
    print("Generating Figure 3: Model Performance Comparison...")
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
    
    # ----- PANEL A: Individual Model Performance (Forest Plot Style) -----
    ax = axes[0]
    
    # Calculate rates per model
    model_stats = []
    for model in df['model_name_clean'].unique():
        subset = df[df['model_name_clean'] == model]
        n = len(subset)
        rate = (subset['Overall_Classification'] == 'Weak').mean()
        ci = wilson_ci(rate, n)
        provider = subset['model_provider'].iloc[0]
        
        # Clean model names for display
        display_name = model.replace('.json', '').replace('_', ' ')
        display_name = display_name.replace('claude-3-7-sonnet-20250219', 'Claude 3.7 Sonnet')
        display_name = display_name.replace('claude-3-5-haiku-20241022', 'Claude 3.5 Haiku')
        display_name = display_name.replace('gemini-2.0-flash-thinking-exp-01-21', 'Gemini 2.0 Thinking')
        display_name = display_name.replace('google gemma-3-27b-it', 'Gemma 3 27B')
        display_name = display_name.replace('deepseek-ai DeepSeek-R1-Distill-Qwen-32B', 'DeepSeek R1 Distill')
        display_name = display_name.replace('Qwen Qwen3-32B', 'Qwen 3 32B')
        display_name = display_name.replace('gemini-', 'Gemini ')
        display_name = display_name.replace('gemma3-', 'Gemma 3 ')
        display_name = display_name.replace('llama3.2 3b', 'Llama 3.2 3B')
        display_name = display_name.replace('4o-mini', 'GPT-4o Mini')
        display_name = display_name.replace('4o', 'GPT-4o')
        display_name = display_name.replace('o3-mini', 'O3 Mini')
        
        model_stats.append({
            'model': display_name,
            'provider': provider,
            'rate': rate * 100,
            'ci_lower': ci[0] * 100,
            'ci_upper': ci[1] * 100,
            'n': n
        })
    
    model_df = pd.DataFrame(model_stats).sort_values('rate')
    
    # Plot forest plot style
    y_positions = range(len(model_df))
    
    for i, (_, row) in enumerate(model_df.iterrows()):
        color = MODEL_COLORS.get(row['provider'], COLORS['gray_dark'])
        
        # Point estimate
        ax.scatter(row['rate'], i, color=color, s=80, zorder=3, edgecolor='black', linewidth=0.5)
        
        # CI line
        ax.hlines(i, row['ci_lower'], row['ci_upper'], color=color, linewidth=2, zorder=2)
        
        # Rate label
        ax.text(row['ci_upper'] + 1, i, f"{row['rate']:.1f}%", 
                va='center', ha='left', fontsize=8, color=color, fontweight='bold')
    
    ax.set_yticks(y_positions)
    ax.set_yticklabels(model_df['model'], fontsize=9)
    ax.set_xlabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlim(-2, 50)
    ax.axvline(x=9.8, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Overall mean')
    
    # Provider legend
    legend_elements = [mpatches.Patch(facecolor=c, edgecolor='black', label=p) 
                      for p, c in MODEL_COLORS.items() if p in model_df['provider'].values]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, 
              edgecolor='gray', fontsize=8, title='Provider')
    add_panel_label(ax, 'A')
    
    # ----- PANEL B: Provider-Level Performance -----
    ax = axes[1]
    
    # Calculate provider-level stats
    provider_stats = []
    for provider in df['model_provider'].unique():
        subset = df[df['model_provider'] == provider]
        n = len(subset)
        rate = (subset['Overall_Classification'] == 'Weak').mean()
        ci = wilson_ci(rate, n)
        
        provider_stats.append({
            'provider': provider,
            'rate': rate * 100,
            'ci_lower': ci[0] * 100,
            'ci_upper': ci[1] * 100,
            'n': n
        })
    
    provider_df = pd.DataFrame(provider_stats).sort_values('rate')
    
    # Horizontal bar chart
    colors = [MODEL_COLORS.get(p, COLORS['gray_dark']) for p in provider_df['provider']]
    y_pos = range(len(provider_df))
    
    bars = ax.barh(y_pos, provider_df['rate'], 
                   xerr=[provider_df['rate'] - provider_df['ci_lower'], 
                         provider_df['ci_upper'] - provider_df['rate']],
                   color=colors, edgecolor='black', linewidth=1, height=0.6,
                   capsize=4, error_kw={'linewidth': 1.5})
    
    # Add value labels with sample sizes
    for i, (_, row) in enumerate(provider_df.iterrows()):
        ax.text(row['ci_upper'] + 1, i, f"{row['rate']:.1f}% (n={row['n']})", 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(provider_df['provider'], fontsize=10, fontweight='bold')
    ax.set_xlabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlim(0, 45)
    ax.axvline(x=9.8, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(10.5, len(provider_df)-0.5, 'Overall\nmean', fontsize=8, color='gray', va='top')
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure3_ModelPerformance.png'),
                facecolor='white', edgecolor='none')
    plt.savefig(os.path.join(output_dir, 'Figure3_ModelPerformance.pdf'),
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Figure 3 saved")

# =============================================================================
# FIGURE 4: SAFETY EROSION ANALYSIS
# =============================================================================

def figure4_safety_erosion(df, output_dir):
    """
    Figure 4: Safety Erosion in Paired Conversations
    
    Panel A: Alluvial/Sankey-style flow diagram (simplified as grouped bars)
    Panel B: Dimension-level analysis (radar/bar chart)
    """
    print("Generating Figure 4: Safety Erosion Analysis...")
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    
    # Calculate framing condition
    df['is_misconception'] = (
        ((df['treatment_type'] == 'alternative') & (df['valence'] == 'positive')) |
        ((df['treatment_type'] == 'traditional') & (df['valence'] == 'negative'))
    )
    
    # ----- PANEL A: Classification Transitions -----
    ax = axes[0]
    
    # Find paired conversations
    class_map = {'Strong': 0, 'Moderate': 1, 'Weak': 2}
    
    # Group by model, treatment, format to isolate valence pairs
    transition_matrix = np.zeros((3, 3))
    
    grouped = df.groupby(['model_name_clean', 'treatment_id', 'format'])
    
    for name, group in grouped:
        if len(group) != 2:
            continue
        
        if not (('positive' in group['valence'].values) and ('negative' in group['valence'].values)):
            continue
        
        treatment_type = group['treatment_type'].iloc[0]
        
        # Determine Neutral (Source) -> Misconception (Target)
        if treatment_type == 'alternative':
            neutral_row = group[group['valence'] == 'negative'].iloc[0]
            miscon_row = group[group['valence'] == 'positive'].iloc[0]
        elif treatment_type == 'traditional':
            neutral_row = group[group['valence'] == 'positive'].iloc[0]
            miscon_row = group[group['valence'] == 'negative'].iloc[0]
        else:
            continue
        
        start_idx = class_map.get(neutral_row['Overall_Classification'])
        end_idx = class_map.get(miscon_row['Overall_Classification'])
        
        if start_idx is not None and end_idx is not None:
            transition_matrix[start_idx, end_idx] += 1
    
    # Normalize by starting classification
    row_totals = transition_matrix.sum(axis=1, keepdims=True)
    row_totals[row_totals == 0] = 1  # Avoid division by zero
    transition_pct = (transition_matrix / row_totals) * 100
    
    # Plot grouped bars for each starting classification
    x = np.arange(3)
    width = 0.25
    
    classifications = ['Strong', 'Moderate', 'Weak']
    class_colors = [COLORS['strong'], COLORS['moderate'], COLORS['weak']]
    
    for i, (start_class, color) in enumerate(zip(classifications, class_colors)):
        if transition_matrix[i].sum() > 0:
            bars = ax.bar(x + (i - 1) * width, transition_pct[i], width, 
                         label=f'Started {start_class}', color=color,
                         edgecolor='black', linewidth=0.5, alpha=0.8)
            
            # Add counts
            for j, bar in enumerate(bars):
                if transition_pct[i, j] > 3:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{int(transition_matrix[i, j])}', ha='center', va='bottom',
                            fontsize=8, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(['Remained\nStrong', 'Became\nModerate', 'Became\nWeak'])
    ax.set_ylabel('Percentage of Conversations (%)', fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(title='Starting\nClassification', loc='upper right', frameon=True, edgecolor='gray')
    ax.set_title('Classification Transitions (Neutral → Misconception)', fontsize=11, fontweight='bold', pad=10)
    add_panel_label(ax, 'A')
    
    # ----- PANEL B: Dimension-Level Score Comparison -----
    ax = axes[1]
    
    dimensions = ['Evidence_R_Adj', 'Testimonial_R_Adj', 'Safety_Rejection_Adj', 
                  'Misatribution_R_Adj', 'Promotion_Adj', 'HCP_Ref_Adj']
    dim_labels = ['Evidence\nAccuracy', 'Testimonial\nHandling', 'Safety\nGuidance', 
                  'Misattribution\nCorrection', 'Promotional\nContent', 'HCP\nReferral']
    dim_max = [3, 1, 2, 1, 3, 2]
    
    neutral_means = []
    miscon_means = []
    
    neutral_df = df[~df['is_misconception']]
    miscon_df = df[df['is_misconception']]
    
    for dim, max_score in zip(dimensions, dim_max):
        neutral_means.append(neutral_df[dim].mean() / max_score * 100)
        miscon_means.append(miscon_df[dim].mean() / max_score * 100)
    
    x = np.arange(len(dimensions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, neutral_means, width, label='Neutral Framing',
                   color=COLORS['neutral'], edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, miscon_means, width, label='Misconception Framing',
                   color=COLORS['misconception'], edgecolor='black', linewidth=1)
    
    # Add percentage labels
    for bar, val in zip(bars1, neutral_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=8)
    for bar, val in zip(bars2, miscon_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, fontsize=9)
    ax.set_ylabel('Score (% of Maximum)', fontweight='bold')
    ax.set_ylim(0, 115)
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.legend(loc='upper right', frameon=True, edgecolor='gray')
    ax.set_title('Performance by Rubric Dimension', fontsize=11, fontweight='bold', pad=10)
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure4_SafetyErosion.png'),
                facecolor='white', edgecolor='none')
    plt.savefig(os.path.join(output_dir, 'Figure4_SafetyErosion.pdf'),
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Figure 4 saved")

# =============================================================================
# SUPPLEMENTARY: TREATMENT × VALENCE INTERACTION
# =============================================================================

def figure_s1_treatment_valence(df, output_dir):
    """
    Supplementary Figure 1: Treatment × Valence Interaction
    Shows the conceptual crossover where positive valence hurts alternative
    and negative valence hurts traditional.
    """
    print("Generating Supplementary Figure 1: Treatment × Valence Interaction...")
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Calculate rates for each condition
    conditions = []
    for treatment in ['traditional', 'alternative']:
        for valence in ['positive', 'negative']:
            subset = df[(df['treatment_type'] == treatment) & (df['valence'] == valence)]
            n = len(subset)
            rate = (subset['Overall_Classification'] == 'Weak').mean() * 100
            ci = wilson_ci(rate/100, n)
            conditions.append({
                'treatment': 'Evidence-Based' if treatment == 'traditional' else 'Unproven/Alternative',
                'valence': 'Positive\n(Promoting)' if valence == 'positive' else 'Negative\n(Questioning)',
                'rate': rate,
                'ci_lower': ci[0] * 100,
                'ci_upper': ci[1] * 100
            })
    
    cond_df = pd.DataFrame(conditions)
    
    # Plot interaction
    x_positions = {'Positive\n(Promoting)': 0, 'Negative\n(Questioning)': 1}
    treatment_styles = {
        'Evidence-Based': {'color': COLORS['multi_turn'], 'marker': 'o', 'linestyle': '-'},
        'Unproven/Alternative': {'color': COLORS['misconception'], 'marker': 's', 'linestyle': '--'}
    }
    
    for treatment in ['Evidence-Based', 'Unproven/Alternative']:
        t_data = cond_df[cond_df['treatment'] == treatment]
        x = [x_positions[v] for v in t_data['valence']]
        y = t_data['rate'].values
        yerr_lower = y - t_data['ci_lower'].values
        yerr_upper = t_data['ci_upper'].values - y
        
        style = treatment_styles[treatment]
        ax.errorbar(x, y, yerr=[yerr_lower, yerr_upper],
                    label=treatment, color=style['color'],
                    marker=style['marker'], markersize=12,
                    linestyle=style['linestyle'], linewidth=2.5,
                    capsize=5, capthick=2)
        
        for xi, yi in zip(x, y):
            offset = 1.8 if treatment == 'Unproven/Alternative' else -1.8
            va = 'bottom' if treatment == 'Unproven/Alternative' else 'top'
            ax.text(xi, yi + offset, f'{yi:.1f}%', ha='center', va=va,
                    fontsize=10, fontweight='bold', color=style['color'])
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Positive\n(Promoting)', 'Negative\n(Questioning)'])
    ax.set_xlabel('User Valence', fontweight='bold')
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_ylim(0, 22)
    ax.set_xlim(-0.3, 1.3)
    ax.legend(title='Treatment Type', loc='upper center', frameon=True, edgecolor='gray')
    
    # Add annotation explaining the crossover
    ax.annotate('Promoting unproven\ntreatments triggers\nsycophancy', 
                xy=(0, 15), xytext=(0.15, 19),
                fontsize=8, ha='left',
                arrowprops=dict(arrowstyle='->', color='gray', lw=1))
    ax.annotate('Attacking evidence-based\ntreatments also\ntriggers sycophancy',
                xy=(1, 9), xytext=(0.55, 5),
                fontsize=8, ha='left',
                arrowprops=dict(arrowstyle='->', color='gray', lw=1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'FigureS1_TreatmentValence.png'),
                facecolor='white', edgecolor='none')
    plt.savefig(os.path.join(output_dir, 'FigureS1_TreatmentValence.pdf'),
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Supplementary Figure 1 saved")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Generate all figures for the manuscript."""
    
    # Setup
    setup_jama_style()
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'batch_results', 'final_all_batches_data.csv')
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n{'='*60}")
    print("JAMA Oncology Figure Generation")
    print(f"{'='*60}")
    print(f"Data: {data_path}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")
    
    # Load data
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} conversations from {df['model_name_clean'].nunique()} models\n")
    except Exception as e:
        print(f"ERROR: Could not load data: {e}")
        return
    
    # Generate figures
    figure1_sycophancy_effect(df, output_dir)
    figure2_multiturn_protection(df, output_dir)
    figure3_model_performance(df, output_dir)
    figure4_safety_erosion(df, output_dir)
    figure_s1_treatment_valence(df, output_dir)
    
    print(f"\n{'='*60}")
    print("All figures generated successfully!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
