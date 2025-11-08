# Rate Limiting Guide

## Overview

Both `random_propositions.py` and `proposition_pipeline.py` include comprehensive rate limiting protection for low-tier API plans.

## Quick Reference

### Command-Line Usage

```bash
# Default (safest for low-tier plans)
python proposition_pipeline.py 10        # 10 propositions, 1.5s delay

# Custom delay
python proposition_pipeline.py 10 2.0    # 10 propositions, 2.0s delay
python proposition_pipeline.py 10 0.5    # 10 propositions, 0.5s delay (risky for low-tier)
```

### Time Estimates

For a batch of 10 propositions (20 API calls total):

| Delay | Total Time | Risk Level |
|-------|------------|------------|
| 2.0s  | ~40s       | Very Safe  |
| 1.5s  | ~30s       | Safe (Default) |
| 1.0s  | ~20s       | Moderate   |
| 0.5s  | ~10s       | Risky for low-tier |

## How It Works

### 1. Proactive Delay
- Adds configurable delay between API calls
- Prevents hitting rate limits in the first place
- Default: 1.5 seconds

### 2. Exponential Backoff Retry
When rate limits are hit, the system automatically:
1. Waits 1 second (with jitter)
2. Retries the request
3. If it fails again, waits 2 seconds
4. Then 4 seconds, 8 seconds, 16 seconds
5. Up to 5 total retry attempts

### 3. Random Jitter
- Adds ±0-100% random variation to delays
- Prevents multiple requests from synchronizing
- Avoids "thundering herd" problems

## Error Messages

```
[INFO] Using 1.5s delay between API calls to avoid rate limits
```
Normal operation message showing delay setting.

```
[WARN] Rate limit hit. Waiting 2.1s before retry 1/5
```
Rate limit encountered, automatic retry in progress.

```
[ERROR] Rate limit exceeded after 5 attempts
```
All retries exhausted, you may need to increase delay or wait before retrying.

## Recommendations

### Low-Tier Plans
- Use default 1.5s delay
- Keep batch sizes ≤ 20
- If you see rate limit warnings, increase delay to 2.0s

### Mid-Tier Plans
- Try 1.0s delay
- Batch sizes up to 50 should work

### High-Tier Plans
- Use 0.5s delay
- Batch sizes limited only by time

## Testing Your Rate Limits

Run a small test batch first:

```bash
# Start conservative
python test_pipeline.py    # 2 propositions with 1.5s delay

# If no rate limit warnings, try larger batch
python proposition_pipeline.py 5

# Gradually increase if successful
python proposition_pipeline.py 10
python proposition_pipeline.py 20
```

## Advanced: Modifying Retry Behavior

Edit the `retry_with_exponential_backoff` function in either script:

```python
def retry_with_exponential_backoff(
    func,
    max_retries: int = 5,           # Increase for more patience
    initial_delay: float = 1.0,     # First retry wait time
    exponential_base: float = 2.0,  # How aggressively to back off
    jitter: bool = True             # Random variation
):
```

## Troubleshooting

**Q: Still hitting rate limits with 1.5s delay?**
- Increase to 2.0s or 3.0s
- Reduce batch size
- Check if other scripts are using your API key

**Q: Process is too slow?**
- Reduce delay (but monitor for rate limit warnings)
- Consider upgrading API tier
- Run multiple small batches instead of one large batch

**Q: Getting API errors other than rate limits?**
- Check your API key is valid
- Verify internet connection
- Wait a few minutes and retry
