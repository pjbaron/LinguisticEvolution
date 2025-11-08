#!/usr/bin/env python3
"""
Helper script to format proposition requests for Claude Code

This script:
1. Prompts you for your proposition and domain
2. Outputs a formatted request to paste into Claude Code
3. No API calls = No credits used!

Usage:
    python ask_claude.py
"""

from datetime import datetime

def main():
    print("\n" + "="*70)
    print("CLAUDE CODE REQUEST FORMATTER")
    print("="*70 + "\n")
    print("This will format a request for Claude Code (FREE - no API credits used)\n")

    # Get input
    print("Enter your proposition:")
    proposition = input("> ").strip()

    if not proposition:
        print("❌ Proposition cannot be empty")
        return

    print("\nEnter the academic domain (e.g., physics, philosophy, computer science):")
    domain = input("> ").strip()

    if not domain:
        domain = "general"

    # Format the request
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "="*70)
    print("COPY AND PASTE THIS TO CLAUDE CODE:")
    print("="*70 + "\n")

    request = f"""Process this proposition through the full pipeline:

Proposition: {proposition}
Domain: {domain}

Steps:
1. Refine it 5 times iteratively (show each stage briefly)
2. Evaluate the final version on these metrics (1-10 scale):
   - Clarity: How easy is it to understand?
   - Coherence: How logically consistent is it?
   - Novelty: How original is the insight?
   - Depth: How intellectually rich is it?
   - Precision: How well-defined are the terms?

   For each metric, provide the score and a one-sentence justification.

3. Generate an ELI Year 12 summary (2-3 paragraphs, plain language)

4. Save everything to outputs/proposition_{timestamp}.json

Use this JSON structure:
{{
  "metadata": {{
    "timestamp": "{timestamp}",
    "domain": "{domain}",
    "refinement_stages": 5
  }},
  "original": "{proposition}",
  "refinement_stages": [
    {{"stage": 1, "text": "...", "length": 123}},
    {{"stage": 2, "text": "...", "length": 128}},
    {{"stage": 3, "text": "...", "length": 135}},
    {{"stage": 4, "text": "...", "length": 131}},
    {{"stage": 5, "text": "...", "length": 133}}
  ],
  "final": "...",
  "evaluation": {{
    "clarity": {{"score": X, "justification": "..."}},
    "coherence": {{"score": X, "justification": "..."}},
    "novelty": {{"score": X, "justification": "..."}},
    "depth": {{"score": X, "justification": "..."}},
    "precision": {{"score": X, "justification": "..."}},
    "overall": X.X
  }},
  "eli_year12_summary": "..."
}}

Show me:
- Brief preview of each refinement stage
- All evaluation scores with justifications
- The ELI Year 12 summary
- Confirmation when saved"""

    print(request)
    print("\n" + "="*70)
    print("\n✅ Copy the text above and paste it to Claude Code!")
    print("💡 This uses your FREE Claude Code credits, not API credits\n")

if __name__ == "__main__":
    main()
