# Random Proposition Generator

Generates meaningful-sounding but genuinely random propositions using true randomness and Claude LLM.

## Features

- **True Randomness**: Uses random.org API for atmospheric noise-based random numbers
- **High-Quality Output**: Claude LLM ensures propositions are believable and coherent
- **Dictionary Encoding**: Maps random numbers to words for seed concepts
- **Multiple Domains**: Randomly selects from 20+ academic fields
- **Cryptographic Fallback**: Uses Python's `secrets` module if random.org is unavailable

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key:
   ```bash
   # Linux/Mac
   export ANTHROPIC_API_KEY='your-api-key'

   # Windows CMD
   set ANTHROPIC_API_KEY=your-api-key

   # Windows PowerShell
   $env:ANTHROPIC_API_KEY='your-api-key'
   ```

3. (Optional) Add your dictionary.txt file:
   - Place a text file with one word per line
   - The program includes a fallback dictionary if not provided

## Usage

Generate 5 random propositions (default):
```bash
python random_propositions.py
```

Generate a specific number:
```bash
python random_propositions.py 10
```

## Output

Propositions are:
- Saved to `propositions_output.json`
- Displayed in the console
- Include metadata (seed words, domain, random source)

## Example Output

```
[1/5] Generating proposition...
  → Quantum epistemology demonstrates that consciousness exhibits isomorphic
      properties with topological structures in phase space, suggesting that
      semantic emergence follows recursive optimization patterns.

[2/5] Generating proposition...
  → The dialectical synthesis of entropy and cognitive variance produces
      algorithmic correlations that fundamentally challenge traditional
      phenomenological inference models.
```

## Pipeline Modes

### Fully Automated Pipeline (process_proposition.py) ⭐ RECOMMENDED

**Zero human intervention - complete automation:**

```bash
python process_proposition.py
```

Enter your proposition once, then everything happens automatically:
- ✅ 5-stage iterative refinement
- ✅ Multi-metric evaluation (clarity, coherence, novelty, depth, precision)
- ✅ ELI Year 12 summary generation
- ✅ Real-time progress display with emojis
- ✅ Complete results saved to timestamped file

**Example output:**
```
REFINEMENT (5 STAGES)
----------------------------------------------------------------------
  ✓ Stage 1/5 complete (234 chars)
  ✓ Stage 2/5 complete (245 chars)
  ...

EVALUATION
----------------------------------------------------------------------
📊 Evaluation Scores:
  Clarity       8/10 - The proposition clearly articulates...
  Coherence     9/10 - Logically structured with consistent...
  Overall      8.2/10

ELI YEAR 12 SUMMARY
----------------------------------------------------------------------
[Plain language explanation displayed here]

✅ Results saved to: outputs/proposition_20251101_143052.json
```

**Time:** ~10-15 seconds total (7 API calls)

### Claude Code Interactive Workflow (claude_integrated_pipeline.py)

**For when you want human-in-the-loop evaluation:**

```bash
# Step 1: Automated refinement
python claude_integrated_pipeline.py

# Step 2: Copy/paste prompt to Claude Code for evaluation
```

Useful when you want to:
- See Claude Code's reasoning process
- Adjust evaluation criteria interactively
- Have conversational context

See **[CLAUDE_CODE_WORKFLOW.md](CLAUDE_CODE_WORKFLOW.md)** for details.

### Simple Pipeline (proposition_pipeline.py)

Single-stage generation and refinement:

```bash
# Generate and refine 10 propositions (default, 1.5s delay between API calls)
python proposition_pipeline.py

# Generate and refine custom batch size (1-50)
python proposition_pipeline.py 20

# Custom batch size with custom delay (for higher-tier plans)
python proposition_pipeline.py 20 0.5

# Quick test with 2 propositions
python test_pipeline.py
```

### Iterative Refinement Pipeline (control.py)

**Automated large-scale generation with 5-stage iterative refinement:**

```bash
# Generate 500 propositions with 5 stages of refinement (default 1.5s delay)
python control.py

# Custom delay for higher-tier plans
python control.py 0.5
```

**How it works:**
1. Generates batch of 10 propositions → saves to `propositions/`
2. Refines batch → saves to `responses/1/`
3. Refines again → saves to `responses/2/`
4. Continues through `responses/3/`, `responses/4/`, `responses/5/`
5. Repeats until 500 fully refined propositions in `responses/5/`

**Features:**
- Automatically tracks progress (resume-friendly)
- Graceful interrupt handling (Ctrl+C)
- Each proposition refined 5 times total
- Timestamps preserved throughout all stages
- Folder structure: propositions → responses/1 → responses/2 → ... → responses/5

### Manual Refinement (refine_batch.py)

Refine propositions from one folder to another:

```bash
# Refine propositions to responses/1
python refine_batch.py propositions responses/1 1.5

# Refine responses/1 to responses/2
python refine_batch.py responses/1 responses/2 1.5

# Any folder to any folder
python refine_batch.py responses/3 responses/4 1.5
```

### Pipeline Features

- **Expert Prompting**: Each refinement starts with "You are an expert in {domain}"
- **Strong Output Formatting**: Prompts heavily emphasize returning ONLY the refined proposition
- **Batch Processing**: Efficient generation and refinement in batches
- **Timestamped Storage**: Both originals and refinements saved with timestamps
- **Domain Tracking**: Each proposition includes its academic domain
- **Rate Limit Handling**:
  - Configurable delays between API calls (default 1.5s for low-tier plans)
  - Exponential backoff retry logic (up to 5 retries)
  - Automatic recovery from transient API errors
  - Jittered backoff to avoid thundering herd problems

## How It Works

1. **Random Number Generation**: Fetches true random numbers from random.org
2. **Word Selection**: Maps random numbers to dictionary words as seed concepts
3. **Domain Selection**: Randomly picks an academic domain
4. **Proposition Generation**: Claude weaves seeds into a believable proposition
5. **Refinement**: Second Claude call improves clarity and removes non-value
6. **Quality Assurance**: Output is authoritative, coherent, and non-trivial

## Customization

Edit `random_propositions.py` to:
- Add more domains (line 130)
- Adjust complexity levels
- Modify proposition criteria
- Change output format

Edit `proposition_pipeline.py` to:
- Modify refinement prompt
- Change batch sizes
- Adjust temperature settings
- Customize output format

## Rate Limiting

Both scripts include robust rate limit handling for low-tier API plans:

**Default Settings (Low-Tier Plans):**
- 1.5s delay between API calls
- 5 retry attempts with exponential backoff
- Automatic jitter to prevent synchronization issues

**For Higher-Tier Plans:**
```bash
# Reduce delay to 0.5s for faster processing
python proposition_pipeline.py 10 0.5
```

**Retry Behavior:**
- Initial retry delay: 1 second
- Exponential backoff: 2x multiplier (1s → 2s → 4s → 8s → 16s)
- Random jitter: ±100% to avoid synchronized retries
- Maximum retries: 5 attempts before failure

**Estimated Times:**

*Simple Pipeline (10 propositions, 1 refinement):*
- With 1.5s delay: ~0.5 minutes (20 API calls)
- With 1.0s delay: ~0.3 minutes
- With 0.5s delay: ~0.2 minutes

*Control Pipeline (500 propositions, 5 refinements):*
- With 1.5s delay: ~2.5 hours (3000 API calls total)
- With 1.0s delay: ~1.7 hours
- With 0.5s delay: ~50 minutes

Note: Control pipeline runs batches sequentially, so you can stop/resume anytime.
