const fs = require('fs');
const path = require('path');

function analyzePairedShifts() {
    const csvPath = 'LLMalignment/batch_results/final_all_batches_data.csv';
    try {
        const data = fs.readFileSync(csvPath, 'utf8');
        const lines = data.split('\n').filter(l => l.trim() !== '');
        
        // Parse CSV (assuming simple CSV without quoted newlines for now)
        const headers = lines[0].split(',');
        const records = lines.slice(1).map(line => {
            const values = line.split(',');
            const record = {};
            headers.forEach((h, i) => record[h.trim()] = values[i] ? values[i].trim() : '');
            return record;
        });

        console.log("\n=== VALENCE SHIFT ANALYSIS (Regular -> Misinformation) ===");
        
        // Grouping
        const groups = {};
        records.forEach(r => {
            // Key for Valence Shift: model + treatment + format
            const key = `${r.model_name_clean}|${r.treatment_id}|${r.format}`;
            if (!groups[key]) groups[key] = [];
            groups[key].push(r);
        });

        let totalPairs = 0;
        let strongStart = 0;
        let strongToStrong = 0;
        let strongToModerate = 0;
        let strongToWeak = 0;
        let moderateStart = 0;
        let moderateToWeak = 0;

        for (const key in groups) {
            const group = groups[key];
            if (group.length !== 2) continue;

            const pos = group.find(r => r.valence === 'positive');
            const neg = group.find(r => r.valence === 'negative');

            if (!pos || !neg) continue;

            let startRow, endRow;
            // logic: Alt: Neg->Pos | Trad: Pos->Neg
            if (pos.treatment_type === 'alternative') {
                startRow = neg;
                endRow = pos;
            } else if (pos.treatment_type === 'traditional') {
                startRow = pos;
                endRow = neg;
            } else {
                continue;
            }

            totalPairs++;

            if (startRow.Overall_Classification === 'Strong') {
                strongStart++;
                if (endRow.Overall_Classification === 'Strong') strongToStrong++;
                else if (endRow.Overall_Classification === 'Moderate') strongToModerate++;
                else if (endRow.Overall_Classification === 'Weak') strongToWeak++;
            }
            
            if (startRow.Overall_Classification === 'Moderate') {
                moderateStart++;
                if (endRow.Overall_Classification === 'Weak') moderateToWeak++;
            }
        }

        console.log(`Total Paired Conversations: ${totalPairs}`);
        console.log(`Conversations starting as STRONG: ${strongStart}`);
        if (strongStart > 0) {
            const sDeg = strongToModerate + strongToWeak;
            const sDegPct = (sDeg / strongStart) * 100;
            console.log(`  -> Remained Strong: ${strongToStrong} (${(strongToStrong/strongStart*100).toFixed(1)}%)`);
            console.log(`  -> Shifted to Moderate: ${strongToModerate} (${(strongToModerate/strongStart*100).toFixed(1)}%)`);
            console.log(`  -> Collapsed to Weak: ${strongToWeak} (${(strongToWeak/strongStart*100).toFixed(1)}%)`);
            console.log(`  -> TOTAL DEGRADATION (Strong -> Mod/Weak): ${sDeg} (${sDegPct.toFixed(1)}%)`);
        }
        
        // Format Shift
        console.log("\n\n=== FORMAT SHIFT ANALYSIS (Single -> Multi-turn) ===");
        
        const groupsFmt = {};
        records.forEach(r => {
            const key = `${r.model_name_clean}|${r.treatment_id}|${r.valence}`;
            if (!groupsFmt[key]) groupsFmt[key] = [];
            groupsFmt[key].push(r);
        });
        
        let fmtTotal = 0;
        let weakStart = 0;
        let weakToMod = 0;
        let weakToStrong = 0;
        
        for (const key in groupsFmt) {
             const group = groupsFmt[key];
             if (group.length !== 2) continue;
             
             const single = group.find(r => r.format === 'single_turn');
             const multi = group.find(r => r.format === 'multi_turn');
             
             if (!single || !multi) continue;
             
             fmtTotal++;
             
             if (single.Overall_Classification === 'Weak') {
                 weakStart++;
                 if (multi.Overall_Classification === 'Moderate') weakToMod++;
                 if (multi.Overall_Classification === 'Strong') weakToStrong++;
             }
        }
        
        console.log(`Total Paired Conversations: ${fmtTotal}`);
        if (weakStart > 0) {
             const recovered = weakToMod + weakToStrong;
             console.log(`Conversations starting as WEAK (Single-turn): ${weakStart}`);
             console.log(`  -> Recovered to Moderate: ${weakToMod}`);
             console.log(`  -> Recovered to Strong: ${weakToStrong}`);
             console.log(`  -> TOTAL RECOVERY: ${recovered} (${(recovered/weakStart*100).toFixed(1)}%)`);
        }

    } catch (e) {
        console.error("Error:", e.message);
    }
}

analyzePairedShifts();
