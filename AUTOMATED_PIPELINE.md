# Automated Proposition Pipeline

Interactive system that takes a user-provided proposition and automatically runs it through the complete refinement, evaluation, and summarization process.

## Features

- **Interactive Input**: Simply type your proposition and domain
- **5-Stage Iterative Refinement**: Automatically refines your proposition 5 times
- **Multi-Metric Evaluation**: Scores on clarity, coherence, novelty, depth, and precision
- **ELI Year 12 Summary**: Generates a high-school-senior-level explanation
- **Real-Time Progress Display**: Shows current stage and scores as they're calculated
- **Complete Output File**: All stages saved to timestamped JSON file

## Quick Start

```bash
python automated_proposition.py
```

Then follow the prompts:
1. Enter your proposition
2. Enter the academic domain (e.g., "physics", "philosophy", "computer science")
3. Wait for the pipeline to complete

## What It Does

### 1. Iterative Refinement (5 Stages)
Your proposition is refined 5 times using Claude, with each stage:
- Making the core idea clearer
- Improving logical flow
- Adding expert insights
- Removing unnecessary content

### 2. Evaluation
The final refined proposition is evaluated on 5 metrics:

| Metric | Description |
|--------|-------------|
| **Clarity** | How easy is it to understand? |
| **Coherence** | How logically consistent is it? |
| **Novelty** | How original is the insight? |
| **Depth** | How intellectually rich is it? |
| **Precision** | How well-defined are the terms? |

Each metric is scored 1-10 with a justification.

### 3. ELI Year 12 Summary
Generates a clear, accessible explanation suitable for a high school senior:
- Plain language (minimal jargon)
- Relatable examples and analogies
- 2-3 concise paragraphs
- Makes the idea interesting and relevant

### 4. Timestamped Output
Everything is saved to `outputs/proposition_YYYYMMDD_HHMMSS.json`:
- Original proposition
- All 5 refinement stages
- Evaluation scores with justifications
- ELI Year 12 summary
- Metadata (timestamp, domain, etc.)

## Example Session

```
AUTOMATED PROPOSITION PIPELINE
======================================================================

Enter your proposition (press Enter when done):
> Quantum entanglement suggests that information can travel faster than light

Enter the academic domain (e.g., physics, philosophy, computer science):
> physics

======================================================================
AUTOMATED PROPOSITION REFINEMENT & EVALUATION PIPELINE
======================================================================
Domain: physics
Refinement stages: 5
Rate limit delay: 1.5s
======================================================================

Original Proposition:
  Quantum entanglement suggests that information can travel faster than light

======================================================================
STAGE: REFINEMENT STAGE 1/5
======================================================================

[Stage 1] ✓ Refined (245 chars)
  → Quantum entanglement demonstrates non-local correlations between particles...

[... stages 2-5 ...]

======================================================================
FINAL REFINED PROPOSITION:
======================================================================
[Refined proposition displayed here]

======================================================================
STAGE: EVALUATION
======================================================================

Evaluation Scores:
  Clarity:    8/10 - The proposition clearly articulates the core concept
  Coherence:  9/10 - Logically structured with consistent argumentation
  Novelty:    6/10 - Addresses a well-known quantum phenomenon
  Depth:      8/10 - Engages with subtle aspects of quantum mechanics
  Precision:  9/10 - Technical terms are well-defined

  Overall:    8.0/10

======================================================================
STAGE: ELI YEAR 12 SUMMARY
======================================================================

[Accessible summary displayed here]

[OK] Results saved to: outputs/proposition_20251101_143052.json

======================================================================
PIPELINE COMPLETE
======================================================================
Refinement stages completed: 5
Overall evaluation score: 8.0/10
Output file: outputs/proposition_20251101_143052.json
======================================================================
```

## Output File Format

```json
{
  "metadata": {
    "timestamp": "2025-11-01T14:30:52.123456",
    "domain": "physics",
    "refinement_stages": 5
  },
  "original": "Your original proposition...",
  "refinement_stages": [
    {
      "stage": 1,
      "text": "First refinement...",
      "length": 245
    },
    // ... stages 2-5 ...
  ],
  "final": "Final refined proposition...",
  "evaluation": {
    "clarity": {
      "score": 8,
      "justification": "..."
    },
    // ... other metrics ...
    "overall": 8.0
  },
  "eli_year12_summary": "Accessible explanation..."
}
```

## Usage Options

### Basic Usage
```bash
python automated_proposition.py
```

### Custom Rate Limit Delay
```bash
# Use 1.0s delay (for higher-tier API plans)
python automated_proposition.py 1.0

# Use 2.0s delay (extra safe for low-tier plans)
python automated_proposition.py 2.0
```

## Time Estimates

| Delay | Total Time | API Calls | Safety |
|-------|-----------|-----------|--------|
| 2.0s  | ~14 seconds | 7 calls | Very Safe |
| 1.5s  | ~10 seconds | 7 calls | Safe (Default) |
| 1.0s  | ~7 seconds  | 7 calls | Moderate |
| 0.5s  | ~3 seconds  | 7 calls | Risky (higher-tier needed) |

**API Call Breakdown:**
- 5 refinement calls
- 1 evaluation call
- 1 ELI summary call
- **Total: 7 API calls per proposition**

## Integration with Existing Tools

This automated pipeline is separate from but compatible with the batch processing system:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `random_propositions.py` | Generate random propositions | None | JSON batch files |
| `control.py` | Batch refinement (500 props) | Batch files | `responses/5/` |
| `automated_proposition.py` | **Single interactive run** | **User input** | **Timestamped JSON** |

## Advanced Customization

Edit `automated_proposition.py` to customize:

### Change Refinement Stages
```python
self.refinement_stages = 3  # Line 79: Change from 5 to 3
```

### Modify Evaluation Metrics
Add or remove metrics in the `evaluate_proposition()` method (line 147)

### Adjust Temperature/Tokens
Modify API call parameters:
- Refinement: Line 136 (temperature=0.3)
- Evaluation: Line 201 (temperature=0.3)
- ELI Summary: Line 242 (temperature=0.5)

## Troubleshooting

**Q: Getting rate limit errors?**
Increase the delay: `python automated_proposition.py 2.0`

**Q: Where are the output files?**
Check the `outputs/` directory. Each run creates a uniquely timestamped file.

**Q: Can I run multiple propositions?**
Yes! Just run the script multiple times. Each creates a separate output file.

**Q: How do I view past results?**
All results are in `outputs/`. Use `cat outputs/proposition_*.json | jq` to view them nicely.

**Q: Can I modify the prompts?**
Yes! Edit the prompt strings in the script:
- Refinement prompt: Line 103
- Evaluation prompt: Line 147
- ELI prompt: Line 226

## Examples

### Example 1: Philosophy
```bash
> python automated_proposition.py
Enter your proposition:
> Free will is an emergent property of complex deterministic systems

Enter the academic domain:
> philosophy

# Pipeline runs...
# Overall score: 7.8/10
```

### Example 2: Computer Science
```bash
> python automated_proposition.py
Enter your proposition:
> Machine learning models can develop emergent reasoning capabilities

Enter the academic domain:
> computer science

# Pipeline runs...
# Overall score: 8.2/10
```

## Dependencies

- `anthropic` - Claude API client
- `python-dotenv` - Environment variable management
- Python 3.8+ required

All dependencies are in `requirements.txt`.

## See Also

- `README.md` - Main project documentation
- `CONTROL_PIPELINE.md` - Batch processing guide
- `RATE_LIMITING.md` - API rate limit strategies
