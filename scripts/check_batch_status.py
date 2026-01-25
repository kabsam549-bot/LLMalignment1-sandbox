#!/usr/bin/env python3
"""
Check status of a specific batch and download results if available.
"""
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def check_and_download_batch(batch_id: str, output_dir: Path):
    """Check batch status and download results if completed."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print(f"Checking batch: {batch_id}")
    
    try:
        batch = client.batches.retrieve(batch_id)
        
        print(f"\nBatch Status: {batch.status}")
        print(f"Created at: {batch.created_at}")
        print(f"Total requests: {batch.request_counts.get('total', 'N/A')}")
        print(f"Completed: {batch.request_counts.get('completed', 'N/A')}")
        print(f"Failed: {batch.request_counts.get('failed', 'N/A')}")
        
        if batch.status == "completed":
            if batch.output_file_id:
                print(f"\n✅ Batch completed! Downloading results...")
                result_content = client.files.content(batch.output_file_id)
                
                results_file = output_dir / "batch_results.jsonl"
                with open(results_file, 'wb') as f:
                    f.write(result_content.content)
                
                print(f"Results downloaded to: {results_file}")
                
                # Count lines
                with open(results_file, 'r') as f:
                    line_count = sum(1 for _ in f)
                print(f"Total results: {line_count}")
                
                return results_file
            else:
                print("⚠️  Batch completed but no output file available")
        elif batch.status == "failed":
            print("❌ Batch failed")
            if batch.error_file_id:
                print(f"Error file ID: {batch.error_file_id}")
                error_content = client.files.content(batch.error_file_id)
                error_file = output_dir / "batch_error.jsonl"
                with open(error_file, 'wb') as f:
                    f.write(error_content.content)
                print(f"Error file downloaded to: {error_file}")
        else:
            print(f"⏳ Batch is still {batch.status}")
            
    except Exception as e:
        print(f"Error checking batch: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_batch_status.py <batch_id> [output_dir]")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results") / f"batch_{batch_id[:8]}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    check_and_download_batch(batch_id, output_dir)


