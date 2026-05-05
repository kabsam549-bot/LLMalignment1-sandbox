#!/usr/bin/env python3
"""
Resume batch processing after timeout - download and process completed batches.
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
    print("RESUMING BATCH 001 PROCESSING")
    print("=" * 80)
    
    # Batch 001
    batch_001_path = workspace / "Model_Runs_Cleaned/batches/batch_001.json"
    batch_001_run_dir = output_dir / "batch_001_run"
    
    with open(batch_001_path, 'r') as f:
        batch_001_data = json.load(f)
    
    formatted_001 = format_conversations_for_evaluation(batch_001_data)
    print(f"Loaded {len(formatted_001)} conversations from batch 001")
    
    # Create evaluator to download results
    evaluator_001 = BatchEvaluator(prompt, batch_001_run_dir)
    
    batch_001_id = "batch_69174bbf8c708190850dcce3ac62037b"
    print(f"Downloading results for batch {batch_001_id}...")
    
    results_file = evaluator_001.download_results(batch_001_id)
    print(f"Results downloaded to: {results_file}")
    
    print("Parsing and scoring results...")
    scored_results_001 = evaluator_001.parse_batch_results(results_file, formatted_001)
    print(f"✓ Batch 001 scored: {len(scored_results_001)} results")
    
    # Process results
    print("\nProcessing batch 001 outputs...")
    raw_judgments_001 = processor.process_raw_judgments(scored_results_001)
    metadata_001 = processor.extract_metadata_from_conversations(batch_001_data)
    combined_001 = processor.join_judgments_with_metadata(raw_judgments_001, metadata_001)
    
    processor.save_outputs(
        raw_judgments_001,
        metadata_001,
        combined_001,
        output_dir,
        "batch_001"
    )
    
    print(f"\n✓ Batch 001 complete! Processed {len(scored_results_001)} conversations")
    print(f"\nNow you can run batch 002 using the same process.")


if __name__ == "__main__":
    main()

