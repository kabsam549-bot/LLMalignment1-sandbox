#!/usr/bin/env python3
"""
Consolidated CLI for LLM Alignment evaluation and analysis.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

from src.analysis import AgreementAnalyzer
from src.batch_evaluator import BatchEvaluator
from src.regular_evaluator import RegularEvaluator
from src.config import PROMPT_FILE, RESULTS_DIR


def cmd_analyze(args):
    """Run agreement analysis on predictions."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load predictions JSON (expects a list of dicts)
    with open(args.predictions) as f:
        predictions = json.load(f)

    analyzer = AgreementAnalyzer(predictions, output_dir)
    analyzer.run_analysis(args.timestamp)


def cmd_evaluate(args):
    """Run LLM evaluation (batch or regular mode)."""
    timestamp = args.timestamp or datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = RESULTS_DIR / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load prompt
    if not PROMPT_FILE.exists():
        print(f"Error: Prompt file not found: {PROMPT_FILE}")
        sys.exit(1)
    
    with open(PROMPT_FILE, 'r') as f:
        prompt = f.read()
    
    # Save prompt copy
    shutil.copy(PROMPT_FILE, output_dir / f"prompt_{timestamp}.txt")
    
    # Save config
    config = {
        'timestamp': timestamp,
        'mode': args.mode,
        'model': 'gpt-5-mini',
        'prompt_file': str(PROMPT_FILE),
    }
    with open(output_dir / f"run_config_{timestamp}.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    # Run evaluation
    if args.mode == 'batch':
        evaluator = BatchEvaluator(prompt, output_dir)
        predictions = evaluator.run_batch_evaluation()
    else:
        evaluator = RegularEvaluator(prompt, output_dir)
        predictions = evaluator.run_evaluation()
    
    if predictions:
        # Save predictions
        with open(output_dir / f"llm_predictions_{timestamp}.json", 'w') as f:
            json.dump(predictions, f, indent=2)
        
        df = pd.DataFrame(predictions)
        df.to_csv(output_dir / f"llm_predictions_{timestamp}.csv", index=False)
        
        # Run analysis
        if args.analyze:
            print("\nRunning agreement analysis...")
            analyzer = AgreementAnalyzer(predictions, output_dir)
            analyzer.run_analysis(timestamp)
    
    print(f"\nResults saved to: {output_dir}")


def cmd_clean_model_runs(args):
    """Clean and normalize model runs data."""
    from scripts.clean_model_runs import ModelRunsCleaner
    
    cleaner = ModelRunsCleaner(args.input_dir, args.output_dir)
    cleaner.clean_all()
    print("\n✓ Model runs cleaning completed!")


def cmd_validate_cleaned(args):
    """Validate cleaned model runs data."""
    from scripts.validate_cleaned_data import validate_cleaned_data
    
    results = validate_cleaned_data()
    if results['unique_set_ids'] and results['issues_count'] == 0:
        print("\n✓ All validation checks passed!")
    else:
        print("\n⚠ Some validation issues detected. Review above.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="LLM Alignment CLI - Evaluation, Analysis, and Data Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run batch evaluation with analysis
  python -m src.cli evaluate --mode batch --analyze
  
  # Run agreement analysis on existing predictions
  python -m src.cli analyze --predictions results/run_*/llm_predictions_*.json \\
                           --output-dir results/run_* --timestamp 20251015_060225
  
  # Clean model runs
  python -m src.cli clean-model-runs --input-dir Model_Runs --output-dir Model_Runs_Cleaned
  
  # Validate cleaned data
  python -m src.cli validate-cleaned
        """
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    p_analyze = sub.add_parser("analyze", help="Run agreement analysis on predictions")
    p_analyze.add_argument("--predictions", required=True, help="Path to predictions JSON list")
    p_analyze.add_argument("--output-dir", required=True, help="Directory for results")
    p_analyze.add_argument("--timestamp", required=True, help="Timestamp label for outputs")
    p_analyze.set_defaults(func=cmd_analyze)

    # Evaluate command
    p_evaluate = sub.add_parser("evaluate", help="Run LLM evaluation")
    p_evaluate.add_argument("--mode", choices=['batch', 'regular'], default='batch',
                           help="Evaluation mode (batch or regular)")
    p_evaluate.add_argument("--timestamp", help="Optional timestamp (default: now)")
    p_evaluate.add_argument("--analyze", action='store_true',
                           help="Run agreement analysis after evaluation")
    p_evaluate.set_defaults(func=cmd_evaluate)

    # Clean model runs command
    p_clean = sub.add_parser("clean-model-runs", help="Clean and normalize model runs")
    p_clean.add_argument("--input-dir", default="Model_Runs", help="Input directory")
    p_clean.add_argument("--output-dir", default="Model_Runs_Cleaned", help="Output directory")
    p_clean.set_defaults(func=cmd_clean_model_runs)

    # Validate cleaned data
    p_validate = sub.add_parser("validate-cleaned", help="Validate cleaned model runs")
    p_validate.set_defaults(func=cmd_validate_cleaned)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


