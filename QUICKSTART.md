# Quick Start Guide

Get started with proposition processing in 30 seconds.

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY='your-key-here'
```

## Process a Single Proposition (Fully Automated)

```bash
python process_proposition.py
```

**That's it!** Just enter your proposition and domain when prompted.

### What Happens

1. **Refinement** - Your proposition is refined 5 times
2. **Evaluation** - Scored on 5 metrics (clarity, coherence, novelty, depth, precision)
3. **Summary** - ELI Year 12 (high school senior) explanation generated
4. **Output** - Everything saved to `outputs/proposition_TIMESTAMP.json`

### Example

```
Enter your proposition:
> Language models learn human cognitive biases from training data

Enter the academic domain:
> computer science

REFINEMENT (5 STAGES)
----------------------------------------------------------------------
  ✓ Stage 1/5 complete (234 chars)
  ✓ Stage 2/5 complete (245 chars)
  ✓ Stage 3/5 complete (251 chars)
  ✓ Stage 4/5 complete (248 chars)
  ✓ Stage 5/5 complete (252 chars)

FINAL REFINED PROPOSITION
----------------------------------------------------------------------
[Your refined proposition appears here]

EVALUATION
----------------------------------------------------------------------
📊 Evaluation Scores:
  Clarity       8/10 - The proposition clearly articulates...
  Coherence     9/10 - Logically structured with consistent...
  Novelty       7/10 - Addresses a known concern but with...
  Depth         8/10 - Engages with substantive implications...
  Precision     9/10 - Technical terms are well-defined...

  Overall       8.2/10

ELI YEAR 12 SUMMARY
----------------------------------------------------------------------
Think of language models like students who learn from textbooks. If
those textbooks contain certain patterns or biases, the student will
pick them up too. When we train AI on human-written text, it doesn't
just learn facts and grammar - it also absorbs the subtle biases and
assumptions that humans have...

✅ Results saved to: outputs/proposition_20251101_143052.json
```

## Output File Structure

```json
{
  "metadata": {
    "timestamp": "20251101_143052",
    "domain": "computer science",
    "refinement_stages": 5
  },
  "original": "Your original proposition",
  "refinement_stages": [
    {"stage": 1, "text": "...", "length": 234},
    {"stage": 2, "text": "...", "length": 245},
    ...
  ],
  "final": "Final refined proposition",
  "evaluation": {
    "clarity": {"score": 8, "justification": "..."},
    "coherence": {"score": 9, "justification": "..."},
    "novelty": {"score": 7, "justification": "..."},
    "depth": {"score": 8, "justification": "..."},
    "precision": {"score": 9, "justification": "..."},
    "overall": 8.2
  },
  "eli_year12_summary": "Plain language explanation..."
}
```

## Time & Cost

- **Time:** ~10-15 seconds
- **API Calls:** 7 total
  - 5 refinement calls
  - 1 evaluation call
  - 1 summary call

## Advanced Options

### Custom Rate Limit Delay

```bash
# Use 1.0s delay (faster, needs higher-tier API)
python process_proposition.py 1.0

# Use 2.0s delay (safer for low-tier API)
python process_proposition.py 2.0
```

### View Results

```bash
# Pretty print latest result
ls -t outputs/*.json | head -1 | xargs cat | jq

# View just the evaluation scores
cat outputs/proposition_*.json | jq '.evaluation'

# View just the summary
cat outputs/proposition_*.json | jq -r '.eli_year12_summary'
```

## Other Workflows

### Batch Processing (500 propositions)

```bash
# Generate and refine 500 random propositions
python control.py
```

See [CONTROL_PIPELINE.md](CONTROL_PIPELINE.md) for details.

### Random Proposition Generation

```bash
# Generate 10 random propositions
python random_propositions.py 10
```

See [README.md](README.md) for all available tools.

## Troubleshooting

**API Key Not Found**
```bash
export ANTHROPIC_API_KEY='your-key-here'
# Or add to .env file
```

**Rate Limit Errors**
```bash
# Increase delay between calls
python process_proposition.py 2.0
```

**Want to see intermediate steps?**
- All 5 refinement stages are saved in the output file
- Check the `refinement_stages` array in the JSON output

## Next Steps

- ✅ Process your first proposition with `process_proposition.py`
- 📖 Read [README.md](README.md) for full documentation
- 🔄 Try the Claude Code workflow in [CLAUDE_CODE_WORKFLOW.md](CLAUDE_CODE_WORKFLOW.md)
- 📊 Generate batches with [CONTROL_PIPELINE.md](CONTROL_PIPELINE.md)
