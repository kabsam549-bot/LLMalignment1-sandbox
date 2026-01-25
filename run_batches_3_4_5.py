#!/usr/bin/env python3
"""
Run batches 3, 4, and 5 simultaneously - submit all at once without waiting.
"""
import json
from pathlib import Path
from src.batch_evaluator import BatchEvaluator

def format_conversations_for_evaluation(conversations_data):
    """Format conversations from batch format to evaluation format."""
    formatted = []
    
    for item in conversations_data:
        set_id = item['set_id']
        conversation_id = set_id
        
        conversation_text = ""
        for conv in item.get('conversations', []):
            exchanges = conv.get('exchanges', [])
            for i, exchange in enumerate(exchanges):
                role = exchange.get('role', '')
                content = exchange.get('content', '')
                
                if role == 'user':
                    q_num = (i // 2) + 1
                    conversation_text += f"Q{q_num}: {content}\n\n"
                elif role == 'assistant':
                    a_num = (i // 2) + 1
                    conversation_text += f"A{a_num}: {content}\n\n"
        
        formatted.append({
            'conversation_id': conversation_id,
            'set_id': set_id,
            'conversation_text': conversation_text.strip()
        })
    
    return formatted


def submit_batch(batch_num: str, workspace: Path, prompt: str):
    """Submit a single batch and return the batch ID."""
    print(f"\n{'='*80}")
    print(f"PROCESSING BATCH {batch_num}")
    print(f"{'='*80}")
    
    batch_path = workspace / f"Model_Runs_Cleaned/batches/batch_{batch_num}.json"
    output_dir = workspace / "batch_results"
    batch_run_dir = output_dir / f"batch_{batch_num}_run"
    
    batch_run_dir.mkdir(parents=True, exist_ok=True)
    
    # Load batch data
    print(f"Loading batch from: {batch_path}")
    with open(batch_path, 'r') as f:
        batch_data = json.load(f)
    print(f"Loaded {len(batch_data)} conversations from batch {batch_num}")
    
    # Format for evaluation
    formatted_conversations = format_conversations_for_evaluation(batch_data)
    print(f"Formatted {len(formatted_conversations)} conversations for evaluation")
    
    # Create evaluator
    evaluator = BatchEvaluator(prompt, batch_run_dir)
    
    # Create batch file
    batch_requests = evaluator.judge.prepare_batch_input(formatted_conversations)
    batch_file = evaluator.output_dir / "batch_input.jsonl"
    with open(batch_file, 'w') as f:
        for request in batch_requests:
            f.write(json.dumps(request) + '\n')
    print(f"Created batch input file with {len(batch_requests)} requests")
    
    # Submit batch (don't wait)
    batch_id = evaluator.submit_batch(batch_file)
    print(f"\n✓ Batch {batch_num} submitted: {batch_id}")
    
    return batch_id


def main():
    print("=" * 80)
    print("SUBMITTING BATCHES 3, 4, AND 5 SIMULTANEOUSLY")
    print("=" * 80)
    
    workspace = Path(__file__).parent
    prompt_path = workspace / "results/run_20251015_060225/prompt_20251015_060225.txt"
    
    # Load prompt
    print(f"\nLoading prompt from: {prompt_path}")
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    print(f"Prompt loaded ({len(prompt)} characters)")
    
    # Submit all batches
    batch_ids = {}
    for batch_num in ['003', '004', '005']:
        try:
            batch_id = submit_batch(batch_num, workspace, prompt)
            batch_ids[batch_num] = batch_id
        except Exception as e:
            print(f"\n✗ Error submitting batch {batch_num}: {e}")
            batch_ids[batch_num] = None
    
    # Summary
    print(f"\n{'='*80}")
    print("SUBMISSION SUMMARY")
    print(f"{'='*80}")
    for batch_num, batch_id in batch_ids.items():
        if batch_id:
            print(f"  Batch {batch_num}: {batch_id}")
        else:
            print(f"  Batch {batch_num}: FAILED to submit")
    
    # Save batch IDs for later reference
    batch_info_file = workspace / "batch_results/batches_3_4_5_info.json"
    batch_info_file.parent.mkdir(parents=True, exist_ok=True)
    with open(batch_info_file, 'w') as f:
        json.dump(batch_ids, f, indent=2)
    print(f"\nBatch IDs saved to: {batch_info_file}")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("All batches have been submitted and will run in parallel.")
    print("\nTo check status, you can use:")
    print("  python3 check_batch_status.py  # (create this script)")
    print("\nOr check manually via OpenAI API.")
    print("\nWhen batches complete, download and process with:")
    print("  python3 resume_batch_processing.py  # (adapt for batches 3-5)")


if __name__ == "__main__":
    main()

