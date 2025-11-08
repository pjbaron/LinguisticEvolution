# Using Claude Code Directly (FREE - No API Credits Used)

This workflow uses your free Claude Code credits instead of your paid API credits.

## Quick Start

Just ask me (Claude Code) directly! No scripts, no API calls.

### Format Your Request

```
Please process this proposition through the full pipeline:

Proposition: [Your proposition here]
Domain: [e.g., physics, philosophy, computer science]

Steps:
1. Refine it 5 times iteratively (show each stage)
2. Evaluate on: clarity, coherence, novelty, depth, precision (1-10 scale with justifications)
3. Generate an ELI Year 12 summary
4. Save everything to outputs/proposition_[timestamp].json

Use this JSON structure:
{
  "metadata": {
    "timestamp": "YYYYMMDD_HHMMSS",
    "domain": "...",
    "refinement_stages": 5
  },
  "original": "...",
  "refinement_stages": [
    {"stage": 1, "text": "...", "length": 123},
    ...
  ],
  "final": "...",
  "evaluation": {
    "clarity": {"score": X, "justification": "..."},
    "coherence": {"score": X, "justification": "..."},
    "novelty": {"score": X, "justification": "..."},
    "depth": {"score": X, "justification": "..."},
    "precision": {"score": X, "justification": "..."},
    "overall": X.X
  },
  "eli_year12_summary": "..."
}
```

## Example

**You:**
```
Please process this proposition through the full pipeline:

Proposition: Language models learn human cognitive biases from training data
Domain: computer science

[Include the steps and JSON structure from above]
```

**Me (Claude Code):**
- I'll refine your proposition 5 times
- Show you each refinement stage
- Evaluate it on all 5 metrics
- Generate an accessible summary
- Save everything to a timestamped file
- Show you the results

## Benefits

✅ **FREE** - Uses your Claude Code credits (no API charges)
✅ **Interactive** - You can see my reasoning and ask questions
✅ **Transparent** - You see exactly what I'm doing at each step
✅ **Flexible** - Can adjust criteria or ask for changes mid-process
✅ **No setup** - No API keys, no scripts to run

## Comparison

| Method | Cost | Speed | Interaction |
|--------|------|-------|-------------|
| **Direct Claude Code** | FREE (your credits) | ~30 sec | High - conversational |
| process_proposition.py | $$ (API credits) | ~10 sec | None - fully automated |
| claude_integrated_pipeline.py | $ (API for refinement) | ~15 sec | Medium - copy/paste |

## Even Simpler Version

Just tell me:

**"Process this proposition: [your proposition]. Domain: [domain]. Do 5 refinements, evaluate it, create an ELI Year 12 summary, and save to outputs/"**

I'll know what to do! 😊

## Tips

1. **Be specific about domain** - Helps me tailor refinements and evaluation
2. **Check outputs/ folder** - I'll save the timestamped JSON there
3. **Ask for adjustments** - Want different evaluation criteria? Just ask!
4. **Request explanations** - Want to know why I gave a certain score? Ask!

## Save Time with a Template

Copy this template and fill in your proposition:

```
Process this proposition through the full pipeline:

Proposition: [YOUR PROPOSITION HERE]
Domain: [YOUR DOMAIN HERE]

Do:
1. 5 refinement stages
2. Evaluate: clarity, coherence, novelty, depth, precision
3. ELI Year 12 summary
4. Save to outputs/proposition_[timestamp].json

Show me each refinement stage and the final scores.
```

## Why This Works

- I (Claude Code) have access to file operations
- I can read, write, and execute within your repository
- Your free Claude Code credits cover all of this
- No external API calls = No charges to your Anthropic account

## Alternative: Helper Script

If you want something to format your input, use:

```bash
python ask_claude.py
```

This just collects your proposition and outputs a formatted request for you to paste here.
(But honestly, you can just ask me directly - it's faster!)
