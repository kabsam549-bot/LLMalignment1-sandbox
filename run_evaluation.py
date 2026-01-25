#!/usr/bin/env python3
"""
Main entry point for LLM Judge evaluation system.
This is a thin wrapper around the consolidated CLI for backwards compatibility.

For new usage, prefer:
    python -m src.cli evaluate --mode batch --analyze
"""
import sys
from src.cli import main

if __name__ == "__main__":
    # If no arguments provided, default to evaluate command
    if len(sys.argv) == 1:
        sys.argv = ['run_evaluation.py', 'evaluate', '--mode', 'batch', '--analyze']
    elif sys.argv[1] not in ['evaluate', 'analyze', 'clean-model-runs', 'validate-cleaned']:
        # If first arg is not a command, assume old usage and insert 'evaluate'
        sys.argv.insert(1, 'evaluate')
    
    main()
