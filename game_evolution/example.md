# Example Evolution: Snake Game

This example shows what a typical game evolution looks like.

## Input

```
Game idea: snake game
Number of stages: 5
API delay: 1.5s
```

## Evolution Timeline

### Stage 1: Simplest Version (487 chars)
```python
# Minimal text-based snake
# - 10x10 grid
# - WASD controls
# - Apple spawns randomly
# - Game over on wall hit or self-collision
```

**Playability**: Basic but functional
**Features**: Core gameplay only

### Stage 2: Improved Error Handling (682 chars)
```python
# Added:
# - Input validation
# - Better collision detection
# - Clear error messages
# - Proper game loop
```

**Improvement**: Fixed bugs, cleaner code
**Category**: Code quality fixes

### Stage 3: Enhanced Features (931 chars)
```python
# Added:
# - Score tracking
# - Snake length display
# - Better visual representation (# for snake, O for apple)
# - Game state display
```

**Improvement**: Better UI/UX
**Category**: Feature enhancement

### Stage 4: New Gameplay Elements (1284 chars)
```python
# Added:
# - Speed increases as score grows
# - Multiple lives system
# - High score tracking
# - Restart option
```

**Improvement**: More engaging gameplay
**Category**: New features

### Stage 5: Polish & Additional Features (1653 chars)
```python
# Added:
# - Difficulty selection (easy/medium/hard)
# - Pause functionality
# - Better grid rendering
# - Instructions at startup
# - Statistics display
```

**Improvement**: Professional polish
**Category**: New features + refinement

## Growth Summary

| Metric | Value |
|--------|-------|
| Initial size | 487 chars |
| Final size | 1653 chars |
| Growth factor | 3.39x |
| Stages | 5 |
| Time | ~2 minutes |

## Evolution Pattern

1. **Stage 1**: Minimal viable game
2. **Stage 2**: Fix quality issues (code improvement priority)
3. **Stage 3**: Enhance what's there (feature improvement priority)
4. **Stage 4**: Add meaningful features (new features priority)
5. **Stage 5**: Professional polish (mixed)

## Key Observations

- Each stage genuinely builds on the previous
- Code quality improves before features are added
- Growth is exponential (later stages add more)
- Final version is production-ready for a simple game

## Trying It Yourself

```bash
python game_evolution/game_evolver.py
# Enter: snake game
# Enter: 5
# Enter: 1.5

# Play the evolved game
python game_evolution/stages/stage5_TIMESTAMP.py
```

## Variations

Same game idea evolved differently:

**Run 1**: Text grid → Color indicators → AI opponent
**Run 2**: Text grid → ASCII art → Difficulty modes
**Run 3**: Text grid → Obstacles → Power-ups

Each evolution takes a different path based on what the LLM identifies as the highest priority improvement at each stage.
