import csv
import json
from collections import Counter, defaultdict

def run_analysis():
    data_path = 'LLMalignment/batch_results/all_batches_combined_data.csv'
    
    rows = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean numeric fields
            for col in ['Evidence_R_Adj', 'Testimonial_R_Adj', 'Safety_Rejection_Adj', 
                        'Misatribution_R_Adj', 'Promotion_Adj', 'HCP_Ref_Adj', 'Total_Score']:
                try:
                    row[col] = float(row[col]) if row[col] else 0.0
                except:
                    row[col] = 0.0
            rows.append(row)
            
    class_order = ['Strong', 'Moderate', 'Weak']
    dimensions = ['Evidence_R_Adj', 'Testimonial_R_Adj', 'Safety_Rejection_Adj', 
                  'Misatribution_R_Adj', 'Promotion_Adj', 'HCP_Ref_Adj']
    
    # --- PRIORITY 1: SHIFT MATRICES ---
    shift_results = []
    for fmt in ['single_turn', 'multi_turn']:
        pairs = {}
        for row in rows:
            if row['format'] == fmt:
                key = (row['model_name_clean'], row['treatment_id'])
                if key not in pairs: pairs[key] = {}
                pairs[key][row['valence']] = row
        
        matrix = {r: {c: 0 for c in class_order} for r in class_order}
        n_pairs = 0
        
        # Track dimension changes for P3
        dim_deltas = defaultdict(list)
        
        for key, valences in pairs.items():
            if 'negative' in valences and 'positive' in valences:
                n_pairs += 1
                neg_row = valences['negative']
                pos_row = valences['positive']
                
                n_cls = neg_row['Overall_Classification']
                p_cls = pos_row['Overall_Classification']
                
                if n_cls in class_order and p_cls in class_order:
                    matrix[n_cls][p_cls] += 1
                    shift_results.append({
                        'model': key[0],
                        'treatment_id': key[1],
                        'format': fmt,
                        'from_class': n_cls,
                        'to_class': p_cls
                    })
                    
                    # If it degraded (Strong -> Moderate/Weak), log dimension deltas
                    if n_cls == 'Strong' and p_cls != 'Strong':
                        for d in dimensions:
                            delta = pos_row[d] - neg_row[d]
                            dim_deltas[d].append(delta)

        # Output CSV for Priority 1 (Classification Transitions)
        with open(f'LLMalignment/results/classification_transitions_{fmt}.csv', 'w') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['From_Neg', 'To_Pos_Strong', 'To_Pos_Moderate', 'To_Pos_Weak'])
            for r in class_order:
                writer.writerow([r, matrix[r]['Strong'], matrix[r]['Moderate'], matrix[r]['Weak']])

    # --- PRIORITY 3: DIMENSION VULNERABILITY ---
    # Calculate mean score for each dimension by classification level
    dim_profiles = {cls: {d: [] for d in dimensions} for cls in class_order}
    for row in rows:
        cls = row['Overall_Classification']
        if cls in class_order:
            for d in dimensions:
                dim_profiles[cls][d].append(row[d])
    
    with open('LLMalignment/results/dimension_vulnerability_profile.csv', 'w') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['Classification'] + dimensions)
        for cls in class_order:
            means = [sum(dim_profiles[cls][d])/len(dim_profiles[cls][d]) if dim_profiles[cls][d] else 0 for d in dimensions]
            writer.writerow([cls] + means)

    print("DONE: Generated Priority 1 & 3 analysis files.")
    print("Files created in LLMalignment/results/:")
    print(" - classification_transitions_single_turn.csv")
    print(" - classification_transitions_multi_turn.csv")
    print(" - dimension_vulnerability_profile.csv")

if __name__ == "__main__":
    run_analysis()
