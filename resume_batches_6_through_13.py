#!/usr/bin/env python3
"""
Resume processing for batches 6 through 13 - download and process completed batches.
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


def process_batch(batch_num: str, batch_id: str, workspace: Path, prompt: str, processor: BatchResultProcessor):
    """Download and process a single completed batch."""
    print(f"\n{'='*80}")
    print(f"PROCESSING BATCH {batch_num}")
    print(f"{'='*80}")
    
    batch_path = workspace / f"Model_Runs_Cleaned/batches/batch_{batch_num}.json"
    output_dir = workspace / "batch_results"
    batch_run_dir = output_dir / f"batch_{batch_num}_run"
    
    # Load batch data
    with open(batch_path, 'r') as f:
        batch_data = json.load(f)
    
    formatted = format_conversations_for_evaluation(batch_data)
    print(f"Loaded {len(formatted)} conversations from batch {batch_num}")
    
    # Create evaluator to download results
    evaluator = BatchEvaluator(prompt, batch_run_dir)
    
    print(f"Downloading results for batch {batch_id}...")
    results_file = evaluator.download_results(batch_id)
    print(f"Results downloaded to: {results_file}")
    
    print("Parsing and scoring results...")
    scored_results = evaluator.parse_batch_results(results_file, formatted)
    print(f"✓ Batch {batch_num} scored: {len(scored_results)} results")
    
    # Process results
    print("Processing batch outputs...")
    raw_judgments = processor.process_raw_judgments(scored_results)
    metadata = processor.extract_metadata_from_conversations(batch_data)
    combined = processor.join_judgments_with_metadata(raw_judgments, metadata)
    
    processor.save_outputs(
        raw_judgments,
        metadata,
        combined,
        output_dir,
        f"batch_{batch_num}"
    )
    
    print(f"✓ Batch {batch_num} complete! Processed {len(scored_results)} conversations")
    return len(scored_results)


def main():
    workspace = Path(__file__).parent
    prompt_path = workspace / "results/run_20251015_060225/prompt_20251015_060225.txt"
    metadata_csv_path = workspace / "Model_Runs_Cleaned/metadata_mapping.csv"
    batch_info_file = workspace / "batch_results/batches_6_through_13_info.json"
    
    # Load prompt
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    
    processor = BatchResultProcessor(str(metadata_csv_path))
    
    # Load batch IDs
    if batch_info_file.exists():
        with open(batch_info_file, 'r') as f:
            batch_ids = json.load(f)
    else:
        print("Error: batch_info_file not found. Please run run_batches_6_through_13.py first.")
        return
    
    print("=" * 80)
    print("RESUMING BATCHES 6-13 PROCESSING")
    print("=" * 80)
    
    total_processed = 0
    for batch_num in sorted(batch_ids.keys()):
        batch_id = batch_ids.get(batch_num)
        if batch_id:
            try:
                count = process_batch(batch_num, batch_id, workspace, prompt, processor)
                total_processed += count
            except Exception as e:
                print(f"\n✗ Error processing batch {batch_num}: {e}")
        else:
            print(f"\n⚠ Batch {batch_num} not found in batch_info_file")
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: Processed {total_processed} total conversations across batches 6-13")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

