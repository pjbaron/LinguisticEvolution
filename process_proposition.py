"""
Fully Automated Proposition Processing Pipeline

Single command - complete automation from start to finish:
1. User provides proposition (once)
2. Automated 5-stage refinement
3. Automated evaluation with scoring
4. Automated ELI Year 12 summary
5. Real-time progress display
6. Complete results saved to timestamped file

No human intervention after initial input.

Usage:
    python process_proposition.py
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
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"  ⏳ Rate limit - waiting {actual_delay:.1f}s (retry {attempt + 1}/{max_retries})")
                time.sleep(actual_delay)
                delay *= exponential_base

            except APIError as e:
                if attempt == max_retries - 1:
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"  ⏳ API error - retrying in {actual_delay:.1f}s")
                time.sleep(actual_delay)
                delay *= exponential_base

        return func(*args, **kwargs)

    return wrapper


class AutomatedProcessor:
    """Fully automated proposition processor"""

    def __init__(self, delay: float = 1.5):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = Anthropic(api_key=api_key)
        self.delay = delay
        os.makedirs("outputs", exist_ok=True)

    def print_header(self, text: str, char: str = "="):
        """Print formatted header"""
        print(f"\n{char*70}")
        print(text)
        print(f"{char*70}\n")

    def refine(self, proposition: str, domain: str, stage: int) -> str:
        """Refine proposition once"""
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
                messages=[{"role": "user", "content": prompt}]
            )

        response = make_api_call()
        refined = response.content[0].text.strip()

        print(f"  ✓ Stage {stage}/5 complete ({len(refined)} chars)")
        return refined

    def evaluate(self, proposition: str, domain: str) -> Dict:
        """Evaluate proposition on multiple metrics"""
        prompt = f"""You are evaluating an academic proposition in the field of {domain}.

Proposition:
"{proposition}"

Please evaluate this proposition on the following dimensions. For each dimension, provide:
1. A score from 1-10
2. A brief justification (one sentence)

Dimensions:
- CLARITY: How easy is it to understand the core claim?
- COHERENCE: How logically consistent and well-structured is it?
- NOVELTY: How original or non-obvious is the insight?
- DEPTH: How substantive and intellectually rich is the proposition?
- PRECISION: How specific and well-defined are the terms and claims?

Format your response as JSON:
{{
  "clarity": {{"score": X, "justification": "..."}},
  "coherence": {{"score": X, "justification": "..."}},
  "novelty": {{"score": X, "justification": "..."}},
  "depth": {{"score": X, "justification": "..."}},
  "precision": {{"score": X, "justification": "..."}}
}}

Output ONLY the JSON, no additional text."""

        time.sleep(self.delay)

        @retry_with_exponential_backoff
        def make_api_call():
            return self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

        response = make_api_call()
        evaluation_text = response.content[0].text.strip()

        # Extract JSON
        if "```json" in evaluation_text:
            evaluation_text = evaluation_text.split("```json")[1].split("```")[0].strip()
        elif "```" in evaluation_text:
            evaluation_text = evaluation_text.split("```")[1].split("```")[0].strip()

        try:
            evaluation = json.loads(evaluation_text)
            overall = sum(e['score'] for e in evaluation.values()) / len(evaluation)
            evaluation['overall'] = round(overall, 1)
        except json.JSONDecodeError:
            evaluation = {
                "clarity": {"score": 0, "justification": "Error parsing"},
                "coherence": {"score": 0, "justification": "Error parsing"},
                "novelty": {"score": 0, "justification": "Error parsing"},
                "depth": {"score": 0, "justification": "Error parsing"},
                "precision": {"score": 0, "justification": "Error parsing"},
                "overall": 0
            }

        return evaluation

    def summarize(self, proposition: str, domain: str) -> str:
        """Generate ELI Year 12 summary"""
        prompt = f"""You are explaining an academic proposition to a Year 12 student (high school senior, age 17-18).

Domain: {domain}
Proposition: "{proposition}"

Create a clear, accessible explanation that:
1. Explains the key idea in plain language
2. Uses relatable examples or analogies
3. Avoids unnecessary jargon (or explains technical terms when needed)
4. Keeps it concise (2-3 short paragraphs)
5. Makes it interesting and relevant

Write the explanation directly, without meta-commentary like "Here's an explanation" or "This means"."""

        time.sleep(self.delay)

        @retry_with_exponential_backoff
        def make_api_call():
            return self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

        response = make_api_call()
        return response.content[0].text.strip()

    def process(self, proposition: str, domain: str) -> str:
        """Run complete automated pipeline"""

        self.print_header("AUTOMATED PROPOSITION PROCESSING")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"📝 Domain: {domain}")
        print(f"⏱️  Timestamp: {timestamp}")
        print(f"🔄 Delay: {self.delay}s between API calls\n")

        # Store results
        results = {
            "metadata": {
                "timestamp": timestamp,
                "domain": domain,
                "refinement_stages": 5
            },
            "original": proposition,
            "refinement_stages": [],
            "final": "",
            "evaluation": {},
            "eli_year12_summary": ""
        }

        # Display original
        print(f"Original Proposition:")
        print(f"  {proposition}\n")

        # Refinement
        self.print_header("REFINEMENT (5 STAGES)", "-")

        current = proposition
        for stage in range(1, 6):
            refined = self.refine(current, domain, stage)
            results["refinement_stages"].append({
                "stage": stage,
                "text": refined,
                "length": len(refined)
            })
            current = refined

        results["final"] = current

        # Display final
        self.print_header("FINAL REFINED PROPOSITION", "-")
        print(f"{current}\n")

        # Evaluation
        self.print_header("EVALUATION", "-")
        print("⏳ Evaluating proposition...")

        evaluation = self.evaluate(current, domain)
        results["evaluation"] = evaluation

        # Display scores
        print("\n📊 Evaluation Scores:")
        for metric in ['clarity', 'coherence', 'novelty', 'depth', 'precision']:
            score = evaluation[metric]['score']
            just = evaluation[metric]['justification']
            print(f"  {metric.capitalize():12} {score:2}/10 - {just}")

        print(f"\n  {'Overall':12} {evaluation['overall']}/10\n")

        # Summary
        self.print_header("ELI YEAR 12 SUMMARY", "-")
        print("⏳ Generating summary...")

        summary = self.summarize(current, domain)
        results["eli_year12_summary"] = summary

        print(f"\n{summary}\n")

        # Save
        output_file = f"outputs/proposition_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.print_header("COMPLETE")
        print(f"✅ Processing complete!")
        print(f"📁 Results saved to: {output_file}")
        print(f"📊 Overall score: {evaluation['overall']}/10")
        print(f"🔢 Total API calls: 7 (5 refinements + 1 evaluation + 1 summary)")
        print()

        return output_file


def main():
    """Main entry point"""

    print("\n" + "="*70)
    print("AUTOMATED PROPOSITION PROCESSOR")
    print("="*70 + "\n")

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("\nSet it in .env file or as environment variable")
        sys.exit(1)

    try:
        # Get input
        print("Enter your proposition:")
        proposition = input("> ").strip()

        if not proposition:
            print("❌ ERROR: Proposition cannot be empty")
            sys.exit(1)

        print("\nEnter the academic domain (e.g., physics, philosophy, computer science):")
        domain = input("> ").strip()

        if not domain:
            domain = "general"

        # Optional delay override
        delay = 1.5
        if len(sys.argv) > 1:
            try:
                delay = float(sys.argv[1])
                if delay < 0.1 or delay > 10:
                    delay = 1.5
            except ValueError:
                pass

        # Process
        processor = AutomatedProcessor(delay=delay)
        output_file = processor.process(proposition, domain)

        print("="*70)
        print(f"✅ SUCCESS - Results in {output_file}")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
