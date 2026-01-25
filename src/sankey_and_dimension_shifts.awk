BEGIN {
    FS = ",";
}

NR == 1 {
    for (i=1; i<=NF; i++) {
        if ($i == "model_name_clean") model_idx = i;
        if ($i == "treatment_id") treat_idx = i;
        if ($i == "format") format_idx = i;
        if ($i == "valence") valence_idx = i;
        if ($i == "treatment_type") type_idx = i;
        if ($i == "Overall_Classification") class_idx = i;
        if ($i == "Evidence_R_Adj") e_idx = i;
        if ($i == "Testimonial_R_Adj") t_idx = i;
        if ($i == "Safety_Rejection_Adj") s_idx = i;
        if ($i == "Misatribution_R_Adj") m_idx = i;
        if ($i == "Promotion_Adj") p_idx = i;
        if ($i == "HCP_Ref_Adj") h_idx = i;
    }
}

NR > 1 {
    key = $model_idx SUBSEP $treat_idx SUBSEP $format_idx;
    v = $valence_idx;
    t = $type_idx;
    c_val = $class_idx;
    
    is_misinfo = 0;
    if ((t == "alternative" && v == "positive") || (t == "traditional" && v == "negative")) is_misinfo = 1;
    
    if (is_misinfo) {
        data_mis[key] = c_val;
        s_e_m[key] = $e_idx; s_t_m[key] = $t_idx; s_s_m[key] = $s_idx;
        s_m_m[key] = $m_idx; s_p_m[key] = $p_idx; s_h_m[key] = $h_idx;
    } else {
        data_reg[key] = c_val;
        s_e_r[key] = $e_idx; s_t_r[key] = $t_idx; s_s_r[key] = $s_idx;
        s_m_r[key] = $m_idx; s_p_r[key] = $p_idx; s_h_r[key] = $h_idx;
    }
    keys[key] = 1;
}

END {
    print "--- SANKEY DATA (REGULAR -> MISINFO) ---"
    print "Format,Source,Target,Count"
    
    for (k in keys) {
        split(k, parts, SUBSEP);
        fmt = parts[3];
        src_c = data_reg[k];
        tgt_c = data_mis[k];
        if (src_c != "" && tgt_c != "") {
            sankey[fmt, src_c, tgt_c]++;
            
            if (src_c == "Strong" && tgt_c != "Strong") {
                diff_e += (s_e_m[k] - s_e_r[k]);
                diff_t += (s_t_m[k] - s_t_r[k]);
                diff_s += (s_s_m[k] - s_s_r[k]);
                diff_m += (s_m_m[k] - s_m_r[k]);
                diff_p += (s_p_m[k] - s_p_r[k]);
                diff_h += (s_h_m[k] - s_h_r[k]);
                shift_count++;
            }
        }
    }
    
    fmts[1] = "single_turn"; fmts[2] = "multi_turn";
    classes[1] = "Strong"; classes[2] = "Moderate"; classes[3] = "Weak";
    
    for (f=1; f<=2; f++) {
        for (i=1; i<=3; i++) {
            for (j=1; j<=3; j++) {
                cnt = sankey[fmts[f], classes[i], classes[j]];
                if (cnt > 0) print fmts[f] "," classes[i] "," classes[j] "," cnt;
            }
        }
    }
    
    print "\n--- DIMENSION DEGRADATION (MEAN DELTA FOR SHIFTED CASES) ---"
    print "Dimension | Mean Delta (Negative indicates drop)"
    print "-----------------------------------------------"
    if (shift_count > 0) {
        printf "Evidence Accuracy      | %.2f\n", diff_e / shift_count;
        printf "Testimonial Eval       | %.2f\n", diff_t / shift_count;
        printf "Safety Guidance        | %.2f\n", diff_s / shift_count;
        printf "Misattribution Corr    | %.2f\n", diff_m / shift_count;
        printf "Promotional Response   | %.2f\n", diff_p / shift_count;
        printf "HCP Reference          | %.2f\n", diff_h / shift_count;
    }
}
