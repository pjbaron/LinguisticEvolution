#!/usr/bin/env python3
"""
Evaluate propositions using Claude Sonnet 4.5

Scoring criteria (0-10 scale):
- Novel (x8): Has this been done before? Is it original?
- Testable (x4): Can the theory be tested with the right equipment, or is it hand-waving?
- Significant (x2): Is it a big new concept or a tiny refinement?
- Coherent (x1): Is it well-formed? (Least important, can be improved later)

Final score = (novel * 8) + (testable * 4) + (significant * 2) + (coherent * 1)
Maximum possible score: 150
"""

import json
import os
import sys
from pathlib import Path
from anthropic import Anthropic

def evaluate_proposition(client, proposition_text, domain, index):
    """
    Evaluate a single proposition using Claude Sonnet 4.5

    Returns: dict with scores and reasoning
    """

    prompt = f"""You are evaluating a scientific/philosophical proposition. Please rate it on four criteria, each on a scale of 0-10:

1. **Novel** (0-10): How original is this idea? Has this been done before?
   - 0-3: Well-established or obvious idea
   - 4-6: Some novel aspects but builds heavily on existing work
   - 7-9: Genuinely new approach or insight
   - 10: Completely unprecedented idea

2. **Testable** (0-10): Can this theory be tested with appropriate equipment and methods?
   - 0-3: Pure speculation or hand-waving, not testable
   - 4-6: Partially testable but requires major assumptions or impractical resources
   - 7-9: Clearly testable with current or near-future technology
   - 10: Immediately testable with existing methods

3. **Significant** (0-10): How important is this idea?
   - 0-3: Tiny refinement or minor detail
   - 4-6: Moderate contribution to the field
   - 7-9: Major conceptual advance
   - 10: Paradigm-shifting discovery

4. **Coherent** (0-10): How well-formed and logically consistent is the proposition?
   - 0-3: Confused or contradictory
   - 4-6: Some logical gaps or unclear aspects
   - 7-9: Well-structured and logical
   - 10: Perfectly clear and coherent

**Domain:** {domain}

**Proposition to evaluate:**
{proposition_text}

Please respond ONLY with a valid JSON object in this exact format (no markdown, no code blocks):
{{
  "novel": <score>,
  "novel_reasoning": "<brief explanation>",
  "testable": <score>,
  "testable_reasoning": "<brief explanation>",
  "significant": <score>,
  "significant_reasoning": "<brief explanation>",
  "coherent": <score>,
  "coherent_reasoning": "<brief explanation>"
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent scoring
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text.strip()

        # Try to parse JSON response
        scores = json.loads(response_text)

        # Calculate weighted final score
        final_score = (
            scores["novel"] * 8 +
            scores["testable"] * 4 +
            scores["significant"] * 2 +
            scores["coherent"] * 1
        )

        scores["final_score"] = final_score
        scores["max_possible"] = 150

        return scores

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response for proposition {index}: {e}")
        print(f"Response was: {response_text}")
        return None
    except Exception as e:
        print(f"Error evaluating proposition {index}: {e}")
        return None


def evaluate_batch_file(batch_file_path, output_file_path=None):
    """
    Evaluate all propositions in a batch file
    """
    # Initialize Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Load batch file
    print(f"\nLoading batch file: {batch_file_path}")
    with open(batch_file_path, 'r') as f:
        propositions = json.load(f)

    print(f"Found {len(propositions)} propositions to evaluate\n")

    results = []

    # Evaluate each proposition
    for i, prop_data in enumerate(propositions, 1):
        print(f"Evaluating proposition {i}/{len(propositions)}...")
        print(f"Domain: {prop_data['domain']}")
        print(f"Preview: {prop_data['proposition'][:100]}...")

        evaluation = evaluate_proposition(
            client,
            prop_data['proposition'],
            prop_data['domain'],
            i
        )

        if evaluation:
            result = {
                "index": i,
                "domain": prop_data['domain'],
                "timestamp": prop_data['timestamp'],
                "proposition": prop_data['proposition'],
                "evaluation": evaluation
            }
            results.append(result)

            print(f"  Novel: {evaluation['novel']}/10 (weight: x8)")
            print(f"  Testable: {evaluation['testable']}/10 (weight: x4)")
            print(f"  Significant: {evaluation['significant']}/10 (weight: x2)")
            print(f"  Coherent: {evaluation['coherent']}/10 (weight: x1)")
            print(f"  FINAL SCORE: {evaluation['final_score']}/150\n")
        else:
            print(f"  Failed to evaluate proposition {i}\n")

    # Save results
    if output_file_path is None:
        batch_name = Path(batch_file_path).stem
        output_file_path = f"evaluation_{batch_name}.json"

    print(f"Saving results to: {output_file_path}")
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    if results:
        avg_novel = sum(r["evaluation"]["novel"] for r in results) / len(results)
        avg_testable = sum(r["evaluation"]["testable"] for r in results) / len(results)
        avg_significant = sum(r["evaluation"]["significant"] for r in results) / len(results)
        avg_coherent = sum(r["evaluation"]["coherent"] for r in results) / len(results)
        avg_final = sum(r["evaluation"]["final_score"] for r in results) / len(results)

        print(f"Total propositions evaluated: {len(results)}")
        print(f"\nAverage scores:")
        print(f"  Novel: {avg_novel:.1f}/10")
        print(f"  Testable: {avg_testable:.1f}/10")
        print(f"  Significant: {avg_significant:.1f}/10")
        print(f"  Coherent: {avg_coherent:.1f}/10")
        print(f"  Final score: {avg_final:.1f}/150")

        # Top 3 by final score
        sorted_results = sorted(results, key=lambda x: x["evaluation"]["final_score"], reverse=True)
        print(f"\nTop 3 propositions by final score:")
        for i, result in enumerate(sorted_results[:3], 1):
            print(f"  {i}. Proposition #{result['index']} ({result['domain']}): {result['evaluation']['final_score']}/150")

    print("="*60)

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluate_propositions.py <batch_file_path> [output_file_path]")
        print("Example: python evaluate_propositions.py responses/5/batch_001.json")
        sys.exit(1)

    batch_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(batch_file).exists():
        print(f"Error: File not found: {batch_file}")
        sys.exit(1)

    evaluate_batch_file(batch_file, output_file)
