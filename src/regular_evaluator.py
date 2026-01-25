"""
Regular (synchronous) evaluation.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from src.llm_judge import LLMJudge
from src.scorer import ConversationScorer


class RegularEvaluator:
    """Evaluator for synchronous processing."""
    
    def __init__(self, prompt_template: str, output_dir: Path):
        """
        Initialize regular evaluator.
        
        Args:
            prompt_template: Prompt template for evaluation
            output_dir: Directory to save outputs
        """
        self.judge = LLMJudge(prompt_template)
        self.scorer = ConversationScorer()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_evaluation(self) -> List[Dict[str, Any]]:
        """
        Run complete regular evaluation workflow.
        
        Returns:
            List of scored results
        """
        # Load conversations
        print("Loading conversations...")
        conversations = self.judge.load_conversations()
        print(f"Loaded {len(conversations)} conversations")
        
        # Evaluate each conversation
        print("\nEvaluating conversations...")
        results = []
        
        for conversation in tqdm(conversations, desc="Evaluating"):
            # Get LLM evaluation
            eval_result = self.judge.evaluate_conversation(conversation)
            
            if eval_result.get('llm_response'):
                # Score the conversation
                scores = self.scorer.score_conversation(
                    conversation['conversation_text'],
                    eval_result['llm_response']
                )
                
                # Combine results
                result = {
                    'conversation_id': conversation['conversation_id'],
                    **scores,
                    'usage': eval_result.get('usage', {})
                }
            else:
                # Error case
                result = {
                    'conversation_id': conversation['conversation_id'],
                    'error': eval_result.get('error', 'Unknown error')
                }
            
            results.append(result)
            
            # Save incrementally to avoid data loss
            self._save_intermediate_results(results)
        
        print(f"\nCompleted {len(results)} evaluations")
        return results
    
    def _save_intermediate_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Save intermediate results.
        
        Args:
            results: Current results list
        """
        intermediate_file = self.output_dir / "intermediate_results.json"
        with open(intermediate_file, 'w') as f:
            json.dump(results, f, indent=2)

