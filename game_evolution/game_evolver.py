#!/usr/bin/env python3
"""
Game Code Evolution System

Similar to linguistic evolution for propositions, but for game development.
Takes a brief game idea and evolves it through iterative refinement:
- Stage 1: Simplest possible working version
- Stage 2+: Improve weak code → enhance features → add new features

Uses file-based iteration to ensure genuine evolution rather than
pre-planned multi-stage generation.
"""

import os
import json
import time
from datetime import datetime
from anthropic import Anthropic

def get_client():
    """Initialize Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return Anthropic(api_key=api_key)

def call_claude(client, prompt, delay=1.5):
    """Call Claude API with rate limiting."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        time.sleep(delay)
        return response.content[0].text
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise

def generate_stage1(client, game_idea, timestamp, delay):
    """Generate the simplest possible working version of the game."""
    print(f"\n{'='*70}")
    print("STAGE 1: GENERATING SIMPLEST WORKING VERSION")
    print(f"{'='*70}\n")

    prompt = f"""You are an expert game developer. Create the SIMPLEST possible working version of this game:

Game Idea: {game_idea}

Requirements:
1. Write complete, executable Python code
2. Keep it as simple as possible while being playable
3. Use only standard library (no external dependencies unless absolutely necessary)
4. Include clear instructions in comments at the top
5. Make it text-based if the game idea allows (for simplicity)
6. Focus on core gameplay loop only

Output ONLY the Python code, no explanations or markdown. Start directly with the code."""

    code = call_claude(client, prompt, delay)

    # Clean up markdown code blocks if present
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    elif code.startswith("```"):
        code = code.split("```")[1].split("```")[0].strip()

    stage_file = f"game_evolution/stages/stage1_{timestamp}.py"
    with open(stage_file, 'w') as f:
        f.write(code)

    print(f"✓ Stage 1 complete ({len(code)} chars)")
    print(f"  Saved to: {stage_file}")

    return code

def evolve_stage(client, stage_num, previous_code, timestamp, delay):
    """Evolve the game code through improvement."""
    print(f"\n{'='*70}")
    print(f"STAGE {stage_num}: EVOLVING THE GAME")
    print(f"{'='*70}\n")

    prompt = f"""You are an expert game developer reviewing and improving a game.

Here is the current version of the game code:

```python
{previous_code}
```

Improve this game by following these priorities IN ORDER:

1. **Fix weak/buggy code**: If there are bugs, poor practices, or code quality issues, fix them FIRST
2. **Improve existing features**: If code quality is good, enhance what's already there (better UI, smoother gameplay, clearer instructions)
3. **Add new features**: Only if code is solid and features are polished, add ONE new meaningful feature

Guidelines:
- Make ONE significant improvement per iteration
- Keep the code clean and well-commented
- Maintain all existing functionality
- Don't overcomplicate - stay focused
- Ensure the game remains playable and fun

Output ONLY the complete improved Python code, no explanations or markdown. Start directly with the code."""

    code = call_claude(client, prompt, delay)

    # Clean up markdown code blocks if present
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    elif code.startswith("```"):
        code = code.split("```")[1].split("```")[0].strip()

    stage_file = f"game_evolution/stages/stage{stage_num}_{timestamp}.py"
    with open(stage_file, 'w') as f:
        f.write(code)

    print(f"✓ Stage {stage_num} complete ({len(code)} chars)")
    print(f"  Saved to: {stage_file}")

    return code

def save_evolution_record(game_idea, timestamp, num_stages, stages_data):
    """Save complete evolution record as JSON."""
    output_file = f"game_evolution/games/game_{timestamp}.json"

    record = {
        "metadata": {
            "timestamp": timestamp,
            "game_idea": game_idea,
            "total_stages": num_stages,
            "evolution_date": datetime.now().isoformat()
        },
        "stages": stages_data,
        "final_code": stages_data[-1]["code"],
        "evolution_summary": {
            "initial_length": stages_data[0]["length"],
            "final_length": stages_data[-1]["length"],
            "growth_factor": round(stages_data[-1]["length"] / stages_data[0]["length"], 2)
        }
    }

    with open(output_file, 'w') as f:
        json.dump(record, f, indent=2)

    return output_file

def main():
    print("\n" + "="*70)
    print("GAME CODE EVOLUTION SYSTEM")
    print("="*70 + "\n")

    # Get user input
    game_idea = input("Enter your game idea (brief description): ").strip()
    if not game_idea:
        print("❌ Game idea cannot be empty")
        return

    try:
        num_stages = int(input("Number of evolution stages (recommended 3-7): ").strip())
        if num_stages < 1:
            print("❌ Must have at least 1 stage")
            return
    except ValueError:
        print("❌ Please enter a valid number")
        return

    delay = float(input("API delay between calls in seconds (default 1.5): ").strip() or "1.5")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*70}")
    print(f"CONFIGURATION")
    print(f"{'='*70}")
    print(f"Game Idea: {game_idea}")
    print(f"Total Stages: {num_stages}")
    print(f"API Delay: {delay}s")
    print(f"Session ID: {timestamp}")
    print(f"{'='*70}\n")

    # Initialize client
    client = get_client()

    # Track all stages
    stages_data = []

    # Stage 1: Generate simplest version
    code = generate_stage1(client, game_idea, timestamp, delay)
    stages_data.append({
        "stage": 1,
        "description": "Simplest working version",
        "code": code,
        "length": len(code)
    })

    # Stages 2+: Evolve
    for stage_num in range(2, num_stages + 1):
        code = evolve_stage(client, stage_num, code, timestamp, delay)
        stages_data.append({
            "stage": stage_num,
            "description": "Evolution iteration",
            "code": code,
            "length": len(code)
        })

    # Save final record
    output_file = save_evolution_record(game_idea, timestamp, num_stages, stages_data)

    # Print summary
    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"\nGame Idea: {game_idea}")
    print(f"Total Stages: {num_stages}")
    print(f"Code Growth: {stages_data[0]['length']} → {stages_data[-1]['length']} chars")
    print(f"Growth Factor: {stages_data[-1]['length'] / stages_data[0]['length']:.2f}x")
    print(f"\n✅ Final game saved to: {output_file}")
    print(f"✅ All stages saved to: game_evolution/stages/")
    print(f"\nTo play the final game:")
    print(f"  python game_evolution/stages/stage{num_stages}_{timestamp}.py")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
