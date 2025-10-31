# Control Pipeline Guide

## Overview

The `control.py` script orchestrates large-scale proposition generation with iterative refinement. It automatically generates batches and refines them through 5 stages until you have 500 fully polished propositions.

## Quick Start

```bash
python control.py           # Use default 1.5s delay
python control.py 1.0       # Use 1.0s delay (faster, but needs higher-tier API)
```

## How It Works

### Process Flow

For each batch of 10 propositions:

1. **Generate** → Random propositions saved to `propositions/batch_001.json`
2. **Refine Stage 1** → Load from propositions, refine, save to `responses/1/`
3. **Refine Stage 2** → Load from responses/1, refine, save to `responses/2/`
4. **Refine Stage 3** → Load from responses/2, refine, save to `responses/3/`
5. **Refine Stage 4** → Load from responses/3, refine, save to `responses/4/`
6. **Refine Stage 5** → Load from responses/4, refine, save to `responses/5/`
7. **Repeat** until 500 propositions in `responses/5/`

### Folder Structure

```
propositions/
  batch_001.json          # Original batch 1
  batch_002.json          # Original batch 2
  ...
responses/
  1/
    batch_propositions.json
    batch_propositions.json
  2/
    batch_1.json
    batch_1.json
  3/
    ...
  4/
    ...
  5/                      # FINAL OUTPUT
    batch_1.json          # Fully refined batch 1
    batch_2.json          # Fully refined batch 2
    ...
```

## Key Features

### Resume-Friendly
The script automatically counts existing propositions in `responses/5/` and resumes from where it left off. You can stop and restart anytime.

### Progress Tracking
```
BATCH 3: 20/500 complete (480 remaining)
```

The script shows clear progress updates after each batch.

### Graceful Interruption
Press Ctrl+C to stop gracefully:
```
[INTERRUPTED] Stopping gracefully...
[INFO] Current progress: 30/500 propositions
```

### Error Recovery
If a batch fails, the script logs the error and continues to the next batch.

## Time Estimates

| Delay | Time for 500 props | API Calls | Safety |
|-------|-------------------|-----------|--------|
| 2.0s  | ~3.3 hours        | 3000      | Very Safe |
| 1.5s  | ~2.5 hours        | 3000      | Safe (Default) |
| 1.0s  | ~1.7 hours        | 3000      | Moderate |
| 0.5s  | ~50 minutes       | 3000      | Risky (needs higher-tier) |

**API Call Breakdown:**
- 50 batches × 10 propositions = 500 propositions
- 500 generation calls + 2500 refinement calls = 3000 total

## Monitoring Progress

### Check Current Status
```bash
# Count files in responses/5
ls responses/5/*.json | wc -l

# View latest batch
cat responses/5/batch_050.json | jq length
```

### View Final Results
```bash
# Pretty print a final refined proposition
cat responses/5/batch_001.json | jq '.[0]'
```

Example output:
```json
{
  "proposition": "The computational complexity of distributed consensus...",
  "domain": "computer science",
  "timestamp": "2025-10-30T00:43:42.123456"
}
```

## Advanced Usage

### Custom Target
Edit `control.py` line 23:
```python
self.target_total = 1000  # Change to any target
```

### Custom Batch Size
Edit `control.py` line 22:
```python
self.batch_size = 20  # Change from 10 to 20
```

### Custom Refinement Stages
Edit `control.py` line 23:
```python
self.refinement_stages = 3  # Change from 5 to 3
```

## Troubleshooting

**Q: Script stopped, will I lose progress?**
No! Just run `python control.py` again and it will resume from where it stopped.

**Q: Getting rate limit errors?**
Increase the delay: `python control.py 2.0`

**Q: Want to check a specific stage?**
All intermediate stages are preserved in `responses/1/` through `responses/4/`

**Q: How do I restart from scratch?**
Delete the folders:
```bash
rm -rf propositions responses
python control.py
```

**Q: Can I run multiple instances?**
No, they will conflict. Only run one instance at a time.

## File Format

All files (propositions and responses at every stage) use the same format:

```json
[
  {
    "proposition": "Full text of the proposition...",
    "domain": "physics",
    "timestamp": "2025-10-30T00:43:42.123456"
  },
  {
    "proposition": "Another proposition...",
    "domain": "mathematics",
    "timestamp": "2025-10-30T00:43:45.789012"
  }
]
```

The timestamp is preserved throughout all refinement stages, allowing you to track a proposition's journey.
