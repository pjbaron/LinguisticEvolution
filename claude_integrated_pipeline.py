"""
Claude Code Integrated Pipeline

This script handles only the refinement stage, then creates a prompt for Claude Code
to handle evaluation and summarization.

Workflow:
1. User provides proposition → Script refines it 5 times
2. Script saves refined version to work/
3. Script outputs instructions for Claude Code
4. User asks Claude Code to evaluate and summarize
5. Claude Code reads the work file, evaluates, summarizes, and saves results

Usage:
    python claude_integrated_pipeline.py
"""

import os
import sys
import json
import time
import secrets
from datetime import datetime
from typing import Dict
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


def refine_proposition(client, proposition: str, domain: str, stage_num: int, delay: float) -> str:
    """Refine a proposition using Claude API"""
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

    time.sleep(delay)

    @retry_with_exponential_backoff
    def make_api_call():
        return client.messages.create(
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

    print(f"  [Stage {stage_num}/5] ✓ Refined ({len(refined_text)} chars)")

    return refined_text


def main():
    """Main entry point"""
    print(f"\n{'='*70}")
    print("CLAUDE CODE INTEGRATED PIPELINE")
    print(f"{'='*70}\n")

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("[ERROR] ANTHROPIC_API_KEY not found in environment")
        sys.exit(1)

    try:
        # Get user input
        print("Enter your proposition:")
        proposition = input("> ").strip()

        if not proposition:
            print("[ERROR] Proposition cannot be empty")
            sys.exit(1)

        print("\nEnter the academic domain:")
        domain = input("> ").strip()

        if not domain:
            domain = "general"

        # Setup
        client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        delay = 1.5
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create directories
        os.makedirs("work", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)

        # Refinement
        print(f"\n{'='*70}")
        print("REFINING PROPOSITION (5 STAGES)")
        print(f"{'='*70}\n")

        current_text = proposition
        stages = []

        for stage in range(1, 6):
            refined_text = refine_proposition(client, current_text, domain, stage, delay)
            stages.append({"stage": stage, "text": refined_text})
            current_text = refined_text

        # Save to work file
        work_data = {
            "timestamp": timestamp,
            "domain": domain,
            "original": proposition,
            "refinement_stages": stages,
            "final": current_text
        }

        work_file = f"work/proposition_{timestamp}.json"
        with open(work_file, 'w', encoding='utf-8') as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)

        # Display final version
        print(f"\n{'='*70}")
        print("REFINEMENT COMPLETE")
        print(f"{'='*70}\n")
        print(f"Final Proposition:\n{current_text}\n")
        print(f"Saved to: {work_file}\n")

        # Instructions for Claude Code
        print(f"{'='*70}")
        print("NEXT: ASK CLAUDE CODE TO EVALUATE & SUMMARIZE")
        print(f"{'='*70}\n")
        print("Copy and paste this to Claude Code:\n")
        print("-" * 70)
        print(f"""Please evaluate and summarize the proposition in {work_file}

Read the file, then provide:

1. **Evaluation** - Score the final proposition on these metrics (1-10 each):
   - Clarity: How easy is it to understand?
   - Coherence: How logically consistent is it?
   - Novelty: How original is the insight?
   - Depth: How intellectually rich is it?
   - Precision: How well-defined are the terms?

   For each metric, provide the score and a one-sentence justification.

2. **ELI Year 12 Summary** - Explain the proposition in plain language suitable for a high school senior (age 17-18). Use 2-3 short paragraphs with relatable examples.

3. **Save Results** - Combine the original data from {work_file} with your evaluation and summary, then save everything to outputs/proposition_{timestamp}.json

The output file should have this structure:
{{
  "timestamp": "...",
  "domain": "...",
  "original": "...",
  "refinement_stages": [...],
  "final": "...",
  "evaluation": {{
    "clarity": {{"score": X, "justification": "..."}},
    ...
  }},
  "eli_year12_summary": "..."
}}""")
        print("-" * 70)
        print()

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
