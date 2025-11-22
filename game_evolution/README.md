# Game Code Evolution

Apply linguistic evolution principles to game development. Takes a brief game idea and evolves it through iterative refinement, building from the simplest possible version to a polished game.

## Concept

Just like linguistic evolution refines propositions through multiple stages, this system evolves game code:

1. **Stage 1**: Generate the simplest possible working version
2. **Stage 2+**: Iteratively improve following priority order:
   - Fix weak/buggy code
   - Improve existing features
   - Add new features

Each stage reads the previous version and genuinely builds upon it (file-based iteration ensures real evolution, not pre-planned multi-stage generation).

## Quick Start

```bash
# Ensure ANTHROPIC_API_KEY is set
export ANTHROPIC_API_KEY='your-api-key'

# Run the evolution
python game_evolution/game_evolver.py
```

You'll be prompted for:
- **Game idea**: Brief description (e.g., "snake game" or "guess the number")
- **Number of stages**: Recommended 3-7 iterations
- **API delay**: Seconds between calls (default 1.5s)

## Example Session

```
Enter your game idea: rock paper scissors
Number of evolution stages: 5
API delay between calls in seconds: 1.5

STAGE 1: GENERATING SIMPLEST WORKING VERSION
✓ Stage 1 complete (423 chars)

STAGE 2: EVOLVING THE GAME
✓ Stage 2 complete (587 chars)

STAGE 3: EVOLVING THE GAME
✓ Stage 3 complete (891 chars)

STAGE 4: EVOLVING THE GAME
✓ Stage 4 complete (1205 chars)

STAGE 5: EVOLVING THE GAME
✓ Stage 5 complete (1456 chars)

EVOLUTION COMPLETE
Game Idea: rock paper scissors
Code Growth: 423 → 1456 chars (3.44x)

To play the final game:
  python game_evolution/stages/stage5_20251109_020145.py
```

## Output Structure

```
game_evolution/
├── game_evolver.py          # Main evolution script
├── games/                   # Evolution records (JSON)
│   └── game_20251109_020145.json
├── stages/                  # All code stages
│   ├── stage1_20251109_020145.py
│   ├── stage2_20251109_020145.py
│   ├── stage3_20251109_020145.py
│   └── ...
└── README.md
```

## Evolution Record (JSON)

Each evolution creates a complete record:

```json
{
  "metadata": {
    "timestamp": "20251109_020145",
    "game_idea": "rock paper scissors",
    "total_stages": 5
  },
  "stages": [
    {
      "stage": 1,
      "description": "Simplest working version",
      "code": "...",
      "length": 423
    },
    {
      "stage": 2,
      "description": "Evolution iteration",
      "code": "...",
      "length": 587
    }
  ],
  "final_code": "...",
  "evolution_summary": {
    "initial_length": 423,
    "final_length": 1456,
    "growth_factor": 3.44
  }
}
```

## Evolution Principles

### Stage 1: Simplest Possible
- Minimal working implementation
- Core gameplay loop only
- Text-based when possible
- Standard library only
- Clear instructions in comments

### Stages 2+: Prioritized Improvement
1. **Fix weak code first**: Bugs, poor practices, quality issues
2. **Improve features second**: Better UI, smoother gameplay, clarity
3. **Add features last**: Only when code is solid and features polished

Each stage makes ONE significant improvement.

## Game Ideas to Try

**Simple (3-5 stages):**
- Guess the number
- Rock paper scissors
- Tic-tac-toe
- Coin flip betting
- Word guessing

**Medium (5-7 stages):**
- Snake game
- Text adventure
- Hangman
- Blackjack
- Memory matching

**Complex (7-10 stages):**
- Dungeon crawler
- Tower defense (text)
- Card game with AI
- Roguelike
- Strategy game

## Tips

1. **Start simple**: Brief game ideas work best (1-2 sentences)
2. **Moderate iterations**: 5-7 stages usually hits the sweet spot
3. **Watch evolution**: Each stage builds genuinely on the previous
4. **Play early versions**: See how the game improves over time
5. **Experiment**: Try the same game idea multiple times - you'll get different evolutions!

## Comparison to Linguistic Evolution

| Linguistic Evolution | Game Code Evolution |
|---------------------|---------------------|
| Refines propositions | Refines game code |
| Theoretical → practical | Simple → polished |
| Adds depth & clarity | Fixes bugs → adds features |
| Outputs: text | Outputs: executable Python |
| 5-10 iterations typical | 3-7 iterations typical |

## Advanced Usage

### Custom Delays

For higher-tier API plans:
```bash
python game_evolution/game_evolver.py
# Enter 0.5 for delay when prompted
```

### Viewing Evolution

Compare stages to see how the game evolved:
```bash
# View stage 1
cat game_evolution/stages/stage1_20251109_020145.py

# View stage 5
cat game_evolution/stages/stage5_20251109_020145.py

# Play different stages
python game_evolution/stages/stage1_20251109_020145.py
python game_evolution/stages/stage5_20251109_020145.py
```

### Analyzing Growth

```bash
# View full evolution record
cat game_evolution/games/game_20251109_020145.json | jq

# Extract just the summary
cat game_evolution/games/game_20251109_020145.json | jq '.evolution_summary'
```

## Why File-Based Iteration?

Like the proposition evolution system, this uses file-based iteration:

1. Stage N code is saved to a file
2. Stage N+1 reads that file before improving
3. This forces genuine evolution (not pre-planned multi-stage generation)

Without this, the LLM might mentally plan all 5 stages at once and just reveal them sequentially. File-based iteration ensures each stage genuinely builds on the previous output.

## Expected Results

**Typical Evolution Pattern:**

- **Stage 1**: Basic console I/O, minimal features (300-500 chars)
- **Stage 2**: Better error handling, clearer prompts (500-800 chars)
- **Stage 3**: Score tracking, improved UI (800-1200 chars)
- **Stage 4**: Multiple rounds, statistics (1200-1600 chars)
- **Stage 5**: Difficulty levels, polish (1600-2200 chars)

**Growth Factor**: Usually 3-5x from stage 1 to final

## Troubleshooting

**Import errors in generated code:**
- Stage 1 uses only standard library
- Later stages might add dependencies - install as needed

**Game not playable:**
- Early stages are intentionally simple
- Play later stages (4-5+) for polished versions

**Code doesn't improve:**
- Increase number of stages
- Try different game ideas (simpler often works better)

**Rate limit errors:**
- Increase delay between API calls
- Use default 1.5s for low-tier plans

## Next Steps

After running an evolution:

1. **Play the game**: See how it evolved from simple to polished
2. **Study the code**: Compare stages to see improvement patterns
3. **Try again**: Same game idea will evolve differently each time
4. **Experiment**: Try various game types and iteration counts
5. **Extend manually**: Use the final code as a starting point for your own development

## License

Same as parent project (LinguisticEvolution)
