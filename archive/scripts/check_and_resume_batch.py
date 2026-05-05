#!/usr/bin/env python3
"""
Check batch status and resume processing when complete.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def check_batch_status(batch_id: str):
    """Check the status of a batch job."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        batch = client.batches.retrieve(batch_id)
        print(f"Batch ID: {batch_id}")
        print(f"Status: {batch.status}")
        print(f"Total requests: {batch.request_counts.total}")
        print(f"Completed: {batch.request_counts.completed}")
        print(f"Failed: {batch.request_counts.failed}")
        
        if batch.status == 'completed':
            print("\n✓ Batch completed!")
            return True
        elif batch.status == 'failed':
            print("\n✗ Batch failed!")
            return False
        else:
            print(f"\n⏳ Batch still {batch.status}...")
            return None
            
    except Exception as e:
        print(f"Error checking batch: {e}")
        return False

if __name__ == "__main__":
    # Batch 001 ID
    batch_id = "batch_69174bbf8c708190850dcce3ac62037b"
    
    print("Checking batch 001 status...")
    check_batch_status(batch_id)

