"""
Batch evaluation using OpenAI Batch API.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
from src.config import OPENAI_API_KEY, BATCH_COMPLETION_WINDOW
from src.llm_judge import LLMJudge
from src.scorer import ConversationScorer


class BatchEvaluator:
    """Evaluator for batch processing via OpenAI Batch API."""
    
    def __init__(self, prompt_template: str, output_dir: Path):
        """
        Initialize batch evaluator.
        
        Args:
            prompt_template: Prompt template for evaluation
            output_dir: Directory to save outputs
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.judge = LLMJudge(prompt_template)
        self.scorer = ConversationScorer()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_batch_file(self, conversations: List[Dict[str, Any]]) -> Path:
        """
        Create JSONL batch input file.
        
        Args:
            conversations: List of conversation dicts
        
        Returns:
            Path to created batch file
        """
        batch_requests = self.judge.prepare_batch_input(conversations)
        
        batch_file = self.output_dir / "batch_input.jsonl"
        
        with open(batch_file, 'w') as f:
            for request in batch_requests:
                f.write(json.dumps(request) + '\n')
        
        print(f"Created batch input file with {len(batch_requests)} requests")
        return batch_file
    
    def submit_batch(self, batch_file: Path) -> str:
        """
        Submit batch job to OpenAI.
        
        Args:
            batch_file: Path to batch input file
        
        Returns:
            Batch job ID
        """
        print("Uploading batch file...")
        
        with open(batch_file, 'rb') as f:
            file_response = self.client.files.create(
                file=f,
                purpose='batch'
            )
        
        print(f"File uploaded: {file_response.id}")
        print("Creating batch job...")
        
        batch_response = self.client.batches.create(
            input_file_id=file_response.id,
            endpoint="/v1/chat/completions",
            completion_window=BATCH_COMPLETION_WINDOW,
        )
        
        batch_id = batch_response.id
        print(f"Batch job created: {batch_id}")
        print(f"Status: {batch_response.status}")
        
        # Save batch info
        batch_info = {
            'batch_id': batch_id,
            'file_id': file_response.id,
            'status': batch_response.status,
            'created_at': batch_response.created_at,
        }
        
        with open(self.output_dir / "batch_info.json", 'w') as f:
            json.dump(batch_info, f, indent=2)
        
        return batch_id
    
    def check_batch_status(self, batch_id: str) -> str:
        """
        Check status of batch job.
        
        Args:
            batch_id: Batch job ID
        
        Returns:
            Status string
        """
        batch = self.client.batches.retrieve(batch_id)
        return batch.status
    
    def wait_for_batch(self, batch_id: str, check_interval: int = 60, max_wait_minutes: int = 60) -> None:
        """
        Wait for batch to complete.
        
        Args:
            batch_id: Batch job ID
            check_interval: Seconds between status checks
            max_wait_minutes: Maximum minutes to wait before timeout
        """
        print(f"Waiting for batch {batch_id} to complete...")
        print("This may take several minutes to hours depending on queue.")
        print(f"Will timeout after {max_wait_minutes} minutes.")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                batch = self.client.batches.retrieve(batch_id)
                raise Exception(
                    f"Batch timeout after {max_wait_minutes} minutes. "
                    f"Current status: {batch.status}. "
                    f"You can check batch {batch_id} status later and resume if needed."
                )
            
            batch = self.client.batches.retrieve(batch_id)
            status = batch.status
            
            elapsed_min = int(elapsed / 60)
            elapsed_sec = int(elapsed % 60)
            print(f"Status: {status} (elapsed: {elapsed_min}m {elapsed_sec}s)")
            
            if status == "completed":
                print("Batch completed successfully!")
                break
            elif status == "failed":
                print("Batch failed!")
                print(f"Error: {batch.errors}")
                raise Exception(f"Batch job failed: {batch.errors}")
            elif status in ["expired", "cancelled"]:
                raise Exception(f"Batch job {status}")
            
            # Wait before checking again
            time.sleep(check_interval)
    
    def download_results(self, batch_id: str) -> Path:
        """
        Download batch results.
        
        Args:
            batch_id: Batch job ID
        
        Returns:
            Path to downloaded results file
        """
        print("Downloading batch results...")
        
        batch = self.client.batches.retrieve(batch_id)
        
        # Check batch status first
        if batch.status != "completed":
            raise Exception(
                f"Cannot download results. Batch status: {batch.status}. "
                f"Expected 'completed'. Batch may still be processing or failed."
            )
        
        if batch.output_file_id is None:
            # Check for error file
            error_info = ""
            if hasattr(batch, 'error_file_id') and batch.error_file_id:
                print(f"⚠️  Batch has errors! Error file ID: {batch.error_file_id}")
                error_info = f" Error file available: {batch.error_file_id}"
                
                # Try to download error file for debugging
                try:
                    error_content = self.client.files.content(batch.error_file_id)
                    error_file = self.output_dir / "batch_error.jsonl"
                    with open(error_file, 'wb') as f:
                        f.write(error_content.content)
                    print(f"Error file downloaded to: {error_file}")
                    error_info += f"\nError details saved to: {error_file}"
                except Exception as e:
                    print(f"Could not download error file: {e}")
            
            raise Exception(
                f"No output file available. Batch status: {batch.status}.{error_info}"
            )
        
        # Download results
        result_content = self.client.files.content(batch.output_file_id)
        
        # Save to file
        results_file = self.output_dir / "batch_results.jsonl"
        with open(results_file, 'wb') as f:
            f.write(result_content.content)
        
        print(f"Results downloaded to: {results_file}")
        return results_file
    
    def parse_batch_results(self, results_file: Path, 
                          conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and score batch results.
        
        Args:
            results_file: Path to batch results JSONL
            conversations: Original conversations list
        
        Returns:
            List of scored results
        """
        print("Parsing and scoring batch results...")
        
        # Create conversation lookup
        conv_lookup = {conv['conversation_id']: conv for conv in conversations}
        
        # Parse results
        results = []
        with open(results_file, 'r') as f:
            for line in f:
                result = json.loads(line)
                
                # Extract conversation ID
                custom_id = result['custom_id']
                conv_id = custom_id.replace('eval-', '')
                
                # Get LLM response
                if result.get('response') and result['response'].get('body'):
                    llm_response = result['response']['body']['choices'][0]['message']['content']
                    
                    # Get original conversation
                    conversation = conv_lookup.get(conv_id)
                    if conversation:
                        # Score the conversation
                        scores = self.scorer.score_conversation(
                            conversation['conversation_text'],
                            llm_response
                        )
                        
                        # Combine results
                        results.append({
                            'conversation_id': conv_id,
                            **scores
                        })
                else:
                    print(f"Warning: No response for {conv_id}")
                    results.append({
                        'conversation_id': conv_id,
                        'error': 'No response from API'
                    })
        
        print(f"Parsed {len(results)} results")
        return results
    
    def run_batch_evaluation(self) -> List[Dict[str, Any]]:
        """
        Run complete batch evaluation workflow.
        
        Returns:
            List of scored results
        """
        # Load conversations
        print("Loading conversations...")
        conversations = self.judge.load_conversations()
        print(f"Loaded {len(conversations)} conversations")
        
        # Create batch file
        batch_file = self.create_batch_file(conversations)
        
        # Submit batch
        batch_id = self.submit_batch(batch_file)
        
        # Wait for completion
        self.wait_for_batch(batch_id)
        
        # Download results
        results_file = self.download_results(batch_id)
        
        # Parse and score results
        scored_results = self.parse_batch_results(results_file, conversations)
        
        return scored_results

