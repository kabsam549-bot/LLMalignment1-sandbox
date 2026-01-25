const fs = require('fs');

function getSankeyData() {
    const csvPath = 'LLMalignment/batch_results/final_all_batches_data.csv';
    try {
        const data = fs.readFileSync(csvPath, 'utf8');
        const lines = data.split('\n').filter(l => l.trim() !== '');
        const headers = lines[0].split(',');
        const records = lines.slice(1).map(line => {
            const values = line.split(',');
            const record = {};
            headers.forEach((h, i) => record[h.trim()] = values[i] ? values[i].trim() : '');
            return record;
        });

        const flows = {}; 
        // Key: "StartClass->EndClass"

        // Group by model+treatment+format
        const groups = {};
        records.forEach(r => {
            const key = `${r.model_name_clean}|${r.treatment_id}|${r.format}`;
            if (!groups[key]) groups[key] = [];
            groups[key].push(r);
        });

        for (const key in groups) {
            const group = groups[key];
            if (group.length !== 2) continue;

            const pos = group.find(r => r.valence === 'positive');
            const neg = group.find(r => r.valence === 'negative');
            if (!pos || !neg) continue;

            let startRow, endRow;
            if (pos.treatment_type === 'alternative') {
                startRow = neg; endRow = pos; // Regular -> Misinfo
            } else if (pos.treatment_type === 'traditional') {
                startRow = pos; endRow = neg; // Regular -> Misinfo
            } else { continue; }

            const s = startRow.Overall_Classification;
            const e = endRow.Overall_Classification;
            const flowKey = `${s}->${e}`;
            flows[flowKey] = (flows[flowKey] || 0) + 1;
        }

        console.log(JSON.stringify(flows, null, 2));

    } catch (e) {
        console.error(e);
    }
}

getSankeyData();
