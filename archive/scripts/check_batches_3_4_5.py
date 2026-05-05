#!/usr/bin/env python3
"""
Check status of batches 3, 4, and 5.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def check_batch_status(batch_id: str, batch_name: str):
    """Check the status of a batch job."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        batch = client.batches.retrieve(batch_id)
        print(f"\n{batch_name}:")
        print(f"  Batch ID: {batch_id}")
        print(f"  Status: {batch.status}")
        print(f"  Total requests: {batch.request_counts.total}")
        print(f"  Completed: {batch.request_counts.completed}")
        print(f"  Failed: {batch.request_counts.failed}")
        
        if batch.status == 'completed':
            print(f"  ✓ COMPLETED!")
            return True
        elif batch.status == 'failed':
            print(f"  ✗ FAILED!")
            return False
        else:
            print(f"  ⏳ Still {batch.status}...")
            return None
            
    except Exception as e:
        print(f"\n{batch_name}:")
        print(f"  Error checking batch: {e}")
        return False

if __name__ == "__main__":
    workspace = Path(__file__).parent
    batch_info_file = workspace / "batch_results/batches_3_4_5_info.json"
    
    # Load batch IDs
    if batch_info_file.exists():
        with open(batch_info_file, 'r') as f:
            batch_ids = json.load(f)
    else:
        # Fallback to hardcoded IDs if file doesn't exist
        batch_ids = {
            '003': 'batch_692dc02bf9688190b91803d47374c2f9',
            '004': 'batch_692dc02e75a48190a175de70dc675d57',
            '005': 'batch_692dc03032ac81909f847c8037b8f0e8'
        }
    
    print("=" * 80)
    print("CHECKING STATUS OF BATCHES 3, 4, AND 5")
    print("=" * 80)
    
    all_complete = True
    for batch_num, batch_id in batch_ids.items():
        if batch_id:
            status = check_batch_status(batch_id, f"Batch {batch_num}")
            if status is not True:
                all_complete = False
        else:
            print(f"\nBatch {batch_num}: Not submitted")
            all_complete = False
    
    if all_complete:
        print("\n" + "=" * 80)
        print("✓ ALL BATCHES COMPLETED!")
        print("=" * 80)
        print("\nYou can now download and process results with:")
        print("  python3 resume_batches_3_4_5.py")

