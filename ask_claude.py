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

    request = f"""I need you to refine, evaluate, and summarize the following academic proposition:

**Proposition:** {proposition}
**Domain:** {domain}

Please complete these tasks:

**TASK 1: Iterative Refinement (5 stages)**
Refine this proposition 5 times. For each refinement:
- Act as an expert in {domain}
- Make the core idea clearer and more precise
- Improve logical flow and remove unnecessary content
- Add valuable insights
- Output ONLY the refined proposition text (no meta-commentary)

Show a brief preview of each of the 5 refined versions.

**TASK 2: Evaluation (score 1-10 on each metric)**
Evaluate the final refined version on these five metrics:
- **Clarity:** How easy is it to understand the core claim?
- **Coherence:** How logically consistent and well-structured is it?
- **Novelty:** How original or non-obvious is the insight?
- **Depth:** How substantive and intellectually rich is it?
- **Precision:** How specific and well-defined are the terms?

For each metric, provide both a score (1-10) and a one-sentence justification.
Calculate the overall average score.

**TASK 3: ELI Year 12 Summary**
Create a plain-language explanation suitable for a high school senior (age 17-18):
- 2-3 paragraphs
- Use accessible language and relatable examples
- Explain technical terms when needed
- Make it engaging and relevant

**TASK 4: Save Results**
Save all results to: outputs/proposition_{timestamp}.json

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
