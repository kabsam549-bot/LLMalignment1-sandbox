#!/usr/bin/env python3
"""
Resume batch 002 processing - download and process completed batch.
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
    workspace = Path(__file__).parent
    prompt_path = workspace / "results/run_20251015_060225/prompt_20251015_060225.txt"
    metadata_csv_path = workspace / "Model_Runs_Cleaned/metadata_mapping.csv"
    output_dir = workspace / "batch_results"
    
    # Load prompt
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    
    processor = BatchResultProcessor(str(metadata_csv_path))
    
    print("=" * 80)
    print("RESUMING BATCH 002 PROCESSING")
    print("=" * 80)
    
    # Batch 002
    batch_002_path = workspace / "Model_Runs_Cleaned/batches/batch_002.json"
    batch_002_run_dir = output_dir / "batch_002_run"
    
    with open(batch_002_path, 'r') as f:
        batch_002_data = json.load(f)
    
    formatted_002 = format_conversations_for_evaluation(batch_002_data)
    print(f"Loaded {len(formatted_002)} conversations from batch 002")
    
    # Create evaluator to download results
    evaluator_002 = BatchEvaluator(prompt, batch_002_run_dir)
    
    batch_002_id = "batch_692db133aa6c8190a084eac64b48dc4d"
    print(f"Downloading results for batch {batch_002_id}...")
    
    results_file = evaluator_002.download_results(batch_002_id)
    print(f"Results downloaded to: {results_file}")
    
    print("Parsing and scoring results...")
    scored_results_002 = evaluator_002.parse_batch_results(results_file, formatted_002)
    print(f"✓ Batch 002 scored: {len(scored_results_002)} results")
    
    # Process results
    print("\nProcessing batch 002 outputs...")
    raw_judgments_002 = processor.process_raw_judgments(scored_results_002)
    metadata_002 = processor.extract_metadata_from_conversations(batch_002_data)
    combined_002 = processor.join_judgments_with_metadata(raw_judgments_002, metadata_002)
    
    processor.save_outputs(
        raw_judgments_002,
        metadata_002,
        combined_002,
        output_dir,
        "batch_002"
    )
    
    print(f"\n✓ Batch 002 complete! Processed {len(scored_results_002)} conversations")


if __name__ == "__main__":
    main()

