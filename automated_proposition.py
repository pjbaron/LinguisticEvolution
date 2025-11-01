"""
Automated Proposition Pipeline

Interactive system that:
1. Takes a user-provided proposition
2. Refines it iteratively through 5 stages
3. Evaluates it with multiple metrics
4. Generates an ELI Year 12 (high school senior) summary
5. Saves all stages to a timestamped output file

Usage:
    python automated_proposition.py
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


class AutomatedPropositionPipeline:
    """Complete automated pipeline for proposition refinement and evaluation"""

    def __init__(self, delay_between_calls: float = 1.5):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.delay = delay_between_calls
        self.refinement_stages = 5

        # Ensure output directory exists
        os.makedirs("outputs", exist_ok=True)

    def print_stage_header(self, stage: str):
        """Print a formatted stage header"""
        print(f"\n{'='*70}")
        print(f"STAGE: {stage}")
        print(f"{'='*70}\n")

    def refine_proposition(self, proposition: str, domain: str, stage_num: int) -> str:
        """
        Refine a proposition using Claude

        Args:
            proposition: The text to refine
            domain: Academic domain
            stage_num: Current refinement stage number

        Returns:
            Refined proposition text
        """
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

    def evaluate_proposition(self, proposition: str, domain: str) -> Dict:
        """
        Evaluate a proposition on multiple metrics

        Returns:
            Dict with scores for clarity, coherence, novelty, depth, and precision
        """
        self.print_stage_header("EVALUATION")

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
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

        response = make_api_call()
        evaluation_text = response.content[0].text.strip()

        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in evaluation_text:
            evaluation_text = evaluation_text.split("```json")[1].split("```")[0].strip()
        elif "```" in evaluation_text:
            evaluation_text = evaluation_text.split("```")[1].split("```")[0].strip()

        try:
            evaluation = json.loads(evaluation_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            evaluation = {
                "clarity": {"score": 0, "justification": "Parsing error"},
                "coherence": {"score": 0, "justification": "Parsing error"},
                "novelty": {"score": 0, "justification": "Parsing error"},
                "depth": {"score": 0, "justification": "Parsing error"},
                "precision": {"score": 0, "justification": "Parsing error"}
            }

        # Display scores
        print("Evaluation Scores:")
        print(f"  Clarity:    {evaluation['clarity']['score']}/10 - {evaluation['clarity']['justification']}")
        print(f"  Coherence:  {evaluation['coherence']['score']}/10 - {evaluation['coherence']['justification']}")
        print(f"  Novelty:    {evaluation['novelty']['score']}/10 - {evaluation['novelty']['justification']}")
        print(f"  Depth:      {evaluation['depth']['score']}/10 - {evaluation['depth']['justification']}")
        print(f"  Precision:  {evaluation['precision']['score']}/10 - {evaluation['precision']['justification']}")

        # Calculate overall score
        overall = sum(e['score'] for e in evaluation.values()) / len(evaluation)
        print(f"\n  Overall:    {overall:.1f}/10")

        evaluation['overall'] = overall

        return evaluation

    def generate_eli_summary(self, proposition: str, domain: str) -> str:
        """
        Generate an "Explain Like I'm Year 12" summary
        (High school senior level explanation)
        """
        self.print_stage_header("ELI YEAR 12 SUMMARY")

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
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

        response = make_api_call()
        summary = response.content[0].text.strip()

        print(summary)

        return summary

    def save_results(self, results: Dict) -> str:
        """
        Save all results to a timestamped JSON file

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/proposition_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Results saved to: {filename}")
        return filename

    def run_pipeline(self, proposition: str, domain: str):
        """
        Run the complete pipeline

        Args:
            proposition: Initial proposition text
            domain: Academic domain
        """
        print(f"\n{'='*70}")
        print("AUTOMATED PROPOSITION REFINEMENT & EVALUATION PIPELINE")
        print(f"{'='*70}")
        print(f"Domain: {domain}")
        print(f"Refinement stages: {self.refinement_stages}")
        print(f"Rate limit delay: {self.delay}s")
        print(f"{'='*70}\n")

        # Store all data
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "domain": domain,
                "refinement_stages": self.refinement_stages
            },
            "original": proposition,
            "refinement_stages": [],
            "evaluation": {},
            "eli_year12_summary": ""
        }

        # Show original
        print(f"Original Proposition:")
        print(f"  {proposition}\n")

        current_text = proposition

        # Refinement stages
        for stage in range(1, self.refinement_stages + 1):
            self.print_stage_header(f"REFINEMENT STAGE {stage}/{self.refinement_stages}")

            refined_text = self.refine_proposition(current_text, domain, stage)

            results["refinement_stages"].append({
                "stage": stage,
                "text": refined_text,
                "length": len(refined_text)
            })

            # Show preview
            preview = refined_text if len(refined_text) <= 100 else refined_text[:97] + "..."
            print(f"  → {preview}\n")

            current_text = refined_text

        # Final refined version
        final_proposition = current_text
        results["final"] = final_proposition

        print(f"\n{'='*70}")
        print("FINAL REFINED PROPOSITION:")
        print(f"{'='*70}")
        print(f"{final_proposition}\n")

        # Evaluation
        evaluation = self.evaluate_proposition(final_proposition, domain)
        results["evaluation"] = evaluation

        # ELI Year 12 Summary
        eli_summary = self.generate_eli_summary(final_proposition, domain)
        results["eli_year12_summary"] = eli_summary

        # Save results
        output_file = self.save_results(results)

        # Final summary
        print(f"\n{'='*70}")
        print("PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"Refinement stages completed: {self.refinement_stages}")
        print(f"Overall evaluation score: {evaluation['overall']:.1f}/10")
        print(f"Output file: {output_file}")
        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    print(f"\n{'='*70}")
    print("AUTOMATED PROPOSITION PIPELINE")
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

        # Run pipeline
        pipeline = AutomatedPropositionPipeline(delay_between_calls=delay)
        pipeline.run_pipeline(proposition, domain)

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
