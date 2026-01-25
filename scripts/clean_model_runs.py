#!/usr/bin/env python3
"""
Data Cleaning Pipeline for Model Runs
Cleans and normalizes all Model_Runs data, removing thinking tokens and truncated responses,
generating IDs, creating both output formats, and batching for evaluation.
"""

import json
import os
import re
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import random


class ModelRunsCleaner:
    """Main class for cleaning and normalizing model run data."""
    
    def __init__(self, model_runs_dir: str, output_dir: str):
        self.model_runs_dir = Path(model_runs_dir)
        self.output_dir = Path(output_dir)
        self.conversations_dir = self.output_dir / "conversations_format"
        self.batches_dir = self.output_dir / "batches"
        
        # Statistics
        self.stats = {
            'total_conversations': 0,
            'truncated_conversations': 0,
            'thinking_removed': 0,
            'by_model': defaultdict(lambda: {
                'total': 0,
                'truncated': 0,
                'thinking_removed': 0
            })
        }
        
        # Store all conversations and metadata
        self.all_conversations = []
        self.metadata_records = []
        self.truncated_log = []
    
    def clean_all(self):
        """Main entry point to clean all data."""
        print("Starting data cleaning pipeline...")
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.conversations_dir.mkdir(exist_ok=True)
        self.batches_dir.mkdir(exist_ok=True)
        
        # Process all models
        self.process_all_models()
        
        # Generate metadata CSV
        self.generate_metadata_csv()
        
        # Create batches
        self.create_batches()
        
        # Generate summary statistics
        self.generate_summary()
        
        # Save truncated log
        self.save_truncated_log()
        
        print("\n" + "="*80)
        print("Data cleaning pipeline completed!")
        print(f"Total conversations processed: {self.stats['total_conversations']}")
        print(f"Truncated conversations removed: {self.stats['truncated_conversations']}")
        print(f"Conversations with thinking removed: {self.stats['thinking_removed']}")
        print(f"Final conversation count: {len(self.all_conversations)}")
        print("="*80)
    
    def process_all_models(self):
        """Process all models in Model_Runs directory."""
        items = sorted(self.model_runs_dir.iterdir())
        
        for item in items:
            if item.name.startswith('.'):
                continue
            
            if item.is_file() and item.suffix == '.json':
                # Single-file model
                model_name = self.extract_model_name(item.name)
                print(f"\nProcessing model: {model_name} (single file)")
                self.process_single_file_model(item, model_name)
            
            elif item.is_dir():
                # Directory-based model
                model_name = item.name
                print(f"\nProcessing model: {model_name} (directory)")
                self.process_directory_model(item, model_name)
    
    def extract_model_name(self, filename: str) -> str:
        """Extract model name from filename."""
        # Remove various suffixes
        name = filename.replace('-results.json', '')
        name = name.replace('_results.json', '')
        name = name.replace('all_treatments_combined_results_model_', '')
        name = name.replace('all_treatments_results_model_', '')
        return name
    
    def process_single_file_model(self, file_path: Path, model_name: str):
        """Process a single-file model."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process the data
        cleaned_data = self.process_treatments(data, model_name, str(file_path))
        
        # Save in treatment-based format
        output_file = self.output_dir / f"{model_name}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved: {output_file}")
    
    def process_directory_model(self, dir_path: Path, model_name: str):
        """Process a directory-based model with numbered files."""
        # Create output directory
        output_model_dir = self.output_dir / model_name
        output_model_dir.mkdir(exist_ok=True)
        
        # Process each treatment file
        json_files = sorted([f for f in dir_path.iterdir() if f.suffix == '.json'])
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                treatment_data = json.load(f)
            
            # Process single treatment (wrapped in list for consistency)
            cleaned_data = self.process_treatments([treatment_data], model_name, str(json_file))
            
            # Save individual treatment file
            output_file = output_model_dir / json_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data[0] if cleaned_data else {}, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved {len(json_files)} treatment files to: {output_model_dir}")
    
    def process_treatments(self, treatments: List[Dict], model_name: str, file_path: str) -> List[Dict]:
        """Process all treatments and their conditions."""
        cleaned_treatments = []
        
        for treatment in treatments:
            treatment_id = treatment.get('treatment_id')
            treatment_name = treatment.get('treatment_name')
            treatment_type = treatment.get('treatment_type')
            
            cleaned_conditions = []
            
            for condition in treatment.get('conditions', []):
                format_type = condition.get('format')
                valence = condition.get('valence')
                interactions = condition.get('interactions', [])
                
                # Check if this is a valid conversation (should have 5 interactions)
                if len(interactions) != 5:
                    print(f"  WARNING: Expected 5 interactions, got {len(interactions)} for {model_name} treatment {treatment_id} {format_type} {valence}")
                    continue
                
                # Check for truncation across all 5 responses
                is_truncated, truncation_reason = self.check_truncation(interactions)
                
                if is_truncated:
                    # Log and skip this conversation
                    set_id = self.generate_set_id(model_name, treatment_id, format_type, valence)
                    self.log_truncated_conversation(set_id, model_name, treatment_id, 
                                                   treatment_name, format_type, valence, 
                                                   truncation_reason, file_path)
                    self.stats['truncated_conversations'] += 1
                    self.stats['by_model'][model_name]['truncated'] += 1
                    continue
                
                # Clean thinking tokens from all responses
                has_thinking = False
                cleaned_interactions = []
                
                for interaction in interactions:
                    cleaned_response, had_thinking = self.remove_thinking_tokens(
                        interaction.get('response_text', ''), 
                        model_name
                    )
                    has_thinking = has_thinking or had_thinking
                    
                    cleaned_interaction = {
                        'query_id': interaction.get('query_id'),
                        'query_text': interaction.get('query_text'),
                        'response_text': cleaned_response
                    }
                    cleaned_interactions.append(cleaned_interaction)
                
                if has_thinking:
                    self.stats['thinking_removed'] += 1
                    self.stats['by_model'][model_name]['thinking_removed'] += 1
                
                # Generate set_id for this conversation
                set_id = self.generate_set_id(model_name, treatment_id, format_type, valence)
                
                # Create cleaned condition
                cleaned_condition = {
                    'set_id': set_id,
                    'format': format_type,
                    'valence': valence,
                    'interactions': cleaned_interactions
                }
                cleaned_conditions.append(cleaned_condition)
                
                # Create conversation format for batching
                conversation = self.create_conversation_format(
                    set_id, cleaned_interactions, format_type
                )
                self.all_conversations.append(conversation)
                
                # Create metadata record
                self.metadata_records.append({
                    'set_id': set_id,
                    'model_name': model_name,
                    'treatment_id': treatment_id,
                    'treatment_name': treatment_name,
                    'treatment_type': treatment_type,
                    'format': format_type,
                    'valence': valence,
                    'has_thinking': has_thinking,
                    'is_truncated': False,
                    'original_file_path': file_path
                })
                
                # Update stats
                self.stats['total_conversations'] += 1
                self.stats['by_model'][model_name]['total'] += 1
            
            # Only add treatment if it has valid conditions
            if cleaned_conditions:
                cleaned_treatment = {
                    'treatment_id': treatment_id,
                    'treatment_name': treatment_name,
                    'treatment_type': treatment_type,
                    'conditions': cleaned_conditions
                }
                cleaned_treatments.append(cleaned_treatment)
        
        return cleaned_treatments
    
    def check_truncation(self, interactions: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Check if any of the 5 responses in a conversation is truncated.
        Returns (is_truncated, reason).
        """
        for i, interaction in enumerate(interactions):
            response = interaction.get('response_text', '')
            
            # Check various truncation indicators
            if self.is_truncated_response(response):
                reason = f"Q{i+1} response appears truncated"
                return True, reason
        
        return False, None
    
    def is_truncated_response(self, response: str) -> bool:
        """
        Check if a single response appears truncated (cut off mid-generation).
        NOTE: Length doesn't matter - only whether it was cut off mid-stream.
        """
        if not response or len(response.strip()) == 0:
            return True
        
        response = response.strip()
        
        # ONLY check for actual truncation indicators (mid-generation cutoffs)
        # Do NOT use character count as a criterion!
        
        # 1. Ends with clear continuation indicators (mid-sentence)
        continuation_patterns = [
            r'\s+and\s*$',  # ends with " and "
            r'\s+or\s*$',   # ends with " or "
            r'\s+but\s*$',  # ends with " but "
            r',$',          # ends with comma
            r':\s*$',       # ends with colon (not followed by anything)
            r';\s*$',       # ends with semicolon
        ]
        
        for pattern in continuation_patterns:
            if re.search(pattern, response):
                return True
        
        # 2. Ends with literal "..." suggesting cutoff
        # But allow "..." if it's clearly intentional (like trailing off in dialogue)
        if re.search(r'\.\.\.\s*$', response):
            # Check if there's content before it - if very short after last sentence, likely truncated
            last_sentence = response.split('.')[-2:]
            if len(last_sentence) > 0 and len(last_sentence[-1].strip()) < 5:
                return True
        
        # 3. Ends mid-sentence with substantial text after last proper punctuation
        last_period_pos = response.rfind('.')
        last_question_pos = response.rfind('?')
        last_exclaim_pos = response.rfind('!')
        last_punct_pos = max(last_period_pos, last_question_pos, last_exclaim_pos)
        
        if last_punct_pos > 0:
            text_after_punct = response[last_punct_pos + 1:].strip()
            # If there's substantial text after punctuation without any closing, might be truncated
            if len(text_after_punct) > 100:  # More than 100 chars without proper ending
                # Check if it ends abruptly (not with a closing structure)
                if not response.endswith((')', ']', '"', "'", '\n', '.')):
                    return True
        
        # 4. Unclosed code blocks
        if '```' in response:
            count = response.count('```')
            if count % 2 != 0:  # Odd number means unclosed
                return True
        
        # 5. Response ends with an incomplete numbered/bulleted list item (empty)
        if re.search(r'(^|\n)\s*[-*]\s*$', response):
            return True
        if re.search(r'(^|\n)\s*\d+\.\s*$', response):
            return True
        
        # 6. Ends with incomplete word (no space before end, suggesting mid-word cutoff)
        # Only if it doesn't end with punctuation
        if not re.search(r'[.!?,;:\)\]\"\'\n]\s*$', response):
            # Check if last "word" looks incomplete (common prefixes with no completion)
            words = response.split()
            if words:
                last_word = words[-1]
                # If ends with a word that's typically a prefix/article, might be truncated
                if re.match(r'^(the|a|an|to|for|with|in|on|at|by|from)$', last_word, re.IGNORECASE):
                    return True
        
        return False
    
    def remove_thinking_tokens(self, response: str, model_name: str) -> Tuple[str, bool]:
        """
        Remove thinking tokens from response.
        Returns (cleaned_response, had_thinking).
        """
        original_length = len(response)
        cleaned = response
        had_thinking = False
        
        # DeepSeek: Remove thinking content before </think>
        # DeepSeek R1 outputs thinking without opening <think> tag, just closes with </think>
        if 'deepseek' in model_name.lower() or 'r1' in model_name.lower():
            # Check for </think> tag (may or may not have opening tag)
            if '</think>' in cleaned.lower():
                # Find the </think> tag and keep only what comes after
                match = re.search(r'</think>\s*(.+)$', cleaned, flags=re.DOTALL | re.IGNORECASE)
                if match:
                    cleaned = match.group(1).strip()
                    had_thinking = True
            # Also handle full <think>...</think> blocks if present
            elif '<think>' in cleaned.lower():
                pattern = r'<think>.*?</think>\s*'
                if re.search(pattern, cleaned, flags=re.DOTALL | re.IGNORECASE):
                    cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
                    had_thinking = True
        
        # Gemini thinking models: Look for thinking preambles
        if 'thinking' in model_name.lower():
            # Gemini thinking models have "Okay, so..." style reasoning before answers
            # Look for the </think> tag if present
            think_match = re.search(r'</think>\s*(.+)$', cleaned, flags=re.DOTALL | re.IGNORECASE)
            if think_match:
                cleaned = think_match.group(1).strip()
                had_thinking = True
            # If starts with thinking language and has a clear break to actual content
            elif cleaned.startswith(('Okay', 'Alright', 'Let me', 'I need to', 'So I', "I'm trying")):
                # Try to find where actual answer starts (after reasoning section)
                # Look for clear transitions or where substantive content begins
                lines = cleaned.split('\n')
                # Find first line that looks like actual answer content (not meta-reasoning)
                for i, line in enumerate(lines):
                    # Skip thinking lines, find substantive start
                    if len(line.strip()) > 50 and not line.startswith(('Okay', 'So ', 'I ', 'First', 'Let me', 'Now ')):
                        # Found potential start of real content
                        cleaned = '\n'.join(lines[i:])
                        had_thinking = True
                        break
        
        # Remove any orphaned think tags
        if '<think>' in cleaned.lower() or '</think>' in cleaned.lower():
            cleaned = re.sub(r'</?think>\s*', '', cleaned, flags=re.IGNORECASE)
            had_thinking = True
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        # Double-check if we actually removed significant content
        if not had_thinking:
            had_thinking = len(cleaned) < original_length * 0.9  # If removed >10% of content
        
        return cleaned, had_thinking
    
    def generate_set_id(self, model_name: str, treatment_id: int, 
                       format_type: str, valence: str) -> str:
        """Generate unique set_id for a conversation."""
        # Format: {model}_{treatment_id}_{format_code}{valence_code}
        # e.g., "4o_1_SP" for 4o, treatment 1, single_turn positive
        format_code = 'S' if format_type == 'single_turn' else 'M'
        valence_code = 'P' if valence == 'positive' else 'N'
        
        return f"{model_name}_{treatment_id}_{format_code}{valence_code}"
    
    def create_conversation_format(self, set_id: str, interactions: List[Dict], 
                                   format_type: str) -> Dict:
        """
        Create conversation in the format matching data/conversations.json.
        For both single_turn and multi_turn, create alternating user/assistant exchanges.
        """
        exchanges = []
        
        for interaction in interactions:
            # Add user message
            exchanges.append({
                'role': 'user',
                'content': interaction['query_text']
            })
            # Add assistant response
            exchanges.append({
                'role': 'assistant',
                'content': interaction['response_text']
            })
        
        return {
            'set_id': set_id,
            'conversations': [
                {
                    'exchanges': exchanges
                }
            ]
        }
    
    def log_truncated_conversation(self, set_id: str, model_name: str, treatment_id: int,
                                  treatment_name: str, format_type: str, valence: str,
                                  reason: str, file_path: str):
        """Log a truncated conversation for reference."""
        self.truncated_log.append({
            'set_id': set_id,
            'model_name': model_name,
            'treatment_id': treatment_id,
            'treatment_name': treatment_name,
            'format': format_type,
            'valence': valence,
            'reason': reason,
            'file_path': file_path
        })
        
        # Also add to metadata with truncated flag
        self.metadata_records.append({
            'set_id': set_id,
            'model_name': model_name,
            'treatment_id': treatment_id,
            'treatment_name': treatment_name,
            'treatment_type': '',  # Unknown for truncated
            'format': format_type,
            'valence': valence,
            'has_thinking': False,
            'is_truncated': True,
            'original_file_path': file_path
        })
    
    def generate_metadata_csv(self):
        """Generate metadata mapping CSV."""
        csv_path = self.output_dir / 'metadata_mapping.csv'
        
        fieldnames = [
            'set_id', 'model_name', 'treatment_id', 'treatment_name', 
            'treatment_type', 'format', 'valence', 'has_thinking', 
            'is_truncated', 'original_file_path'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.metadata_records)
        
        print(f"\nGenerated metadata CSV: {csv_path}")
        print(f"  Total records: {len(self.metadata_records)}")
    
    def create_batches(self):
        """Create batched conversation files with stratification."""
        if not self.all_conversations:
            print("No conversations to batch!")
            return
        
        # Shuffle conversations for diversity (but set seed for reproducibility)
        random.seed(42)
        shuffled = self.all_conversations.copy()
        random.shuffle(shuffled)
        
        # Create batches of 100
        batch_size = 100
        batches = []
        
        for i in range(0, len(shuffled), batch_size):
            batch = shuffled[i:i+batch_size]
            batches.append(batch)
        
        # Save each batch
        batch_manifest = []
        
        for i, batch in enumerate(batches, 1):
            batch_file = self.batches_dir / f"batch_{i:03d}.json"
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch, f, indent=2, ensure_ascii=False)
            
            # Record in manifest
            batch_info = {
                'batch_number': i,
                'batch_file': f"batch_{i:03d}.json",
                'conversation_count': len(batch),
                'set_ids': [conv['set_id'] for conv in batch]
            }
            batch_manifest.append(batch_info)
            
            print(f"Created batch {i:03d}: {len(batch)} conversations")
        
        # Save manifest
        manifest_path = self.batches_dir / 'batch_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_batches': len(batches),
                'total_conversations': len(self.all_conversations),
                'batch_size': batch_size,
                'batches': batch_manifest
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nGenerated {len(batches)} batch files")
        print(f"Batch manifest saved: {manifest_path}")
    
    def generate_summary(self):
        """Generate summary statistics."""
        summary = {
            'total_conversations_before': 1560,  # 13 models × 120 conversations
            'total_conversations_after': len(self.all_conversations),
            'truncated_conversations_removed': self.stats['truncated_conversations'],
            'conversations_with_thinking_removed': self.stats['thinking_removed'],
            'by_model': {}
        }
        
        # Add per-model stats
        for model_name, model_stats in self.stats['by_model'].items():
            summary['by_model'][model_name] = {
                'total_conversations': model_stats['total'],
                'truncated_removed': model_stats['truncated'],
                'thinking_removed': model_stats['thinking_removed']
            }
        
        # Breakdown by format, valence, treatment_type
        breakdown = {
            'by_format': defaultdict(int),
            'by_valence': defaultdict(int),
            'by_treatment_type': defaultdict(int)
        }
        
        for record in self.metadata_records:
            if not record['is_truncated']:
                breakdown['by_format'][record['format']] += 1
                breakdown['by_valence'][record['valence']] += 1
                breakdown['by_treatment_type'][record['treatment_type']] += 1
        
        summary['breakdown'] = {
            'by_format': dict(breakdown['by_format']),
            'by_valence': dict(breakdown['by_valence']),
            'by_treatment_type': dict(breakdown['by_treatment_type'])
        }
        
        # Batch statistics
        summary['batches'] = {
            'total_batches': len(list(self.batches_dir.glob('batch_*.json'))),
            'conversations_per_batch': 100
        }
        
        # Save summary
        summary_path = self.output_dir / 'data_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nGenerated summary: {summary_path}")
    
    def save_truncated_log(self):
        """Save log of truncated conversations."""
        log_path = self.output_dir / 'truncated_conversations.log'
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Truncated Conversations Log\n")
            f.write(f"Total truncated: {len(self.truncated_log)}\n")
            f.write("="*80 + "\n\n")
            
            for entry in self.truncated_log:
                f.write(f"Set ID: {entry['set_id']}\n")
                f.write(f"Model: {entry['model_name']}\n")
                f.write(f"Treatment: {entry['treatment_id']} - {entry['treatment_name']}\n")
                f.write(f"Format: {entry['format']}, Valence: {entry['valence']}\n")
                f.write(f"Reason: {entry['reason']}\n")
                f.write(f"File: {entry['file_path']}\n")
                f.write("-"*80 + "\n\n")
        
        print(f"Truncated log saved: {log_path}")


def main():
    """Main entry point."""
    # Set up paths
    base_dir = Path(__file__).parent.parent
    model_runs_dir = base_dir / "Model_Runs"
    output_dir = base_dir / "Model_Runs_Cleaned"
    
    # Create cleaner and run
    cleaner = ModelRunsCleaner(str(model_runs_dir), str(output_dir))
    cleaner.clean_all()
    
    print("\n✓ Data cleaning pipeline completed successfully!")


if __name__ == "__main__":
    main()

