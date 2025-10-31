"""
Proposition Pipeline

Generates random propositions in batches, then sends them to Claude for refinement.
Saves both original propositions and refined responses to timestamped files.
"""

import os
import sys
import json
import time
import secrets
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from anthropic import Anthropic, RateLimitError, APIError

from random_propositions import RandomPropositionGenerator

# Load environment variables
load_dotenv()


def retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Retry a function with exponential backoff for rate limit handling

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
    """
    def wrapper(*args, **kwargs):
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    print(f"[ERROR] Rate limit exceeded after {max_retries} attempts")
                    raise

                # Add jitter to avoid thundering herd
                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay

                print(f"[WARN] Rate limit hit. Waiting {actual_delay:.1f}s before retry {attempt + 1}/{max_retries}")
                time.sleep(actual_delay)

                # Exponential backoff
                delay *= exponential_base

            except APIError as e:
                # For other API errors, retry with backoff but log differently
                if attempt == max_retries - 1:
                    print(f"[ERROR] API error after {max_retries} attempts: {str(e)}")
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"[WARN] API error: {str(e)}. Retrying in {actual_delay:.1f}s")
                time.sleep(actual_delay)
                delay *= exponential_base

        return func(*args, **kwargs)

    return wrapper


class PropositionPipeline:
    """Orchestrates proposition generation and refinement"""

    def __init__(self):
        if not os.environ.get('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.generator = RandomPropositionGenerator()

        # Ensure directories exist
        os.makedirs("propositions", exist_ok=True)
        os.makedirs("responses", exist_ok=True)

    def generate_batch(self, batch_size: int = 10, delay_between_calls: float = 1.0) -> List[Dict]:
        """
        Generate a batch of random propositions

        Args:
            batch_size: Number of propositions to generate
            delay_between_calls: Delay in seconds between API calls (for rate limiting)
        """
        print(f"\n{'='*70}")
        print(f"GENERATING BATCH OF {batch_size} PROPOSITIONS")
        print(f"{'='*70}")
        print(f"[INFO] Using {delay_between_calls}s delay between API calls to avoid rate limits\n")

        propositions = []
        for i in range(batch_size):
            print(f"[{i+1}/{batch_size}] Generating proposition...")
            result = self.generator.generate_proposition(
                complexity="high",
                delay_between_calls=delay_between_calls
            )
            propositions.append(result)
            print(f"  Domain: {result['domain']}")
            print(f"  Timestamp: {result['timestamp']}")
            print(f"  -> {result['proposition'][:80]}...\n")

        return propositions

    def refine_proposition(self, proposition_data: Dict, delay_before_call: float = 1.0) -> Dict:
        """
        Send a proposition to Claude for refinement

        Args:
            proposition_data: Dict containing proposition, domain, etc.
            delay_before_call: Delay in seconds before API call (for rate limiting)

        Returns:
            Dict with refined proposition and metadata
        """
        proposition = proposition_data['proposition']
        domain = proposition_data['domain']

        # Construct refinement prompt with strong output format instructions
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

        # Add delay to avoid rate limits
        if delay_before_call > 0:
            time.sleep(delay_before_call)

        @retry_with_exponential_backoff
        def make_api_call():
            return self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.3,  # Lower temperature for more focused refinement
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

        try:
            response = make_api_call()
            refined_text = response.content[0].text.strip()

            return {
                "proposition": refined_text,
                "domain": domain,
                "timestamp": proposition_data['timestamp']  # Carry over original timestamp
            }

        except Exception as e:
            print(f"[ERROR] Failed to refine proposition: {str(e)}")
            raise

    def refine_batch(self, propositions: List[Dict], delay_between_calls: float = 1.0) -> List[Dict]:
        """
        Refine a batch of propositions

        Args:
            propositions: List of proposition dicts to refine
            delay_between_calls: Delay in seconds between API calls (for rate limiting)
        """
        print(f"\n{'='*70}")
        print(f"REFINING BATCH OF {len(propositions)} PROPOSITIONS")
        print(f"{'='*70}")
        print(f"[INFO] Using {delay_between_calls}s delay between API calls to avoid rate limits\n")

        refined = []
        for i, prop_data in enumerate(propositions):
            print(f"[{i+1}/{len(propositions)}] Refining proposition in {prop_data['domain']}...")
            result = self.refine_proposition(prop_data, delay_before_call=delay_between_calls)
            refined.append(result)
            print(f"  Original: {prop_data['proposition'][:60]}...")
            print(f"  Refined:  {result['proposition'][:60]}...\n")

        return refined

    def save_batch(self, data: List[Dict], output_dir: str, prefix: str) -> str:
        """
        Save a batch to a timestamped file

        Args:
            data: List of proposition or response dicts
            output_dir: Directory to save to (propositions or responses)
            prefix: Prefix for filename (e.g., 'batch' or 'responses')

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get domain from first item (all should be mixed domains)
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved {len(data)} items to {filepath}")
        return filepath

    def run_pipeline(self, batch_size: int = 10, delay_between_calls: float = 1.5):
        """
        Run the complete pipeline: generate -> refine -> save

        Args:
            batch_size: Number of propositions to generate
            delay_between_calls: Delay in seconds between API calls (default 1.5s for low-tier plans)
        """
        print(f"\n{'='*70}")
        print("PROPOSITION REFINEMENT PIPELINE")
        print(f"{'='*70}")
        print(f"[INFO] Rate limiting: {delay_between_calls}s delay between API calls")
        print(f"[INFO] Total API calls: {batch_size * 2} ({batch_size} generation + {batch_size} refinement)")
        print(f"[INFO] Estimated time: ~{(batch_size * 2 * delay_between_calls) / 60:.1f} minutes\n")

        try:
            # Step 1: Generate propositions
            propositions = self.generate_batch(batch_size, delay_between_calls=delay_between_calls)

            # Step 2: Save original propositions
            prop_file = self.save_batch(propositions, "propositions", "batch")

            # Step 3: Refine propositions
            refined = self.refine_batch(propositions, delay_between_calls=delay_between_calls)

            # Step 4: Save refined responses (use same timestamp format)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resp_file = self.save_batch(refined, "responses", f"responses_{timestamp.split('_')[0]}")

            # Summary
            print(f"\n{'='*70}")
            print("PIPELINE COMPLETE")
            print(f"{'='*70}")
            print(f"Generated: {len(propositions)} propositions")
            print(f"Refined: {len(refined)} propositions")
            print(f"Propositions saved to: {prop_file}")
            print(f"Responses saved to: {resp_file}")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n[ERROR] Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    try:
        # Get batch size from command line or default to 10
        batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10

        # Get delay from command line or default to 1.5s (safe for low-tier plans)
        delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5

        if batch_size < 1 or batch_size > 50:
            print("[ERROR] Batch size must be between 1 and 50")
            sys.exit(1)

        if delay < 0.1 or delay > 10:
            print("[ERROR] Delay must be between 0.1 and 10 seconds")
            sys.exit(1)

        # Run pipeline
        pipeline = PropositionPipeline()
        pipeline.run_pipeline(batch_size, delay_between_calls=delay)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
