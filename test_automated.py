"""
Test script for automated_proposition.py

Runs the pipeline with a sample proposition without requiring user input.
"""

import os
import sys
from automated_proposition import AutomatedPropositionPipeline

def main():
    """Test the automated pipeline"""

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("[ERROR] ANTHROPIC_API_KEY not found in environment")
        print("\nPlease set it in your .env file or as an environment variable")
        sys.exit(1)

    # Sample proposition and domain
    test_proposition = "Language models learn patterns from text data that reflect human cognitive biases, potentially amplifying these biases in unexpected ways."
    test_domain = "computer science"

    print(f"\n{'='*70}")
    print("TESTING AUTOMATED PROPOSITION PIPELINE")
    print(f"{'='*70}\n")
    print(f"Test Proposition: {test_proposition}")
    print(f"Test Domain: {test_domain}\n")

    try:
        # Create pipeline with shorter delay for testing
        pipeline = AutomatedPropositionPipeline(delay_between_calls=0.5)

        # Run pipeline
        pipeline.run_pipeline(test_proposition, test_domain)

        print(f"\n{'='*70}")
        print("[SUCCESS] Test completed successfully!")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
