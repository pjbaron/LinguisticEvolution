"""
Refine Batch Script

Loads propositions from an input folder and refines them using Claude,
saving the refined versions to an output folder.

Usage:
    python refine_batch.py <input_folder> <output_folder> [delay]
"""

import os
import sys
import json
import time
import secrets
from pathlib import Path
from typing import List, Dict
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


class BatchRefiner:
    """Refines propositions from one folder to another"""

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)

    def load_propositions_from_folder(self, folder_path: str) -> List[Dict]:
        """Load all JSON files from a folder"""
        propositions = []
        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"Input folder not found: {folder_path}")

        json_files = sorted(folder.glob("*.json"))

        if not json_files:
            raise FileNotFoundError(f"No JSON files found in: {folder_path}")

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both list and single object formats
                if isinstance(data, list):
                    propositions.extend(data)
                else:
                    propositions.append(data)

        print(f"[OK] Loaded {len(propositions)} propositions from {folder_path}")
        return propositions

    def refine_proposition(self, prop_data: Dict, delay_before_call: float = 1.5) -> Dict:
        """Refine a single proposition"""
        proposition = prop_data['proposition']
        domain = prop_data['domain']
        timestamp = prop_data['timestamp']

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
                temperature=0.3,
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
                "timestamp": timestamp  # Carry over original timestamp
            }

        except Exception as e:
            print(f"[ERROR] Failed to refine proposition: {str(e)}")
            raise

    def refine_batch(
        self,
        input_folder: str,
        output_folder: str,
        delay_between_calls: float = 1.5
    ) -> int:
        """
        Refine all propositions from input folder to output folder

        Returns:
            Number of propositions refined
        """
        print(f"\n{'='*70}")
        print(f"REFINING BATCH: {input_folder} -> {output_folder}")
        print(f"{'='*70}")
        print(f"[INFO] Using {delay_between_calls}s delay between API calls\n")

        # Load propositions
        propositions = self.load_propositions_from_folder(input_folder)

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        # Refine each proposition
        refined = []
        for i, prop_data in enumerate(propositions):
            print(f"[{i+1}/{len(propositions)}] Refining proposition in {prop_data['domain']}...")
            result = self.refine_proposition(prop_data, delay_before_call=delay_between_calls)
            refined.append(result)
            print(f"  Original: {prop_data['proposition'][:60]}...")
            print(f"  Refined:  {result['proposition'][:60]}...\n")

        # Save refined propositions to output folder
        # Extract the original batch filename from the input folder
        input_files = list(Path(input_folder).glob("*.json"))
        if input_files:
            # Use the same filename as the input file (preserves batch number)
            original_filename = input_files[0].name
        else:
            # Fallback: use folder name
            original_filename = f"batch_{Path(input_folder).name}.json"

        output_file = Path(output_folder) / original_filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(refined, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved {len(refined)} refined propositions to {output_file}")
        return len(refined)


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python refine_batch.py <input_folder> <output_folder> [delay]")
        print("\nExample:")
        print("  python refine_batch.py propositions responses/1 1.5")
        print("  python refine_batch.py responses/1 responses/2 1.5")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5

    if delay < 0.1 or delay > 10:
        print("[ERROR] Delay must be between 0.1 and 10 seconds")
        sys.exit(1)

    try:
        refiner = BatchRefiner()
        count = refiner.refine_batch(input_folder, output_folder, delay)

        print(f"\n{'='*70}")
        print("[OK] BATCH REFINEMENT COMPLETE")
        print(f"{'='*70}")
        print(f"Refined {count} propositions")
        print(f"{'='*70}\n")

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
