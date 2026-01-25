BEGIN {
    FS = ",";
    print "Analyzing Misinformation Shift (Paired Comparison)..."
}

# Find column indices
NR == 1 {
    for (i=1; i<=NF; i++) {
        if ($i == "model_name_clean") model_idx = i;
        if ($i == "treatment_id") treat_idx = i;
        if ($i == "format") format_idx = i;
        if ($i == "valence") valence_idx = i;
        if ($i == "treatment_type") type_idx = i;
        if ($i == "Overall_Classification") class_idx = i;
    }
}

# Store data
NR > 1 {
    # group = model + treatment + format
    key = $model_idx SUBSEP $treat_idx SUBSEP $format_idx;
    v = $valence_idx;
    t = $type_idx;
    cls = $class_idx;
    
    # Classify as Misinfo or Regular
    # Alt+Pos = Misinfo, Alt+Neg = Regular
    # Trad+Neg = Misinfo, Trad+Pos = Regular
    is_misinfo = 0;
    if ((t == "alternative" && v == "positive") || (t == "traditional" && v == "negative")) is_misinfo = 1;
    
    if (is_misinfo) {
        data_mis[key] = cls;
    } else {
        data_reg[key] = cls;
    }
    keys[key] = 1;
}

END {
    c[1] = "Strong"; c[2] = "Moderate"; c[3] = "Weak";
    
    analyze("single_turn");
    analyze("multi_turn");
}

function analyze(fmt) {
    for (i=1; i<=3; i++) for (j=1; j<=3; j++) matrix[i,j] = 0;
    n_pairs = 0;
    
    for (k in keys) {
        split(k, parts, SUBSEP);
        if (parts[3] == fmt) {
            reg_cls = data_reg[k];
            mis_cls = data_mis[k];
            
            if (reg_cls != "" && mis_cls != "") {
                n_pairs++;
                idx_r = 0; idx_m = 0;
                for (x=1; x<=3; x++) {
                    if (reg_cls == c[x]) idx_r = x;
                    if (mis_cls == c[x]) idx_m = x;
                }
                if (idx_r > 0 && idx_m > 0) matrix[idx_r, idx_m]++;
            }
        }
    }
    
    print "\n=== MISINFO SHIFT MATRIX: " toupper(fmt) " (n=" n_pairs " pairs) ===";
    print "From(Regular)\\To(Misinfo) | Strong     | Moderate   | Weak       ";
    print "--------------------------------------------------------------------";
    
    for (i=1; i<=3; i++) {
        row_sum = matrix[i,1] + matrix[i,2] + matrix[i,3];
        printf "%-25s | ", c[i];
        for (j=1; j<=3; j++) {
            pct = (row_sum > 0) ? (matrix[i,j]/row_sum*100) : 0;
            printf "%-3d (%4.1f%%) | ", matrix[i,j], pct;
        }
        print "";
    }
    
    total_strong = matrix[1,1] + matrix[1,2] + matrix[1,3];
    if (total_strong > 0) {
        s_to_m = matrix[1,2];
        s_to_w = matrix[1,3];
        deg = ((s_to_m + s_to_w) / total_strong) * 100;
        print "\nStrong Baseline (Regular) Degradation Rate under Misinfo: " sprintf("%.1f%%", deg);
        print " - Strong -> Moderate (Quiet): " s_to_m " (" sprintf("%.1f%%", (s_to_m/total_strong)*100) ")";
        print " - Strong -> Weak (Collapse): " s_to_w " (" sprintf("%.1f%%", (s_to_w/total_strong)*100) ")";
    }
}
