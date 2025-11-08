"""
Control Script

Orchestrates the complete proposition generation and iterative refinement process:
1. Generates batches of 10 propositions
2. Refines them 5 times (responses/1 -> responses/2 -> ... -> responses/5)
3. Continues until 500 fully refined propositions are generated

Usage:
    python control.py [delay]
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from random_propositions import RandomPropositionGenerator
from refine_batch import BatchRefiner

# Load environment variables
load_dotenv()


class PropositionController:
    """Controls the complete proposition generation and refinement pipeline"""

    def __init__(self, delay_between_calls: float = 1.5):
        self.delay = delay_between_calls
        self.batch_size = 10
        self.refinement_stages = 5
        self.target_total = 500

        self.generator = RandomPropositionGenerator()
        self.refiner = BatchRefiner()

        # Create all necessary folders
        self.setup_folders()

    def setup_folders(self):
        """Create the folder structure"""
        os.makedirs("propositions", exist_ok=True)
        for stage in range(1, self.refinement_stages + 1):
            os.makedirs(f"responses/{stage}", exist_ok=True)

    def count_completed_propositions(self) -> int:
        """Count how many propositions have been fully refined (in responses/5)"""
        final_folder = Path("responses/5")

        if not final_folder.exists():
            return 0

        count = 0
        for json_file in final_folder.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    count += len(data)
                else:
                    count += 1

        return count

    def generate_batch(self, batch_num: int) -> str:
        """Generate a batch of propositions and save to propositions folder"""
        print(f"\n{'='*70}")
        print(f"GENERATING BATCH {batch_num} ({self.batch_size} propositions)")
        print(f"{'='*70}\n")

        propositions = []
        for i in range(self.batch_size):
            print(f"[{i+1}/{self.batch_size}] Generating proposition...")
            result = self.generator.generate_proposition(
                complexity="high",
                delay_between_calls=self.delay
            )
            propositions.append(result)
            print(f"  Domain: {result['domain']}")
            print(f"  -> {result['proposition'][:80]}...\n")

        # Save to propositions folder with batch number
        output_file = f"propositions/batch_{batch_num:03d}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(propositions, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved batch to {output_file}")
        return output_file

    def refine_batch_through_stages(self, batch_num: int):
        """Refine a batch through all 5 stages"""
        print(f"\n{'='*70}")
        print(f"REFINING BATCH {batch_num} THROUGH ALL STAGES")
        print(f"{'='*70}\n")

        # Stage 1: propositions -> responses/1
        input_folder = "propositions"
        input_file = f"batch_{batch_num:03d}.json"

        for stage in range(1, self.refinement_stages + 1):
            output_folder = f"responses/{stage}"

            print(f"\n{'='*70}")
            print(f"STAGE {stage}/5: Refining batch {batch_num}")
            print(f"{'='*70}")

            # For stage 1, load from propositions folder
            if stage == 1:
                source_folder = input_folder
            else:
                source_folder = f"responses/{stage-1}"

            # Create temporary folder with just this batch
            temp_input = f"temp_input_{batch_num}"
            os.makedirs(temp_input, exist_ok=True)

            # Copy the specific batch file to temp folder
            if stage == 1:
                source_file = Path(input_folder) / input_file
            else:
                source_file = Path(f"responses/{stage-1}") / f"batch_{source_folder.split('/')[-1]}.json"

            if source_file.exists():
                shutil.copy(source_file, Path(temp_input) / input_file)
            else:
                # Look for the file with the correct naming pattern
                pattern = f"batch_*{batch_num:03d}*.json"
                matches = list(Path(source_folder).glob(pattern))
                if matches:
                    shutil.copy(matches[0], Path(temp_input) / input_file)

            # Refine
            self.refiner.refine_batch(temp_input, output_folder, self.delay)

            # Clean up temp folder
            shutil.rmtree(temp_input)

            print(f"[OK] Stage {stage}/5 complete for batch {batch_num}")

    def run(self):
        """Run the complete control loop"""
        print(f"\n{'='*70}")
        print("PROPOSITION GENERATION & REFINEMENT CONTROL")
        print(f"{'='*70}")
        print(f"Target: {self.target_total} fully refined propositions")
        print(f"Batch size: {self.batch_size}")
        print(f"Refinement stages: {self.refinement_stages}")
        print(f"Rate limit delay: {self.delay}s")
        print(f"{'='*70}\n")

        # Check current progress
        completed = self.count_completed_propositions()
        print(f"[INFO] Current progress: {completed}/{self.target_total} propositions completed\n")

        batch_num = 1

        while completed < self.target_total:
            remaining = self.target_total - completed
            print(f"\n{'='*70}")
            print(f"BATCH {batch_num}: {completed}/{self.target_total} complete ({remaining} remaining)")
            print(f"{'='*70}\n")

            try:
                # Generate batch
                self.generate_batch(batch_num)

                # Refine through all stages
                self.refine_batch_through_stages(batch_num)

                # Update progress
                completed = self.count_completed_propositions()
                batch_num += 1

                print(f"\n[OK] Batch {batch_num-1} complete. Total progress: {completed}/{self.target_total}")

            except KeyboardInterrupt:
                print("\n\n[INTERRUPTED] Stopping gracefully...")
                completed = self.count_completed_propositions()
                print(f"[INFO] Current progress: {completed}/{self.target_total} propositions")
                sys.exit(0)
            except Exception as e:
                print(f"\n[ERROR] Batch {batch_num} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                print(f"[INFO] Continuing to next batch...")
                batch_num += 1
                continue

        # Final summary
        print(f"\n{'='*70}")
        print("PIPELINE COMPLETE!")
        print(f"{'='*70}")
        print(f"Generated {self.target_total} fully refined propositions")
        print(f"Final results in: responses/5/")
        print(f"Total batches processed: {batch_num - 1}")
        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    try:
        # Get delay from command line or use default
        delay = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5

        if delay < 0.1 or delay > 10:
            print("[ERROR] Delay must be between 0.1 and 10 seconds")
            sys.exit(1)

        # Run the control pipeline
        controller = PropositionController(delay_between_calls=delay)
        controller.run()

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
