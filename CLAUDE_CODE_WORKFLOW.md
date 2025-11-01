# Claude Code Integrated Workflow

This is the recommended workflow that combines automated refinement with Claude Code's evaluation and summarization capabilities.

## Why This Workflow?

- **Automated Refinement**: Script handles 5 stages of proposition refinement via API
- **Claude Code Evaluation**: Leverages Claude Code's context and conversation for nuanced evaluation
- **Best of Both**: Fast automated refinement + thoughtful human-in-the-loop evaluation

## Quick Start

### Step 1: Refine Your Proposition

```bash
python claude_integrated_pipeline.py
```

Enter your proposition and domain when prompted. The script will:
- Refine it through 5 stages
- Save to `work/proposition_YYYYMMDD_HHMMSS.json`
- Display instructions for Step 2

### Step 2: Ask Claude Code to Evaluate

The script outputs a prompt for you. Copy and paste it to Claude Code.

Claude Code will:
- Read the refined proposition from the work file
- Evaluate it on 5 metrics (clarity, coherence, novelty, depth, precision)
- Generate an ELI Year 12 summary
- Save everything to `outputs/proposition_YYYYMMDD_HHMMSS.json`

## Complete Example

```bash
$ python claude_integrated_pipeline.py

Enter your proposition:
> Quantum entanglement suggests information can travel faster than light

Enter the academic domain:
> physics

======================================================================
REFINING PROPOSITION (5 STAGES)
======================================================================

  [Stage 1/5] ✓ Refined (234 chars)
  [Stage 2/5] ✓ Refined (245 chars)
  [Stage 3/5] ✓ Refined (251 chars)
  [Stage 4/5] ✓ Refined (248 chars)
  [Stage 5/5] ✓ Refined (252 chars)

======================================================================
REFINEMENT COMPLETE
======================================================================

Final Proposition:
[Refined proposition displayed here]

Saved to: work/proposition_20251101_143052.json

======================================================================
NEXT: ASK CLAUDE CODE TO EVALUATE & SUMMARIZE
======================================================================

Copy and paste this to Claude Code:

----------------------------------------------------------------------
Please evaluate and summarize the proposition in work/proposition_20251101_143052.json

[Full prompt displayed here...]
----------------------------------------------------------------------
```

Then in your Claude Code session:

```
You: Please evaluate and summarize the proposition in work/proposition_20251101_143052.json
     [paste the full prompt]

Claude Code: [Reads file, evaluates, summarizes, and saves results]
```

## Output File Structure

The final file in `outputs/` contains:

```json
{
  "timestamp": "20251101_143052",
  "domain": "physics",
  "original": "Your original proposition...",
  "refinement_stages": [
    {"stage": 1, "text": "..."},
    {"stage": 2, "text": "..."},
    ...
  ],
  "final": "Final refined proposition...",
  "evaluation": {
    "clarity": {"score": 8, "justification": "..."},
    "coherence": {"score": 9, "justification": "..."},
    "novelty": {"score": 7, "justification": "..."},
    "depth": {"score": 8, "justification": "..."},
    "precision": {"score": 9, "justification": "..."}
  },
  "eli_year12_summary": "Plain language explanation..."
}
```

## Workflow Comparison

| Workflow | Refinement | Evaluation | Summary | Best For |
|----------|------------|------------|---------|----------|
| **claude_integrated_pipeline.py** | Automated (API) | Claude Code | Claude Code | Interactive sessions with Claude Code |
| **automated_proposition.py** | Automated (API) | Automated (API) | Automated (API) | Fully hands-off automation |

## Time Estimate

- **Step 1 (Refinement)**: ~7-8 seconds (5 API calls)
- **Step 2 (Evaluation via Claude Code)**: ~5-10 seconds (depends on Claude Code response)
- **Total**: ~15-20 seconds

## Advantages Over Fully Automated

1. **Conversational Context**: Claude Code can ask clarifying questions if needed
2. **Nuanced Evaluation**: Human-in-the-loop for evaluation decisions
3. **Transparency**: You see exactly what Claude Code evaluates
4. **Flexibility**: Can adjust evaluation criteria on the fly
5. **Learning**: See Claude Code's reasoning process

## Tips

1. **Keep Claude Code Open**: Have your Claude Code session ready before running the script
2. **Copy Full Prompt**: Make sure to copy the entire prompt including the JSON structure
3. **Review Results**: Claude Code will show you the evaluation before saving
4. **Iterate**: If you want different evaluation criteria, just ask Claude Code to adjust

## Troubleshooting

**Q: The script says API key not found**
A: Set `ANTHROPIC_API_KEY` in your environment or `.env` file

**Q: Can I skip refinement and just evaluate?**
A: Yes! Just create a work file manually with your proposition and ask Claude Code to evaluate it

**Q: Can I refine multiple propositions at once?**
A: Run the script multiple times. Each gets its own timestamped work file.

**Q: Can Claude Code save directly to outputs/?**
A: Yes! Just ask Claude Code to save the combined results after evaluation.

## See Also

- [AUTOMATED_PIPELINE.md](AUTOMATED_PIPELINE.md) - Fully automated workflow
- [README.md](README.md) - Full project documentation
- [CONTROL_PIPELINE.md](CONTROL_PIPELINE.md) - Batch processing system
