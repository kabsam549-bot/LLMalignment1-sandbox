#!/usr/bin/env python3
"""
Spot-check script to verify data cleaning quality.
Checks for false positives in truncation detection, thinking removal fidelity,
and proper granularity of conversation removal.
"""

import json
import re
import random
from pathlib import Path
from collections import defaultdict


class CleaningSpotCheck:
    """Performs quality spot-checks on cleaned data."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.model_runs_dir = self.base_dir / "Model_Runs"
        self.cleaned_dir = self.base_dir / "Model_Runs_Cleaned"
        
        self.findings = {
            'false_positives': [],
            'thinking_issues': [],
            'granularity_issues': [],
            'truncation_patterns': defaultdict(int),
            'samples_reviewed': 0
        }
    
    def run_full_spot_check(self):
        """Run all spot-check tasks."""
        print("="*80)
        print("DATA CLEANING SPOT-CHECK")
        print("="*80)
        print()
        
        # Task 1: Sample truncated conversations
        print("TASK 1: Sampling Truncated Conversations")
        print("-"*80)
        self.check_gemini_25_pro_truncations()
        self.check_claude_truncations()
        self.check_other_high_truncation_models()
        print()
        
        # Task 2: Verify thinking removal
        print("TASK 2: Verifying Thinking Removal Fidelity")
        print("-"*80)
        self.verify_thinking_removal('deepseek-ai_DeepSeek-R1-Distill-Qwen-32B', 5)
        self.verify_thinking_removal('gemini-2.0-flash-thinking-exp-01-21', 5)
        self.verify_thinking_removal('Qwen_Qwen3-32B', 5)
        print()
        
        # Task 3: Verify removal granularity
        print("TASK 3: Verifying Removal Granularity")
        print("-"*80)
        self.verify_granularity()
        print()
        
        # Task 4: Analyze truncation patterns
        print("TASK 4: Analyzing Truncation Patterns")
        print("-"*80)
        self.analyze_truncation_patterns(20)
        print()
        
        # Generate report
        self.generate_report()
    
    def check_gemini_25_pro_truncations(self):
        """Check Gemini 2.5 Pro truncations (52% - suspicious)."""
        print("Checking Gemini 2.5 Pro truncations (57 out of 120)...")
        
        # Load truncated log
        log_file = self.cleaned_dir / "truncated_conversations.log"
        gemini_truncated = self.parse_truncated_log('gemini-2.5-pro', log_file)
        
        # Sample 10 random ones
        sample_size = min(10, len(gemini_truncated))
        samples = random.sample(gemini_truncated, sample_size)
        
        # Load original data
        orig_file = self.model_runs_dir / "gemini-2.5-pro-results.json"
        with open(orig_file) as f:
            orig_data = json.load(f)
        
        false_positives = 0
        for sample in samples:
            set_id = sample['set_id']
            treatment_id = sample['treatment_id']
            format_type = sample['format']
            valence = sample['valence']
            reason = sample['reason']
            
            # Find in original
            response = self.get_response_from_original(
                orig_data, treatment_id, format_type, valence, reason
            )
            
            if response:
                is_actually_truncated = self.manual_check_truncation(response, reason)
                self.findings['samples_reviewed'] += 1
                
                print(f"  {set_id}: ", end='')
                if is_actually_truncated:
                    print(f"✓ Correctly flagged - {reason}")
                else:
                    print(f"❌ FALSE POSITIVE - {reason}")
                    print(f"     Response ({len(response)} chars): {response[:100]}...")
                    print(f"     Ends with: ...{response[-50:]}")
                    false_positives += 1
                    self.findings['false_positives'].append({
                        'set_id': set_id,
                        'model': 'gemini-2.5-pro',
                        'reason': reason,
                        'response_snippet': response[:200]
                    })
        
        print(f"  Summary: {false_positives}/{sample_size} false positives")
        print()
    
    def check_claude_truncations(self):
        """Check Claude 3.5 Haiku truncations (12 total)."""
        print("Checking Claude 3.5 Haiku truncations (12 out of 120)...")
        
        log_file = self.cleaned_dir / "truncated_conversations.log"
        claude_truncated = self.parse_truncated_log('claude-3-5-haiku', log_file)
        
        # Load original
        orig_file = self.model_runs_dir / "all_treatments_results_model_claude-3-5-haiku-20241022.json"
        with open(orig_file) as f:
            orig_data = json.load(f)
        
        false_positives = 0
        for sample in claude_truncated[:12]:  # Check all 12
            set_id = sample['set_id']
            treatment_id = sample['treatment_id']
            format_type = sample['format']
            valence = sample['valence']
            reason = sample['reason']
            
            response = self.get_response_from_original(
                orig_data, treatment_id, format_type, valence, reason
            )
            
            if response:
                is_actually_truncated = self.manual_check_truncation(response, reason)
                self.findings['samples_reviewed'] += 1
                
                print(f"  {set_id}: ", end='')
                if is_actually_truncated:
                    print(f"✓ Correctly flagged - {reason}")
                else:
                    print(f"❌ FALSE POSITIVE - {reason}")
                    print(f"     Response ends: ...{response[-80:]}")
                    false_positives += 1
                    self.findings['false_positives'].append({
                        'set_id': set_id,
                        'model': 'claude-3-5-haiku',
                        'reason': reason,
                        'response_snippet': response[:200]
                    })
        
        print(f"  Summary: {false_positives}/12 false positives")
        print()
    
    def check_other_high_truncation_models(self):
        """Check Qwen, DeepSeek, Gemini-thinking."""
        models_to_check = [
            ('Qwen_Qwen3-32B', 91, 5),
            ('deepseek-ai_DeepSeek-R1-Distill-Qwen-32B', 82, 5),
            ('gemini-2.0-flash-thinking-exp-01-21', 80, 5)
        ]
        
        log_file = self.cleaned_dir / "truncated_conversations.log"
        
        for model_name, total_truncated, sample_size in models_to_check:
            print(f"Sampling {model_name} ({total_truncated} truncated)...")
            
            truncated = self.parse_truncated_log(model_name, log_file)
            samples = random.sample(truncated, min(sample_size, len(truncated)))
            
            # Load original data
            orig_file = self.find_original_file(model_name)
            if not orig_file:
                print(f"  WARNING: Could not find original file for {model_name}")
                continue
            
            false_positives = 0
            for sample in samples:
                response = self.get_response_from_file(
                    orig_file, sample['treatment_id'], 
                    sample['format'], sample['valence'], sample['reason']
                )
                
                if response:
                    is_actually_truncated = self.manual_check_truncation(response, sample['reason'])
                    self.findings['samples_reviewed'] += 1
                    
                    if not is_actually_truncated:
                        false_positives += 1
                        self.findings['false_positives'].append({
                            'set_id': sample['set_id'],
                            'model': model_name,
                            'reason': sample['reason'],
                            'response_snippet': response[:200]
                        })
            
            print(f"  {false_positives}/{sample_size} false positives\n")
    
    def verify_thinking_removal(self, model_name: str, sample_size: int):
        """Verify thinking was removed but response preserved."""
        print(f"Checking {model_name}...")
        
        # Find conversations with thinking removed
        cleaned_file = self.find_cleaned_file(model_name)
        orig_file = self.find_original_file(model_name)
        
        if not cleaned_file or not orig_file:
            print(f"  WARNING: Could not find files for {model_name}")
            return
        
        # Load data
        cleaned_convs = self.load_conversations_with_thinking(cleaned_file, True)
        orig_convs = self.load_conversations_with_thinking(orig_file, False)
        
        issues = 0
        checked = 0
        
        for set_id, cleaned_resp in list(cleaned_convs.items())[:sample_size]:
            if set_id not in orig_convs:
                continue
            
            orig_resp = orig_convs[set_id]
            checked += 1
            
            # Check 1: No thinking tags in cleaned
            if '</think>' in cleaned_resp.lower() or '<think>' in cleaned_resp.lower():
                print(f"  ❌ {set_id}: Still has <think> tags!")
                issues += 1
                self.findings['thinking_issues'].append({
                    'set_id': set_id,
                    'model': model_name,
                    'issue': 'Tags not removed',
                    'snippet': cleaned_resp[:100]
                })
                continue
            
            # Check 2: Should not start with thinking language
            if cleaned_resp.startswith(('Okay', 'So I', 'Let me', 'I need to', 'Alright')):
                print(f"  ⚠️  {set_id}: Starts with thinking language")
                print(f"      First 80 chars: {cleaned_resp[:80]}...")
                issues += 1
                self.findings['thinking_issues'].append({
                    'set_id': set_id,
                    'model': model_name,
                    'issue': 'Thinking language remains',
                    'snippet': cleaned_resp[:100]
                })
                continue
            
            # Check 3: Should have substantial content
            if len(cleaned_resp) < 100:
                print(f"  ⚠️  {set_id}: Very short after thinking removal ({len(cleaned_resp)} chars)")
                issues += 1
                continue
            
            print(f"  ✓ {set_id}: Thinking properly removed")
        
        print(f"  Summary: {issues}/{checked} issues found\n")
    
    def verify_granularity(self):
        """Verify removal is per-conversation, not per-treatment."""
        print("Checking removal granularity (per-conversation vs per-treatment)...")
        
        # Find treatments with mixed retention
        mixed_treatments = self.find_mixed_retention_treatments()
        
        if not mixed_treatments:
            print("  No mixed retention treatments found - checking...")
            return
        
        # Check 5 examples
        for model, treatment_id, conditions_retained, conditions_removed in mixed_treatments[:5]:
            print(f"  {model} - Treatment {treatment_id}:")
            print(f"    Retained: {conditions_retained}")
            print(f"    Removed: {conditions_removed}")
            print(f"    ✓ Granular removal confirmed")
        
        print(f"  Summary: Verified {len(mixed_treatments[:5])} treatments with mixed retention")
        print()
    
    def analyze_truncation_patterns(self, sample_size: int):
        """Analyze what patterns triggered truncation flags."""
        print(f"Analyzing truncation patterns from {sample_size} samples...")
        
        log_file = self.cleaned_dir / "truncated_conversations.log"
        all_truncated = self.parse_all_truncated(log_file)
        
        samples = random.sample(all_truncated, min(sample_size, len(all_truncated)))
        
        pattern_counts = defaultdict(int)
        
        for sample in samples:
            # Get the actual response
            orig_file = self.find_original_file(sample['model'])
            if not orig_file:
                continue
            
            response = self.get_response_from_file(
                orig_file, sample['treatment_id'],
                sample['format'], sample['valence'], sample['reason']
            )
            
            if not response:
                continue
            
            # Determine which pattern triggered
            pattern = self.identify_truncation_pattern(response)
            pattern_counts[pattern] += 1
            self.findings['truncation_patterns'][pattern] += 1
            self.findings['samples_reviewed'] += 1
        
        print("  Truncation patterns found:")
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {pattern}: {count}")
        print()
    
    def generate_report(self):
        """Generate comprehensive spot-check report."""
        report_file = self.cleaned_dir / "SPOT_CHECK_REPORT.md"
        
        with open(report_file, 'w') as f:
            f.write("# Data Cleaning Spot-Check Report\n\n")
            f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n")
            f.write(f"**Samples Reviewed:** {self.findings['samples_reviewed']}\n\n")
            
            f.write("## 1. False Positive Analysis\n\n")
            f.write(f"**Total False Positives:** {len(self.findings['false_positives'])}\n\n")
            
            if self.findings['false_positives']:
                f.write("### Examples:\n\n")
                for fp in self.findings['false_positives'][:10]:
                    f.write(f"- **{fp['set_id']}** ({fp['model']})\n")
                    f.write(f"  - Reason: {fp['reason']}\n")
                    f.write(f"  - Snippet: {fp['response_snippet'][:150]}...\n\n")
            
            f.write("## 2. Thinking Removal Issues\n\n")
            f.write(f"**Total Issues:** {len(self.findings['thinking_issues'])}\n\n")
            
            if self.findings['thinking_issues']:
                for issue in self.findings['thinking_issues']:
                    f.write(f"- **{issue['set_id']}** ({issue['model']})\n")
                    f.write(f"  - Issue: {issue['issue']}\n")
                    f.write(f"  - Snippet: {issue['snippet']}...\n\n")
            
            f.write("## 3. Truncation Patterns\n\n")
            for pattern, count in sorted(self.findings['truncation_patterns'].items(), 
                                        key=lambda x: x[1], reverse=True):
                f.write(f"- **{pattern}**: {count} occurrences\n")
            
            f.write("\n## 4. Recommendations\n\n")
            
            if len(self.findings['false_positives']) > self.findings['samples_reviewed'] * 0.1:
                f.write("⚠️  **HIGH FALSE POSITIVE RATE** - Consider re-processing\n\n")
            
            if self.findings['thinking_issues']:
                f.write("⚠️  **Thinking removal has issues** - Review logic\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Samples reviewed: {self.findings['samples_reviewed']}\n")
            f.write(f"- False positives: {len(self.findings['false_positives'])}\n")
            f.write(f"- Thinking issues: {len(self.findings['thinking_issues'])}\n")
            f.write(f"- Granularity issues: {len(self.findings['granularity_issues'])}\n")
        
        print(f"Report generated: {report_file}")
    
    # Helper methods
    
    def parse_truncated_log(self, model_name: str, log_file: Path):
        """Parse truncated log for specific model."""
        truncated = []
        with open(log_file) as f:
            content = f.read()
        
        # Split by separator
        entries = content.split('--------------------------------------------------------------------------------')
        
        for entry in entries:
            if f'Model: {model_name}' not in entry:
                continue
            
            lines = entry.strip().split('\n')
            parsed = {}
            
            for line in lines:
                if 'Set ID:' in line:
                    parsed['set_id'] = line.split(': ', 1)[1].strip()
                elif 'Model:' in line:
                    parsed['model'] = line.split(': ', 1)[1].strip()
                elif 'Treatment:' in line:
                    parts = line.split(': ', 1)[1].split(' - ', 1)
                    parsed['treatment_id'] = int(parts[0])
                    if len(parts) > 1:
                        parsed['treatment_name'] = parts[1].strip()
                elif 'Format:' in line:
                    # Format: single_turn, Valence: positive
                    format_part = line.split('Format: ')[1].split(',')[0].strip()
                    valence_part = line.split('Valence: ')[1].strip()
                    parsed['format'] = format_part
                    parsed['valence'] = valence_part
                elif 'Reason:' in line:
                    parsed['reason'] = line.split(': ', 1)[1].strip()
            
            if 'set_id' in parsed and 'treatment_id' in parsed:
                truncated.append(parsed)
        
        return truncated
    
    def parse_all_truncated(self, log_file: Path):
        """Parse all truncated entries."""
        truncated = []
        with open(log_file) as f:
            content = f.read()
        
        entries = content.split('--------------------------------------------------------------------------------')
        for entry in entries:
            if 'Set ID:' not in entry:
                continue
            lines = entry.strip().split('\n')
            parsed = {}
            for line in lines:
                if 'Set ID:' in line:
                    parsed['set_id'] = line.split(': ', 1)[1].strip()
                elif 'Model:' in line:
                    parsed['model'] = line.split(': ', 1)[1].strip()
                elif 'Treatment:' in line:
                    parts = line.split(': ', 1)[1].split(' - ', 1)
                    parsed['treatment_id'] = int(parts[0])
                elif 'Format:' in line:
                    format_part = line.split('Format: ')[1].split(',')[0].strip()
                    valence_part = line.split('Valence: ')[1].strip()
                    parsed['format'] = format_part
                    parsed['valence'] = valence_part
                elif 'Reason:' in line:
                    parsed['reason'] = line.split(': ', 1)[1].strip()
            if 'set_id' in parsed and 'treatment_id' in parsed:
                truncated.append(parsed)
        
        return truncated
    
    def get_response_from_original(self, data, treatment_id, format_type, valence, reason):
        """Get response from original data."""
        # Parse reason to get question number
        q_num = int(reason.split('Q')[1][0]) - 1  # "Q3 response..." -> index 2
        
        for treatment in data:
            if treatment['treatment_id'] == treatment_id:
                for condition in treatment['conditions']:
                    if condition['format'] == format_type and condition['valence'] == valence:
                        if q_num < len(condition['interactions']):
                            return condition['interactions'][q_num]['response_text']
        return None
    
    def get_response_from_file(self, file_path, treatment_id, format_type, valence, reason):
        """Get response from file or directory."""
        file_path = Path(file_path)
        
        # Handle directory-based models
        if file_path.is_dir():
            # Find the specific treatment file
            treatment_file = file_path / f"{treatment_id}_results.json"
            if not treatment_file.exists():
                return None
            with open(treatment_file) as f:
                data = json.load(f)
            # Wrap in list if single dict
            if isinstance(data, dict):
                data = [data]
        else:
            # Single file model
            with open(file_path) as f:
                data = json.load(f)
            # Handle both list and single dict formats
            if isinstance(data, dict):
                data = [data]
        
        return self.get_response_from_original(data, treatment_id, format_type, valence, reason)
    
    def find_original_file(self, model_name: str):
        """Find original file for model."""
        # Check direct file
        candidates = [
            self.model_runs_dir / f"{model_name}-results.json",
            self.model_runs_dir / f"all_treatments_results_model_{model_name}.json",
            self.model_runs_dir / f"all_treatments_combined_results_model_{model_name}.json",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # Check directory
        dir_path = self.model_runs_dir / model_name
        if dir_path.exists() and dir_path.is_dir():
            return dir_path
        
        return None
    
    def find_cleaned_file(self, model_name: str):
        """Find cleaned file for model."""
        candidates = [
            self.cleaned_dir / f"{model_name}_results.json",
            self.cleaned_dir / model_name,
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None
    
    def load_conversations_with_thinking(self, file_path, is_cleaned):
        """Load conversations that had thinking removed."""
        conversations = {}
        
        if file_path.is_dir():
            # Load from directory
            for json_file in file_path.glob('*.json'):
                with open(json_file) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]
                    for treatment in data:
                        for condition in treatment.get('conditions', []):
                            set_id = condition.get('set_id', '')
                            if set_id and condition.get('interactions'):
                                conversations[set_id] = condition['interactions'][0]['response_text']
        else:
            # Load from file
            with open(file_path) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                for treatment in data:
                    for condition in treatment.get('conditions', []):
                        set_id = condition.get('set_id', '')
                        if set_id and condition.get('interactions'):
                            conversations[set_id] = condition['interactions'][0]['response_text']
        
        return conversations
    
    def find_mixed_retention_treatments(self):
        """Find treatments with some conditions kept, some removed."""
        mixed = []
        
        # Scan cleaned files
        for file_path in self.cleaned_dir.glob('*_results.json'):
            with open(file_path) as f:
                data = json.load(f)
            
            model_name = file_path.stem.replace('_results', '')
            
            for treatment in data:
                treatment_id = treatment['treatment_id']
                conditions = treatment.get('conditions', [])
                
                # Should have 0-4 conditions (4 = all kept, 0 = all removed)
                if 0 < len(conditions) < 4:
                    retained = [f"{c['format']}_{c['valence']}" for c in conditions]
                    all_combos = ['single_turn_positive', 'single_turn_negative',
                                 'multi_turn_positive', 'multi_turn_negative']
                    removed = [c for c in all_combos if c not in retained]
                    mixed.append((model_name, treatment_id, retained, removed))
        
        return mixed
    
    def manual_check_truncation(self, response: str, reason: str):
        """Manually verify if response is actually truncated."""
        response = response.strip()
        
        # Check actual truncation signs
        if response.endswith((',', ':', ';')):
            return True
        
        if re.search(r'\s+(and|or|but)\s*$', response):
            return True
        
        # Check if ends mid-sentence
        last_period = response.rfind('.')
        last_question = response.rfind('?')
        last_exclaim = response.rfind('!')
        last_punct = max(last_period, last_question, last_exclaim)
        
        if last_punct > 0:
            after_punct = response[last_punct+1:].strip()
            if len(after_punct) > 100 and not response.endswith((')', ']', '"', "'")):
                return True
        
        return False
    
    def identify_truncation_pattern(self, response: str):
        """Identify which pattern triggered truncation."""
        response = response.strip()
        
        if response.endswith(','):
            return "Ends with comma"
        if response.endswith(':'):
            return "Ends with colon"
        if response.endswith(';'):
            return "Ends with semicolon"
        if re.search(r'\s+and\s*$', response):
            return "Ends with 'and'"
        if re.search(r'\s+or\s*$', response):
            return "Ends with 'or'"
        if re.search(r'\s+but\s*$', response):
            return "Ends with 'but'"
        
        last_period = response.rfind('.')
        if last_period > 0 and len(response[last_period+1:].strip()) > 100:
            return "Long text after last punctuation"
        
        if '```' in response and response.count('```') % 2 != 0:
            return "Unclosed code block"
        
        if re.search(r'(^|\n)\s*[-*]\s*$', response):
            return "Empty list item"
        
        return "Other/Unknown"


def main():
    """Run spot-check."""
    base_dir = Path(__file__).parent.parent
    random.seed(42)  # For reproducibility
    
    checker = CleaningSpotCheck(str(base_dir))
    checker.run_full_spot_check()
    
    print("\n" + "="*80)
    print("SPOT-CHECK COMPLETE")
    print("="*80)
    print(f"Samples reviewed: {checker.findings['samples_reviewed']}")
    print(f"False positives found: {len(checker.findings['false_positives'])}")
    print(f"Thinking removal issues: {len(checker.findings['thinking_issues'])}")
    print(f"Report: Model_Runs_Cleaned/SPOT_CHECK_REPORT.md")


if __name__ == "__main__":
    main()

