BEGIN {
    FS = ",";
    OFS = "|";
    print "Analyzing Valence Shift..."
}

# Find column indices
NR == 1 {
    for (i=1; i<=NF; i++) {
        if ($i == "model_name_clean") model_idx = i;
        if ($i == "treatment_id") treat_idx = i;
        if ($i == "format") format_idx = i;
        if ($i == "valence") valence_idx = i;
        if ($i == "Overall_Classification") class_idx = i;
    }
}

# Store data in memory
NR > 1 {
    key = $model_idx SUBSEP $treat_idx SUBSEP $format_idx;
    val = $valence_idx;
    cls = $class_idx;
    data[key, val] = cls;
    keys[key] = 1;
}

END {
    # Define classes
    c[1] = "Strong"; c[2] = "Moderate"; c[3] = "Weak";
    
    # Analyze Single-Turn
    analyze("single_turn");
    # Analyze Multi-Turn
    analyze("multi_turn");
}

function analyze(fmt) {
    # Initialize matrix
    for (i=1; i<=3; i++) for (j=1; j<=3; j++) matrix[i,j] = 0;
    n_pairs = 0;
    
    for (k in keys) {
        split(k, parts, SUBSEP);
        if (parts[3] == fmt) {
            neg_cls = data[k, "negative"];
            pos_cls = data[k, "positive"];
            
            if (neg_cls != "" && pos_cls != "") {
                n_pairs++;
                # Map class to index
                idx_n = 0; idx_p = 0;
                for (x=1; x<=3; x++) {
                    if (neg_cls == c[x]) idx_n = x;
                    if (pos_cls == c[x]) idx_p = x;
                }
                if (idx_n > 0 && idx_p > 0) matrix[idx_n, idx_p]++;
            }
        }
    }
    
    print "\n=== SHIFT MATRIX: " toupper(fmt) " (n=" n_pairs " pairs) ===";
    print "From(Neg)\\To(Pos) | Strong     | Moderate   | Weak       ";
    print "----------------------------------------------------------";
    
    for (i=1; i<=3; i++) {
        row_sum = matrix[i,1] + matrix[i,2] + matrix[i,3];
        printf "%-14s | ", c[i];
        for (j=1; j<=3; j++) {
            pct = (row_sum > 0) ? (matrix[i,j]/row_sum*100) : 0;
            printf "%-3d (%4.1f%%) | ", matrix[i,j], pct;
        }
        print "";
    }
    
    # Specific stats
    total_strong = matrix[1,1] + matrix[1,2] + matrix[1,3];
    if (total_strong > 0) {
        s_to_m = matrix[1,2];
        s_to_w = matrix[1,3];
        deg = ((s_to_m + s_to_w) / total_strong) * 100;
        print "\nStrong Baseline Degradation Rate: " sprintf("%.1f%%", deg);
        print " - Strong -> Moderate (Quiet): " s_to_m " (" sprintf("%.1f%%", (s_to_m/total_strong)*100) ")";
        print " - Strong -> Weak (Collapse): " s_to_w " (" sprintf("%.1f%%", (s_to_w/total_strong)*100) ")";
    }
}
