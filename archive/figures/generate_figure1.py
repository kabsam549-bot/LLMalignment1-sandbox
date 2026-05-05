import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.gridspec as gridspec

# Set global font to sans-serif (Nature style)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['figure.dpi'] = 300

def create_figure():
    fig = plt.figure(figsize=(12, 10), facecolor='white')
    gs = gridspec.GridSpec(2, 1, height_ratios=[1.2, 1], hspace=0.3)

    # ==========================================
    # PANEL A: Factorial Design (Tree Structure)
    # ==========================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.axis('off')
    
    # Title Panel A
    ax1.text(2, 98, 'A', fontsize=24, fontweight='bold', ha='left', va='top')
    ax1.text(8, 97, 'Experimental Design (2×2×2 Factorial)', fontsize=14, fontweight='bold', ha='left', va='top')

    # Coordinates for tree levels
    level_x = [10, 35, 60, 85]
    
    # Root node (start) is implicit, branching to Factor 1: Format
    # Level 1: Format
    y_starts = [75, 25]
    formats = ['Single-turn', 'Multi-turn']
    
    # Connectors and Boxes for Level 1
    for i, y in enumerate(y_starts):
        # Line from root (virtual)
        # ax1.plot([5, level_x[0]], [50, y], 'k-', lw=1, color='#555555') 
        
        # Box
        rect = patches.FancyBboxPatch((level_x[0]-8, y-6), 16, 12, boxstyle="round,pad=0.5", 
                                      ec="#333333", fc="#E0E0E0", lw=1.5)
        ax1.add_patch(rect)
        ax1.text(level_x[0], y, formats[i], ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Label Factor 1
        if i == 0:
            ax1.text(level_x[0], y+10, 'Factor 1: Format', ha='center', fontsize=10, fontstyle='italic', color='#555555')

    # Level 2: Treatment (branch from each Format)
    treatments = ['Evidence-based', 'Alternative']
    colors = ['#E6F4EA', '#FCE8E6'] # Light Green, Light Red
    stroke_colors = ['#1E8E3E', '#D93025'] # Dark Green, Dark Red
    
    # Offsets for branching
    y_l2 = [85, 65, 35, 15] # 4 nodes
    
    for i in range(2): # From each Level 1 node
        src_y = y_starts[i]
        for j in range(2): # To 2 Level 2 nodes
            dst_idx = i*2 + j
            dst_y = y_l2[dst_idx]
            
            # Draw connecting line
            path_data = [
                (Path.MOVETO, (level_x[0]+8, src_y)),
                (Path.CURVE4, (level_x[0]+20, src_y)), # Control 1
                (Path.CURVE4, (level_x[1]-20, dst_y)), # Control 2
                (Path.LINETO, (level_x[1]-8, dst_y))
            ]
            codes, verts = zip(*path_data)
            path = Path(verts, codes)
            patch = patches.PathPatch(path, facecolor='none', lw=1, edgecolor='#999999')
            ax1.add_patch(patch)
            
            # Draw Box
            rect = patches.FancyBboxPatch((level_x[1]-8, dst_y-4), 16, 8, boxstyle="round,pad=0.4", 
                                          ec=stroke_colors[j], fc=colors[j], lw=1.5)
            ax1.add_patch(rect)
            ax1.text(level_x[1], dst_y, treatments[j], ha='center', va='center', fontsize=10, color='black')

    ax1.text(level_x[1], 98, 'Factor 2: Treatment', ha='center', fontsize=10, fontstyle='italic', color='#555555')

    # Level 3: Valence (branch from each Treatment) -> 8 endpoints
    valences = ['Positive', 'Negative']
    # y positions for 8 final nodes
    y_l3 = [92, 86, 72, 66, 42, 36, 22, 16]
    
    for i in range(4): # From each Level 2 node
        src_y = y_l2[i]
        # Inherit color style from parent (treatment type)
        # i=0,1 (Evidence) -> j=0 style
        # i=2,3 (Alternative) -> j=1 style
        style_idx = i % 2 
        
        for j in range(2): # To 2 Level 3 nodes
            dst_idx = i*2 + j
            dst_y = y_l3[dst_idx]
            
            # Draw connecting line
            path_data = [
                (Path.MOVETO, (level_x[1]+8, src_y)),
                (Path.CURVE4, (level_x[1]+15, src_y)),
                (Path.CURVE4, (level_x[2]-15, dst_y)),
                (Path.LINETO, (level_x[2]-8, dst_y))
            ]
            codes, verts = zip(*path_data)
            path = Path(verts, codes)
            patch = patches.PathPatch(path, facecolor='none', lw=1, edgecolor='#999999')
            ax1.add_patch(patch)
            
            # Draw Endpoint Box
            rect = patches.FancyBboxPatch((level_x[2]-8, dst_y-2.5), 16, 5, boxstyle="round,pad=0.2", 
                                          ec='#555555', fc='white', lw=1)
            ax1.add_patch(rect)
            ax1.text(level_x[2], dst_y, f"{valences[j]}", ha='center', va='center', fontsize=9)
            
            # Add small label for the condition count
            # ax1.text(level_x[2]+10, dst_y, f"Cond {dst_idx+1}", ha='left', va='center', fontsize=8, color='#777')

    ax1.text(level_x[2], 98, 'Factor 3: Valence', ha='center', fontsize=10, fontstyle='italic', color='#555555')
    
    # Final label bracket
    ax1.plot([level_x[3], level_x[3]], [15, 93], 'k-', lw=1.5, color='#333333') # Vertical bar
    ax1.plot([level_x[3], level_x[3]-2], [15, 15], 'k-', lw=1.5, color='#333333') # Bottom tick
    ax1.plot([level_x[3], level_x[3]-2], [93, 93], 'k-', lw=1.5, color='#333333') # Top tick
    
    ax1.text(level_x[3]+2, 54, "8 Experimental\nConditions", ha='left', va='center', fontsize=12, fontweight='bold')


    # ==========================================
    # PANEL B: Evaluation Pipeline (Flowchart)
    # ==========================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 50)
    ax2.axis('off')
    
    # Title Panel B
    ax2.text(2, 48, 'B', fontsize=24, fontweight='bold', ha='left', va='top')
    ax2.text(8, 47, 'Evaluation Pipeline', fontsize=14, fontweight='bold', ha='left', va='top')

    # Flowchart Nodes
    # 1. User Query
    # 2. 14 LLMs
    # 3. 6-Dim Rubric
    # 4. Classification
    
    nodes_x = [15, 40, 65, 90]
    center_y = 25
    
    # Arrow properties
    arrow_props = dict(facecolor='#555555', edgecolor='none', shrink=0.05, headwidth=10, headlength=10)
    
    # Node 1: User Query
    rect1 = patches.FancyBboxPatch((nodes_x[0]-10, center_y-5), 20, 10, boxstyle="round,pad=0.5", 
                                   ec="#005A9C", fc="#E8F0FE", lw=2)
    ax2.add_patch(rect1)
    ax2.text(nodes_x[0], center_y+1, "User Query", ha='center', va='center', fontweight='bold', fontsize=11)
    ax2.text(nodes_x[0], center_y-2, "(Prompt)", ha='center', va='center', fontsize=9, color='#444')
    
    # Arrow 1->2
    ax2.annotate('', xy=(nodes_x[1]-10, center_y), xytext=(nodes_x[0]+10, center_y), arrowprops=arrow_props)
    
    # Node 2: 14 LLMs
    rect2 = patches.FancyBboxPatch((nodes_x[1]-10, center_y-5), 20, 10, boxstyle="round,pad=0.5", 
                                   ec="#B45F06", fc="#FEF7E0", lw=2)
    ax2.add_patch(rect2)
    ax2.text(nodes_x[1], center_y+1, "14 LLMs", ha='center', va='center', fontweight='bold', fontsize=11)
    ax2.text(nodes_x[1], center_y-2, "Response Gen", ha='center', va='center', fontsize=9, color='#444')

    # Arrow 2->3
    ax2.annotate('', xy=(nodes_x[2]-10, center_y), xytext=(nodes_x[1]+10, center_y), arrowprops=arrow_props)

    # Node 3: Rubric
    rect3 = patches.FancyBboxPatch((nodes_x[2]-10, center_y-5), 20, 10, boxstyle="round,pad=0.5", 
                                   ec="#A020F0", fc="#F3E5F5", lw=2)
    ax2.add_patch(rect3)
    ax2.text(nodes_x[2], center_y+1, "Scoring Rubric", ha='center', va='center', fontweight='bold', fontsize=11)
    ax2.text(nodes_x[2], center_y-2, "6 Dimensions", ha='center', va='center', fontsize=9, color='#444')
    
    # Arrow 3->4
    ax2.annotate('', xy=(nodes_x[3]-10, center_y), xytext=(nodes_x[2]+10, center_y), arrowprops=arrow_props)

    # Node 4: Classification
    rect4 = patches.FancyBboxPatch((nodes_x[3]-10, center_y-7), 20, 14, boxstyle="round,pad=0.5", 
                                   ec="#333333", fc="#EEEEEE", lw=2)
    ax2.add_patch(rect4)
    ax2.text(nodes_x[3], center_y+4, "Classification", ha='center', va='center', fontweight='bold', fontsize=11)
    
    # Traffic light circles
    circle_y_base = center_y + 1
    ax2.add_patch(patches.Circle((nodes_x[3]-6, circle_y_base-3), 1, fc='#1E8E3E', ec='none')) # Green
    ax2.text(nodes_x[3]-4, circle_y_base-3, "Strong", ha='left', va='center', fontsize=8)
    
    ax2.add_patch(patches.Circle((nodes_x[3]-6, circle_y_base-6), 1, fc='#F9AB00', ec='none')) # Yellow
    ax2.text(nodes_x[3]-4, circle_y_base-6, "Moderate", ha='left', va='center', fontsize=8)

    ax2.add_patch(patches.Circle((nodes_x[3]-6, circle_y_base-9), 1, fc='#D93025', ec='none')) # Red
    ax2.text(nodes_x[3]-4, circle_y_base-9, "Weak", ha='left', va='center', fontsize=8)

    plt.tight_layout()
    plt.savefig('/Users/ClawdBot/clawd/LLMalignment/figures/Figure1_Architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('/Users/ClawdBot/clawd/LLMalignment/figures/Figure1_Architecture.pdf', bbox_inches='tight')
    print("Figure generated successfully.")

if __name__ == "__main__":
    create_figure()
