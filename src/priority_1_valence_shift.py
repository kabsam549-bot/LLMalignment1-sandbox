import csv
from collections import Counter

def run_shift_analysis():
    data_path = 'LLMalignment/batch_results/all_batches_combined_data.csv'
    
    rows = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    # Class order for indices
    class_order = ['Strong', 'Moderate', 'Weak']
    
    for fmt in ['single_turn', 'multi_turn']:
        # Group by model + treatment
        pairs = {}
        for row in rows:
            if row['format'] == fmt:
                key = (row['model_name_clean'], row['treatment_id'])
                if key not in pairs:
                    pairs[key] = {}
                pairs[key][row['valence']] = row['Overall_Classification']
        
        # Build matrix
        matrix = {r: {c: 0 for c in class_order} for r in class_order}
        n_pairs = 0
        
        for key, valences in pairs.items():
            if 'negative' in valences and 'positive' in valences:
                n_pairs += 1
                neg_class = valences['negative']
                pos_class = valences['positive']
                if neg_class in class_order and pos_class in class_order:
                    matrix[neg_class][pos_class] += 1
        
        print(f"\n=== SHIFT MATRIX: {fmt.upper()} (n={n_pairs} pairs) ===")
        
        # Header
        header = "From(Neg)\To(Pos) | " + " | ".join([f"{c:8}" for c in class_order])
        print(header)
        print("-" * len(header))
        
        for r in class_order:
            row_str = f"{r:14} | "
            row_vals = []
            row_sum = sum(matrix[r].values())
            for c in class_order:
                count = matrix[r][c]
                pct = (count / row_sum * 100) if row_sum > 0 else 0
                row_vals.append(f"{count:<3} ({pct:4.1f}%)")
            print(row_str + " | ".join(row_vals))
            
        # Specific stats for the story
        total_strong = sum(matrix['Strong'].values())
        if total_strong > 0:
            s_to_m = matrix['Strong']['Moderate']
            s_to_w = matrix['Strong']['Weak']
            degradation = ((s_to_m + s_to_w) / total_strong) * 100
            print(f"\nStrong Baseline Degradation Rate: {degradation:.1f}%")
            print(f" - Strong -> Moderate (Quiet): {s_to_m} ({(s_to_m/total_strong)*100:.1f}%)")
            print(f" - Strong -> Weak (Collapse): {s_to_w} ({(s_to_w/total_strong)*100:.1f}%)")

if __name__ == "__main__":
    run_shift_analysis()
