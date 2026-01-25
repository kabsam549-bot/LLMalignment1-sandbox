#!/usr/bin/env python3
"""
Run batch evaluation for batches 001 and 002 using the 060225 prompt configuration.

This script:
1. Loads batch_001.json and batch_002.json
2. Uses the exact prompt from run_20251015_060225
3. Runs batch evaluation for each separately via OpenAI Batch API
4. Produces separate output files per batch
5. Creates combined output files
"""
import json
import sys
from pathlib import Path
from datetime import datetime

from src.batch_evaluator import BatchEvaluator
from src.batch_result_processor import BatchResultProcessor


def load_batch_conversations(batch_path: Path):
    """Load conversations from a batch JSON file."""
    with open(batch_path, 'r') as f:
        conversations = json.load(f)
    return conversations


def format_conversations_for_evaluation(conversations_data):
    """
    Format conversations from batch format to evaluation format.
    
    Args:
        conversations_data: List of dicts with 'set_id' and 'conversations'
    
    Returns:
        List of dicts with 'conversation_id', 'set_id', and 'conversation_text'
    """
    formatted = []
    
    for item in conversations_data:
        set_id = item['set_id']
        # Use set_id as conversation_id for consistency
        conversation_id = set_id
        
        # Format conversation text from exchanges
        conversation_text = ""
        for conv in item.get('conversations', []):
            exchanges = conv.get('exchanges', [])
            for i, exchange in enumerate(exchanges):
                role = exchange.get('role', '')
                content = exchange.get('content', '')
                
                # Format as Q1/A1, Q2/A2, etc.
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
    """Main execution function."""
    print("=" * 80)
    print("BATCH EVALUATION: Batches 001 & 002")
    print("=" * 80)
    
    # Paths
    workspace = Path("/Users/rkouzy/Documents/LLM_Alignment")
    prompt_path = workspace / "results/run_20251015_060225/prompt_20251015_060225.txt"
    batch_001_path = workspace / "Model_Runs_Cleaned/batches/batch_001.json"
    batch_002_path = workspace / "Model_Runs_Cleaned/batches/batch_002.json"
    metadata_csv_path = workspace / "Model_Runs_Cleaned/metadata_mapping.csv"
    output_dir = workspace / "batch_results"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Load prompt (using exact 060225 configuration)
    print(f"\nLoading prompt from: {prompt_path}")
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    print(f"Prompt loaded ({len(prompt)} characters)")
    
    # Initialize processor
    processor = BatchResultProcessor(str(metadata_csv_path))
    print("Initialized batch result processor with metadata")
    
    # Store results for combining
    all_batch_results = []
    
    # Process each batch
    for batch_num, batch_path in [("001", batch_001_path), ("002", batch_002_path)]:
        print(f"\n{'=' * 80}")
        print(f"PROCESSING BATCH {batch_num}")
        print(f"{'=' * 80}")
        
        # Create batch-specific output directory
        batch_output_dir = output_dir / f"batch_{batch_num}_run"
        batch_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load batch data
        print(f"Loading batch from: {batch_path}")
        batch_data = load_batch_conversations(batch_path)
        print(f"Loaded {len(batch_data)} conversations from batch {batch_num}")
        
        # Format for evaluation
        formatted_conversations = format_conversations_for_evaluation(batch_data)
        print(f"Formatted {len(formatted_conversations)} conversations for evaluation")
        
        # Create evaluator
        evaluator = BatchEvaluator(prompt, batch_output_dir)
        
        print(f"\nStarting batch evaluation for batch {batch_num}...")
        print("This will:")
        print("  1. Create batch input file")
        print("  2. Submit to OpenAI Batch API")
        print("  3. Wait for completion")
        print("  4. Download and parse results")
        print("  5. Apply scoring")
        
        # Run evaluation manually with our formatted conversations
        try:
            # Step 1: Create batch file with our conversations
            batch_requests = evaluator.judge.prepare_batch_input(formatted_conversations)
            batch_file = evaluator.output_dir / "batch_input.jsonl"
            with open(batch_file, 'w') as f:
                for request in batch_requests:
                    f.write(json.dumps(request) + '\n')
            print(f"Created batch input file with {len(batch_requests)} requests")
            
            # Step 2: Submit batch
            batch_id = evaluator.submit_batch(batch_file)
            
            # Step 3: Wait for completion
            evaluator.wait_for_batch(batch_id)
            
            # Step 4: Download results
            results_file = evaluator.download_results(batch_id)
            
            # Step 5: Parse and score results
            scored_results = evaluator.parse_batch_results(results_file, formatted_conversations)
            print(f"\n✓ Batch {batch_num} evaluation completed: {len(scored_results)} results")
            
            # Process results
            print(f"\nProcessing results for batch {batch_num}...")
            raw_judgments = processor.process_raw_judgments(scored_results)
            metadata_list = processor.extract_metadata_from_conversations(batch_data)
            combined_data = processor.join_judgments_with_metadata(raw_judgments, metadata_list)
            
            # Save batch-specific outputs
            processor.save_outputs(
                raw_judgments,
                metadata_list,
                combined_data,
                output_dir,
                f"batch_{batch_num}"
            )
            
            # Store for combining
            all_batch_results.append({
                'batch_num': batch_num,
                'raw_judgments': raw_judgments,
                'metadata': metadata_list,
                'combined': combined_data
            })
            
            print(f"✓ Batch {batch_num} processing complete")
            
        except Exception as e:
            print(f"✗ Error processing batch {batch_num}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Combine all batches
    print(f"\n{'=' * 80}")
    print("COMBINING BATCHES")
    print(f"{'=' * 80}")
    
    if len(all_batch_results) == 2:
        processor.combine_batches(
            all_batch_results[0]['raw_judgments'],
            all_batch_results[1]['raw_judgments'],
            all_batch_results[0]['metadata'],
            all_batch_results[1]['metadata'],
            all_batch_results[0]['combined'],
            all_batch_results[1]['combined'],
            output_dir
        )
        print("✓ Combined outputs created")
    else:
        print("✗ Could not combine batches - not all batches completed")
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("EVALUATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nResults saved to: {output_dir}/")
    print("\nGenerated files:")
    print("  Per-batch files:")
    print("    - batch_001_raw_judgments.json")
    print("    - batch_001_metadata.json")
    print("    - batch_001_analysis_ready.json")
    print("    - batch_002_raw_judgments.json")
    print("    - batch_002_metadata.json")
    print("    - batch_002_analysis_ready.json")
    print("  Combined files:")
    print("    - combined_raw_judgments.json")
    print("    - combined_metadata.json")
    print("    - combined_analysis_ready.json")
    print("\nReady for downstream analysis!")


if __name__ == "__main__":
    main()

