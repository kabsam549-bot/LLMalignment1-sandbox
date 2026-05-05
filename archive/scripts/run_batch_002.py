#!/usr/bin/env python3
"""
Run batch evaluation for batch 002.
"""
import json
from pathlib import Path
from src.batch_evaluator import BatchEvaluator
from src.batch_result_processor import BatchResultProcessor

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


def main():
    print("=" * 80)
    print("BATCH 002 EVALUATION")
    print("=" * 80)
    
    workspace = Path("/Users/rkouzy/Documents/LLM_Alignment")
    prompt_path = workspace / "results/run_20251015_060225/prompt_20251015_060225.txt"
    batch_002_path = workspace / "Model_Runs_Cleaned/batches/batch_002.json"
    metadata_csv_path = workspace / "Model_Runs_Cleaned/metadata_mapping.csv"
    output_dir = workspace / "batch_results"
    batch_002_run_dir = output_dir / "batch_002_run"
    
    batch_002_run_dir.mkdir(parents=True, exist_ok=True)
    
    # Load prompt
    print(f"Loading prompt from: {prompt_path}")
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    print(f"Prompt loaded ({len(prompt)} characters)")
    
    # Load batch 002
    print(f"\nLoading batch from: {batch_002_path}")
    with open(batch_002_path, 'r') as f:
        batch_002_data = json.load(f)
    print(f"Loaded {len(batch_002_data)} conversations from batch 002")
    
    # Format for evaluation
    formatted_conversations = format_conversations_for_evaluation(batch_002_data)
    print(f"Formatted {len(formatted_conversations)} conversations for evaluation")
    
    # Create evaluator
    evaluator = BatchEvaluator(prompt, batch_002_run_dir)
    
    print("\nStarting batch evaluation for batch 002...")
    print("This will:")
    print("  1. Create batch input file")
    print("  2. Submit to OpenAI Batch API")
    print("  3. Wait for completion (up to 60 minutes)")
    print("  4. Download and parse results")
    print("  5. Apply scoring")
    
    # Step 1: Create batch file
    batch_requests = evaluator.judge.prepare_batch_input(formatted_conversations)
    batch_file = evaluator.output_dir / "batch_input.jsonl"
    with open(batch_file, 'w') as f:
        for request in batch_requests:
            f.write(json.dumps(request) + '\n')
    print(f"\nCreated batch input file with {len(batch_requests)} requests")
    
    # Step 2: Submit batch
    batch_id = evaluator.submit_batch(batch_file)
    print(f"\n✓ Batch 002 submitted: {batch_id}")
    print(f"\nYou can check status with:")
    print(f"  python3 check_and_resume_batch.py")
    print(f"\nOr wait for it to complete (this may take 30-60+ minutes)...")
    
    # Step 3: Wait for completion
    try:
        evaluator.wait_for_batch(batch_id)
        
        # Step 4: Download results
        results_file = evaluator.download_results(batch_id)
        
        # Step 5: Parse and score
        scored_results = evaluator.parse_batch_results(results_file, formatted_conversations)
        print(f"\n✓ Batch 002 completed: {len(scored_results)} results")
        
        # Process outputs
        print("\nProcessing batch 002 outputs...")
        processor = BatchResultProcessor(str(metadata_csv_path))
        raw_judgments = processor.process_raw_judgments(scored_results)
        metadata = processor.extract_metadata_from_conversations(batch_002_data)
        combined = processor.join_judgments_with_metadata(raw_judgments, metadata)
        
        processor.save_outputs(
            raw_judgments,
            metadata,
            combined,
            output_dir,
            "batch_002"
        )
        
        print(f"\n✓ Batch 002 complete! Processed {len(scored_results)} conversations")
        print(f"\nNext step: Combine batches 001 and 002")
        
    except Exception as e:
        print(f"\n⚠ Batch still processing or timed out: {e}")
        print(f"\nBatch ID: {batch_id}")
        print(f"Check status later and resume processing.")


if __name__ == "__main__":
    main()

