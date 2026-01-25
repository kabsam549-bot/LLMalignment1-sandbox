BEGIN {
    FS = ",";
    dimensions[1] = "Evidence_R_Adj";
    dimensions[2] = "Testimonial_R_Adj";
    dimensions[3] = "Safety_Rejection_Adj";
    dimensions[4] = "Misatribution_R_Adj";
    dimensions[5] = "Promotion_Adj";
    dimensions[6] = "HCP_Ref_Adj";
    
    classes[1] = "Strong";
    classes[2] = "Moderate";
    classes[3] = "Weak";
}

NR == 1 {
    for (i=1; i<=NF; i++) {
        for (j=1; j<=6; j++) {
            if ($i == dimensions[j]) dim_idx[j] = i;
        }
        if ($i == "Overall_Classification") class_idx = i;
    }
}

NR > 1 {
    cls = $class_idx;
    for (j=1; j<=6; j++) {
        val = $dim_idx[j];
        if (val == "") val = 0;
        sum[cls, j] += val;
        count[cls, j]++;
    }
}

END {
    print "=== DIMENSION VULNERABILITY PROFILE (Priority 3) ===";
    printf "%-15s", "Classification";
    for (j=1; j<=6; j++) printf " | %-12s", substr(dimensions[j], 1, 12);
    print "";
    print "---------------------------------------------------------------------------------------------------";

    for (i=1; i<=3; i++) {
        cls = classes[i];
        printf "%-15s", cls;
        for (j=1; j<=6; j++) {
            avg = (count[cls, j] > 0) ? (sum[cls, j] / count[cls, j]) : 0;
            printf " | %-12.2f", avg;
        }
        print "";
    }
    
    # Calculate "Condition Elasticity" - Comparing Negative vs Positive overall
}
