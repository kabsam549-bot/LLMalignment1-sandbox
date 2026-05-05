#!/usr/bin/env python3
"""
Regenerate figures with consistent styling and updated terminology.
- Evidence-aligned instead of Neutral
- Consistent color palette across all figures
- Professional legends
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# UNIFIED COLOR PALETTE (consistent across ALL figures)
# =============================================================================
COLORS = {
    # Primary comparison (framing conditions)
    'evidence_aligned': '#3D7A5C',  # Forest green (good/safe/aligned)
    'misconception': '#B84C4C',      # Muted red (risk/concern)
    
    # Format comparison
    'single_turn': '#7BA3B8',        # Light steel blue
    'multi_turn': '#2D5A6B',         # Dark teal
    
    # Safety classifications
    'strong': '#3D7A5C',             # Forest green (safe)
    'moderate': '#D4A84C',           # Amber (caution)
    'weak': '#B84C4C',               # Muted red (unsafe)
    
    # Provider colors
    'Anthropic': '#2D5A6B',
    'Google': '#4A7C94', 
    'OpenAI': '#7BA3B8',
    'Meta': '#D4A84C',
    'DeepSeek': '#B84C4C',
    'Alibaba': '#8B6B4C',
}

def setup_style():
    """Configure matplotlib for publication."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica Neue', 'DejaVu Sans'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 1.0,
        'axes.grid': False,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })

def add_panel_label(ax, label, x=-0.12, y=1.05):
    ax.text(x, y, label, transform=ax.transAxes, 
            fontsize=14, fontweight='bold', va='top', ha='left')

def wilson_ci(p, n, z=1.96):
    """Wilson score confidence interval."""
    if n == 0:
        return 0, 0
    denominator = 1 + z**2/n
    centre = (p + z**2/(2*n))/denominator
    spread = z * np.sqrt((p*(1-p) + z**2/(4*n))/n)/denominator
    return max(0, centre - spread), min(1, centre + spread)

# =============================================================================
# FIGURE 1: THE SYCOPHANCY EFFECT
# =============================================================================
def figure1(output_dir):
    """Figure 1: Bar chart + stacked distribution."""
    print("Generating Figure 1...")
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # Data (from manuscript)
    rate_aligned = 5.0
    rate_miscon = 14.6
    n_aligned, n_miscon = 636, 636
    
    ci_aligned = wilson_ci(rate_aligned/100, n_aligned)
    ci_miscon = wilson_ci(rate_miscon/100, n_miscon)
    
    # Panel A: Bar chart
    ax = axes[0]
    conditions = ['Evidence-\naligned', 'Misconception']
    rates = [rate_aligned, rate_miscon]
    colors = [COLORS['evidence_aligned'], COLORS['misconception']]
    
    yerr_lower = [rates[0] - ci_aligned[0]*100, rates[1] - ci_miscon[0]*100]
    yerr_upper = [ci_aligned[1]*100 - rates[0], ci_miscon[1]*100 - rates[1]]
    
    bars = ax.bar(conditions, rates, 
                  yerr=[yerr_lower, yerr_upper], 
                  capsize=6, color=colors,
                  edgecolor='black', linewidth=1.2, width=0.55,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})
    
    for i, (bar, rate) in enumerate(zip(bars, rates)):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + yerr_upper[i] + 0.8,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.annotate('OR = 3.13\n(95% CI: 2.05–4.79)\nP < .001', 
                xy=(0.5, 18), ha='center', va='bottom', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray'))
    
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_ylim(0, 22)
    ax.set_xlabel('Framing Condition', fontweight='bold')
    add_panel_label(ax, 'A')
    
    # Panel B: Stacked bars
    ax = axes[1]
    
    # Data (from manuscript)
    aligned_dist = [75.0, 20.0, 5.0]  # Strong, Moderate, Weak
    miscon_dist = [69.5, 15.9, 14.6]
    
    class_colors = [COLORS['strong'], COLORS['moderate'], COLORS['weak']]
    class_labels = ['Strong', 'Moderate', 'Weak']
    
    x_pos = [0, 1]
    width = 0.6
    
    for i, (pcts, x) in enumerate([(aligned_dist, 0), (miscon_dist, 1)]):
        bottom = 0
        for j, (pct, color) in enumerate(zip(pcts, class_colors)):
            ax.bar(x, pct, width, bottom=bottom, color=color, edgecolor='white', linewidth=0.5)
            if pct > 8:
                ax.text(x, bottom + pct/2, f'{pct:.0f}%', ha='center', va='center',
                        fontsize=9, fontweight='bold', color='white')
            bottom += pct
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Evidence-\naligned', 'Misconception'])
    ax.set_ylabel('Classification Distribution (%)', fontweight='bold')
    ax.set_xlabel('Framing Condition', fontweight='bold')
    ax.set_ylim(0, 105)
    
    # Legend
    handles = [mpatches.Patch(color=c, label=l) for c, l in zip(class_colors, class_labels)]
    ax.legend(handles=handles, title='Classification', loc='upper right', 
              frameon=True, edgecolor='gray', fancybox=False)
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure1_SycophancyEffect.png'), facecolor='white')
    plt.savefig(os.path.join(output_dir, 'Figure1_SycophancyEffect.pdf'), facecolor='white')
    plt.close()
    print("  ✓ Figure 1 saved")

# =============================================================================
# FIGURE 2: MULTI-TURN PROTECTION
# =============================================================================
def figure2(output_dir):
    """Figure 2: Interaction plot + risk reduction."""
    print("Generating Figure 2...")
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # Data (from manuscript)
    # Single-turn: 8.2% (aligned), 21.2% (misconception)
    # Multi-turn: 2.2% (aligned), 8.1% (misconception)
    
    # Panel A: Interaction plot
    ax = axes[0]
    x = [0, 1]
    single = [8.2, 21.2]
    multi = [2.2, 8.1]
    
    ax.plot(x, single, 'o-', color=COLORS['single_turn'], linewidth=2.5, 
            markersize=10, label='Single-turn')
    ax.plot(x, multi, 's--', color=COLORS['multi_turn'], linewidth=2.5, 
            markersize=10, label='Multi-turn')
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Evidence-\naligned', 'Misconception'])
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlabel('Framing Condition', fontweight='bold')
    ax.set_ylim(0, 25)
    ax.legend(title='Format', loc='upper left', frameon=True, edgecolor='gray')
    add_panel_label(ax, 'A')
    
    # Panel B: Risk reduction bars
    ax = axes[1]
    
    conditions = ['Evidence-\naligned', 'Misconception']
    rrr = [73, 62]  # Relative risk reduction
    
    bars = ax.bar(conditions, rrr, color=[COLORS['evidence_aligned'], COLORS['misconception']],
                  edgecolor='black', linewidth=1.2, width=0.55)
    
    for bar, val in zip(bars, rrr):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                f'{val}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Relative Risk Reduction (%)', fontweight='bold')
    ax.set_xlabel('Framing Condition', fontweight='bold')
    ax.set_ylim(0, 85)
    ax.axhline(y=68, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(1.1, 68, 'Overall: 68%', va='center', fontsize=9, color='gray')
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure2_MultiTurnProtection.png'), facecolor='white')
    plt.savefig(os.path.join(output_dir, 'Figure2_MultiTurnProtection.pdf'), facecolor='white')
    plt.close()
    print("  ✓ Figure 2 saved")

# =============================================================================
# FIGURE 3: MODEL PERFORMANCE
# =============================================================================
def figure3(output_dir):
    """Figure 3: Forest plot + provider summary."""
    print("Generating Figure 3...")
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    
    # Data (from manuscript Table 4)
    models = [
        ('Claude 3.7 Sonnet', 0.8, 'Anthropic'),
        ('Gemini 1.5 Flash', 0.8, 'Google'),
        ('O3 Mini', 0.8, 'OpenAI'),
        ('Claude 3.5 Haiku', 2.8, 'Anthropic'),
        ('GPT-4o', 6.2, 'OpenAI'),
        ('GPT-4o Mini', 8.4, 'OpenAI'),
        ('Gemini 2.0 Flash', 8.8, 'Google'),
        ('Gemini 2.5 Pro', 10.2, 'Google'),
        ('Gemma 3 27B', 12.4, 'Google'),
        ('Gemini 2.0 Think', 14.1, 'Google'),
        ('Llama 3.2 3B', 16.9, 'Meta'),
        ('Qwen 3 32B', 17.2, 'Alibaba'),
        ('Gemma 3 4B', 35.6, 'Google'),
        ('DeepSeek R1', 36.8, 'DeepSeek'),
    ]
    
    # Panel A: Forest plot
    ax = axes[0]
    y_pos = np.arange(len(models))
    
    for i, (name, rate, provider) in enumerate(models):
        color = COLORS.get(provider, '#666666')
        ax.barh(i, rate, color=color, edgecolor='black', linewidth=0.5, height=0.7)
        ax.text(rate + 0.5, i, f'{rate:.1f}%', va='center', fontsize=8)
    
    ax.axvline(x=9.8, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(9.8, len(models) + 0.3, 'Mean: 9.8%', ha='center', fontsize=9)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([m[0] for m in models], fontsize=9)
    ax.set_xlabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlim(0, 45)
    ax.invert_yaxis()
    add_panel_label(ax, 'A')
    
    # Panel B: Provider summary
    ax = axes[1]
    
    providers = ['Anthropic', 'OpenAI', 'Google', 'Meta', 'Alibaba', 'DeepSeek']
    rates = [1.8, 8.6, 10.2, 16.9, 17.2, 36.8]
    ns = [227, 359, 501, 118, 29, 38]
    
    colors = [COLORS[p] for p in providers]
    bars = ax.bar(providers, rates, color=colors, edgecolor='black', linewidth=1.2, width=0.65)
    
    for bar, rate, n in zip(bars, rates, ns):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width()/2., -3,
                f'n={n}', ha='center', va='top', fontsize=8, color='gray')
    
    ax.set_ylabel('Unsafe Response Rate (%)', fontweight='bold')
    ax.set_xlabel('Provider', fontweight='bold')
    ax.set_ylim(0, 45)
    ax.tick_params(axis='x', rotation=45)
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure3_ModelPerformance.png'), facecolor='white')
    plt.savefig(os.path.join(output_dir, 'Figure3_ModelPerformance.pdf'), facecolor='white')
    plt.close()
    print("  ✓ Figure 3 saved")

# =============================================================================
# FIGURE 4: SAFETY EROSION
# =============================================================================
def figure4(output_dir):
    """Figure 4: Classification transitions + dimension analysis."""
    print("Generating Figure 4...")
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # Panel A: Classification transitions
    ax = axes[0]
    
    # Data: Among 429 Strong conversations under evidence-aligned framing
    categories = ['Remained\nStrong', 'Eroded to\nModerate', 'Collapsed\nto Weak']
    values = [77.4, 12.6, 10.0]
    colors = [COLORS['strong'], COLORS['moderate'], COLORS['weak']]
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2, width=0.6)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Percentage of Conversations (%)', fontweight='bold')
    ax.set_xlabel('Outcome Under Misconception Framing', fontweight='bold')
    ax.set_ylim(0, 95)
    ax.set_title('Starting from Strong (n=429)', fontsize=10, style='italic')
    add_panel_label(ax, 'A')
    
    # Panel B: Dimension comparison
    ax = axes[1]
    
    dimensions = ['Evidence', 'Testimonial', 'Safety', 'Misattrib.', 'Promo.', 'HCP Ref']
    aligned = [93, 61, 87, 68, 91, 84]  # % of max score
    miscon = [89, 83, 85, 77, 81, 77]
    
    x = np.arange(len(dimensions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, aligned, width, label='Evidence-aligned', 
                   color=COLORS['evidence_aligned'], edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x + width/2, miscon, width, label='Misconception',
                   color=COLORS['misconception'], edgecolor='black', linewidth=0.8)
    
    ax.set_ylabel('Score (% of Maximum)', fontweight='bold')
    ax.set_xlabel('Rubric Dimension', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions, rotation=45, ha='right')
    ax.set_ylim(0, 100)
    ax.legend(title='Framing', loc='lower left', frameon=True, edgecolor='gray')
    add_panel_label(ax, 'B')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure4_SafetyErosion.png'), facecolor='white')
    plt.savefig(os.path.join(output_dir, 'Figure4_SafetyErosion.pdf'), facecolor='white')
    plt.close()
    print("  ✓ Figure 4 saved")

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    output_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Output directory: {output_dir}")
    
    figure1(output_dir)
    figure2(output_dir)
    figure3(output_dir)
    figure4(output_dir)
    
    print("\nAll figures regenerated with consistent styling!")
