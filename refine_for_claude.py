"""
Proposition Refinement Script (Claude Code Integration)

This script:
1. Takes a user proposition
2. Refines it through 5 iterative stages
3. Saves the refined version to a work file
4. Instructs the user to use Claude Code for evaluation and summary

Usage:
    python refine_for_claude.py
"""

import os
import sys
import json
import time
import secrets
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from anthropic import Anthropic, RateLimitError, APIError

# Load environment variables
load_dotenv()


def retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Retry a function with exponential backoff for rate limit handling"""
    def wrapper(*args, **kwargs):
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    print(f"[ERROR] Rate limit exceeded after {max_retries} attempts")
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"[WARN] Rate limit hit. Waiting {actual_delay:.1f}s before retry {attempt + 1}/{max_retries}")
                time.sleep(actual_delay)
                delay *= exponential_base

            except APIError as e:
                if attempt == max_retries - 1:
                    print(f"[ERROR] API error after {max_retries} attempts: {str(e)}")
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"[WARN] API error: {str(e)}. Retrying in {actual_delay:.1f}s")
                time.sleep(actual_delay)
                delay *= exponential_base

        return func(*args, **kwargs)

    return wrapper


class RefinementPipeline:
    """Handles proposition refinement only"""

    def __init__(self, delay_between_calls: float = 1.5):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.delay = delay_between_calls
        self.refinement_stages = 5

        # Ensure directories exist
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("work", exist_ok=True)

    def print_stage_header(self, stage: str):
        """Print a formatted stage header"""
        print(f"\n{'='*70}")
        print(f"{stage}")
        print(f"{'='*70}\n")

    def refine_proposition(self, proposition: str, domain: str, stage_num: int) -> str:
        """Refine a proposition using Claude"""
        prompt = f"""You are an expert in {domain}.

A colleague has shared the following proposition with you:

"{proposition}"

Please help improve this proposition by:
1. Making the core idea more clear and precise
2. Highlighting the key insights or implications
3. Removing any sentences that don't contribute value
4. Ensuring proper logical flow
5. Adding your own insights (the colleague is a good friend and welcomes your input)

IMPORTANT OUTPUT FORMAT INSTRUCTIONS:
- Output ONLY the improved proposition itself
- Do NOT include any meta-commentary, explanations, or analysis
- Do NOT use phrases like "Here is the improved version" or "The refined proposition is"
- Do NOT add introductory or concluding remarks
- Do NOT explain what you changed or why
- Output should be the proposition text ONLY, as if you wrote it yourself

Begin your response with the improved proposition directly."""

        time.sleep(self.delay)

        @retry_with_exponential_backoff
        def make_api_call():
            return self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

        response = make_api_call()
        refined_text = response.content[0].text.strip()

        print(f"[Stage {stage_num}] ✓ Refined ({len(refined_text)} chars)")

        return refined_text

    def run_refinement(self, proposition: str, domain: str) -> Dict:
        """Run refinement stages and save to work file"""
        self.print_stage_header("PROPOSITION REFINEMENT PIPELINE")

        print(f"Domain: {domain}")
        print(f"Refinement stages: {self.refinement_stages}")
        print(f"Rate limit delay: {self.delay}s\n")

        # Store data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {
            "timestamp": timestamp,
            "domain": domain,
            "original": proposition,
            "refinement_stages": [],
            "final": ""
        }

        print(f"Original Proposition:")
        print(f"  {proposition}\n")

        current_text = proposition

        # Refinement stages
        for stage in range(1, self.refinement_stages + 1):
            self.print_stage_header(f"REFINEMENT STAGE {stage}/{self.refinement_stages}")

            refined_text = self.refine_proposition(current_text, domain, stage)

            data["refinement_stages"].append({
                "stage": stage,
                "text": refined_text,
                "length": len(refined_text)
            })

            # Show preview
            preview = refined_text if len(refined_text) <= 100 else refined_text[:97] + "..."
            print(f"  → {preview}\n")

            current_text = refined_text

        # Final refined version
        data["final"] = current_text

        print(f"\n{'='*70}")
        print("FINAL REFINED PROPOSITION:")
        print(f"{'='*70}")
        print(f"{current_text}\n")

        # Save to work file
        work_file = f"work/proposition_{timestamp}.json"
        with open(work_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Refinement complete. Saved to: {work_file}\n")

        return data, work_file, timestamp


def main():
    """Main entry point"""
    print(f"\n{'='*70}")
    print("PROPOSITION REFINEMENT (FOR CLAUDE CODE)")
    print(f"{'='*70}\n")

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("[ERROR] ANTHROPIC_API_KEY not found in environment")
        print("\nPlease set it in your .env file or as an environment variable")
        sys.exit(1)

    try:
        # Get user input
        print("Enter your proposition (press Enter when done):")
        proposition = input("> ").strip()

        if not proposition:
            print("[ERROR] Proposition cannot be empty")
            sys.exit(1)

        print("\nEnter the academic domain (e.g., physics, philosophy, computer science):")
        domain = input("> ").strip()

        if not domain:
            domain = "general"

        # Optional: custom delay
        delay = 1.5
        if len(sys.argv) > 1:
            try:
                delay = float(sys.argv[1])
                if delay < 0.1 or delay > 10:
                    print("[WARN] Delay must be between 0.1 and 10 seconds, using default 1.5s")
                    delay = 1.5
            except ValueError:
                print("[WARN] Invalid delay value, using default 1.5s")

        # Run refinement
        pipeline = RefinementPipeline(delay_between_calls=delay)
        data, work_file, timestamp = pipeline.run_refinement(proposition, domain)

        # Instructions for Claude Code
        print(f"\n{'='*70}")
        print("NEXT STEP: USE CLAUDE CODE FOR EVALUATION & SUMMARY")
        print(f"{'='*70}\n")
        print("The proposition has been refined and saved.")
        print("Now, in your Claude Code session, run:\n")
        print(f"  python evaluate_with_claude.py {timestamp}\n")
        print("This will:")
        print("  1. Load the refined proposition")
        print("  2. Ask Claude Code to evaluate it")
        print("  3. Ask Claude Code to generate an ELI Year 12 summary")
        print("  4. Save the complete results to outputs/\n")
        print(f"{'='*70}\n")

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
