#!/usr/bin/env python3
"""
Validation script for cleaned model runs data.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict


def validate_cleaned_data():
    """Run validation checks on cleaned data."""
    base_dir = Path(__file__).parent.parent
    cleaned_dir = base_dir / "Model_Runs_Cleaned"
    
    print("="*80)
    print("VALIDATION REPORT FOR CLEANED DATA")
    print("="*80)
    print()
    
    # Load metadata
    metadata_file = cleaned_dir / "metadata_mapping.csv"
    all_set_ids = []
    metadata_by_status = {'valid': 0, 'truncated': 0}
    
    with open(metadata_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_set_ids.append(row['set_id'])
            if row['is_truncated'] == 'True':
                metadata_by_status['truncated'] += 1
            else:
                metadata_by_status['valid'] += 1
    
    print(f"✓ Metadata file loaded: {len(all_set_ids)} total records")
    print(f"  - Valid conversations: {metadata_by_status['valid']}")
    print(f"  - Truncated (logged): {metadata_by_status['truncated']}")
    print()
    
    # Check for duplicate set_ids
    unique_set_ids = set(all_set_ids)
    if len(unique_set_ids) == len(all_set_ids):
        print("✓ No duplicate set_ids found")
    else:
        print(f"✗ WARNING: Found {len(all_set_ids) - len(unique_set_ids)} duplicate set_ids!")
        duplicates = [sid for sid in all_set_ids if all_set_ids.count(sid) > 1]
        print(f"  Duplicates: {set(duplicates)}")
    print()
    
    # Load and validate batches
    batches_dir = cleaned_dir / "batches"
    manifest_file = batches_dir / "batch_manifest.json"
    
    with open(manifest_file) as f:
        manifest = json.load(f)
    
    print(f"✓ Batch manifest loaded: {manifest['total_batches']} batches")
    print(f"  Total conversations in batches: {manifest['total_conversations']}")
    print()
    
    # Validate each batch
    total_in_batches = 0
    batch_set_ids = []
    issues = []
    
    for batch_info in manifest['batches']:
        batch_file = batches_dir / batch_info['batch_file']
        with open(batch_file) as f:
            batch_data = json.load(f)
        
        total_in_batches += len(batch_data)
        
        # Check each conversation
        for conv in batch_data:
            batch_set_ids.append(conv['set_id'])
            
            # Validate structure
            if 'conversations' not in conv:
                issues.append(f"Missing 'conversations' in {conv['set_id']}")
                continue
            
            if len(conv['conversations']) != 1:
                issues.append(f"Expected 1 conversation object in {conv['set_id']}, got {len(conv['conversations'])}")
                continue
            
            exchanges = conv['conversations'][0].get('exchanges', [])
            
            # Should have 10 exchanges (5 Q&A pairs)
            if len(exchanges) != 10:
                issues.append(f"Expected 10 exchanges in {conv['set_id']}, got {len(exchanges)}")
            
            # Check alternating user/assistant
            for i, exchange in enumerate(exchanges):
                expected_role = 'user' if i % 2 == 0 else 'assistant'
                if exchange.get('role') != expected_role:
                    issues.append(f"Wrong role at position {i} in {conv['set_id']}: expected {expected_role}, got {exchange.get('role')}")
    
    if total_in_batches == manifest['total_conversations']:
        print(f"✓ Batch counts match manifest")
    else:
        print(f"✗ WARNING: Batch count mismatch!")
        print(f"  Manifest says: {manifest['total_conversations']}")
        print(f"  Actually found: {total_in_batches}")
    print()
    
    # Check if batch set_ids match valid metadata set_ids
    valid_set_ids = [sid for i, sid in enumerate(all_set_ids) 
                     if list(csv.DictReader(open(metadata_file)))[i]['is_truncated'] != 'True']
    
    batch_set_id_set = set(batch_set_ids)
    valid_set_id_set = set([sid for sid in all_set_ids if sid not in 
                            [row['set_id'] for row in csv.DictReader(open(metadata_file)) 
                             if row['is_truncated'] == 'True']])
    
    if len(batch_set_ids) == metadata_by_status['valid']:
        print(f"✓ All valid conversations from metadata are in batches")
    else:
        print(f"  Batch conversations: {len(batch_set_ids)}")
        print(f"  Valid in metadata: {metadata_by_status['valid']}")
    print()
    
    # Report issues
    if issues:
        print(f"✗ Found {len(issues)} structural issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("✓ No structural issues found in batch conversations")
    print()
    
    # Load summary
    summary_file = cleaned_dir / "data_summary.json"
    with open(summary_file) as f:
        summary = json.load(f)
    
    print("Summary Statistics:")
    print(f"  Total before cleaning: {summary['total_conversations_before']}")
    print(f"  Total after cleaning: {summary['total_conversations_after']}")
    print(f"  Truncated removed: {summary['truncated_conversations_removed']}")
    print(f"  Thinking removed: {summary['conversations_with_thinking_removed']}")
    print(f"  Retention rate: {summary['total_conversations_after']/summary['total_conversations_before']*100:.1f}%")
    print()
    
    # Check model coverage
    print("Per-Model Statistics:")
    print(f"{'Model':<45} {'Valid':<8} {'Truncated':<10} {'Thinking':<10}")
    print("-" * 80)
    for model, stats in sorted(summary['by_model'].items()):
        retention = stats['total_conversations']
        truncated = stats['truncated_removed']
        thinking = stats['thinking_removed']
        retention_pct = retention / 120 * 100
        print(f"{model:<45} {retention:<8} {truncated:<10} {thinking:<10} ({retention_pct:.0f}%)")
    print()
    
    print("Breakdown by variables:")
    for category, counts in summary['breakdown'].items():
        print(f"  {category}:")
        for key, count in sorted(counts.items()):
            print(f"    {key}: {count}")
    print()
    
    print("="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    
    return {
        'total_conversations': len(batch_set_ids),
        'unique_set_ids': len(unique_set_ids) == len(all_set_ids),
        'issues_count': len(issues),
        'retention_rate': summary['total_conversations_after']/summary['total_conversations_before']
    }


if __name__ == "__main__":
    results = validate_cleaned_data()
    
    if results['unique_set_ids'] and results['issues_count'] == 0:
        print("\n✓ All validation checks passed!")
    else:
        print("\n⚠ Some validation issues detected. Review above.")


