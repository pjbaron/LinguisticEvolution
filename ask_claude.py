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

IMPORTANT: Each refinement must genuinely build on the previous one. To ensure this happens (rather than generating all 5 versions mentally at once), you must use file-based iteration where you save each stage and then READ it back before refining further.

**Why file-based iteration?** Reading from a file forces you to actually process the previous refinement rather than just simulating what iteration might look like. This produces genuine improvement across stages.

**Stage 1:**
Refine the original proposition using this framing:

"You are an expert in {domain}. A colleague has shared this proposition with you:

'{proposition}'

Please improve it by:
1. Making the core idea more clear and precise
2. Highlighting the key insights or implications
3. Advancing the core idea from a theoretical proposition towards a practical implementation
4. Ensuring proper logical flow
5. Removing any sentences or excess verbiage that doesn't contribute value
6. Adding your own further insights (the colleague is a good friend and welcomes your input)

Output ONLY the improved proposition text (no meta-commentary)."

Save the refined version to: work/stage1_{timestamp}.txt

**Stage 2:**
Read the content from: work/stage1_{timestamp}.txt
Now act as the expert again and apply the same 6-point refinement process to what you just read (treating it as a colleague's proposition).
Save the result to: work/stage2_{timestamp}.txt

**Stage 3:**
Read the content from: work/stage2_{timestamp}.txt
Apply the expert refinement process again (6 improvement points above).
Save the result to: work/stage3_{timestamp}.txt

**Stage 4:**
Read the content from: work/stage3_{timestamp}.txt
Apply the expert refinement process again (6 improvement points above).
Save the result to: work/stage4_{timestamp}.txt

**Stage 5:**
Read the content from: work/stage4_{timestamp}.txt
Apply the expert refinement process again (6 improvement points above). This is the final iteration, pay extra attention to the structure.
Save the result to: work/stage5_{timestamp}.txt

After completing all stages, show a brief summary describing:
- How the proposition evolved from the original to the final version
- What major concepts or improvements were added
- How the length/complexity changed

**TASK 2: ELI Year 12 Summary**
Create a plain-language explanation suitable for a high school senior (age 17-18):
- 2-3 paragraphs
- Use accessible language and relatable examples
- Explain technical terms when needed
- Make it engaging and relevant

**TASK 3: Save Results**
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
  "eli_year12_summary": "..."
}}

Show me:
- Brief preview of each refinement stage
- The ELI Year 12 summary
- Confirmation when saved"""

    print(request)
    print("\n" + "="*70)
    print("\n✅ Copy the text above and paste it to Claude Code!")
    print("This uses your Claude Code free credits, not API credits\n")

if __name__ == "__main__":
    main()
