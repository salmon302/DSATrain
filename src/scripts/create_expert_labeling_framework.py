from __future__ import annotations

import argparse
from pathlib import Path

from src.processors.star_rubric_synthesizer import STARRubricSynthesizer
from src.collectors.expert_response_collector import ExpertResponseCollector


def main() -> None:
    parser = argparse.ArgumentParser(description="Create expert labeling framework for STAR method responses")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    parser.add_argument("--prompts", type=int, default=200, help="Number of prompts to generate for expert responses")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating expert labeling framework for STAR method responses...")
    print("This synthesizes research-based evaluation rubrics and creates expert collection tools.")
    
    # Step 1: Synthesize master rubric from research sources
    print("\n=== Step 1: Synthesizing Master Evaluation Rubric ===")
    rubric_synthesizer = STARRubricSynthesizer(data_dir)
    rubric_results = rubric_synthesizer.run_synthesis()
    
    # Step 2: Create expert response collection framework  
    print(f"\n=== Step 2: Creating Expert Collection Framework ({args.prompts} prompts) ===")
    response_collector = ExpertResponseCollector(data_dir)
    collection_results = response_collector.run_collection_setup(args.prompts)
    
    # Summary
    print("\n=== Expert Labeling Framework Complete ===")
    print(f"📋 Master rubric: {rubric_results['rubric_file']}")
    print(f"📝 Sample responses: {rubric_results['samples_file']}")
    print(f"📖 Labeling guidelines: {rubric_results['guidelines_file']}")
    print(f"❓ Expert prompts: {collection_results['package_file']}")
    print(f"📋 Collection template: Generated in expert_labeled directory")
    print(f"\n🎯 Ready for expert recruitment and response collection!")
    print(f"   Target: 3-5 experts × 40-60 responses = 200+ labeled examples")


if __name__ == "__main__":
    main()
