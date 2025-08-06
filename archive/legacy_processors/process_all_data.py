"""
Process all collected Codeforces data
"""

import json
from pathlib import Path
from process_data_simple import SimpleCodeforcesProcessor

def main():
    print("Processing ALL Codeforces Data")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    # Initialize processor
    processor = SimpleCodeforcesProcessor(data_dir)
    
    # Find raw Codeforces data
    raw_file = data_dir / "raw" / "codeforces" / "problems" / "problems_simple.json"
    
    if not raw_file.exists():
        print(f"Error: Raw data file not found: {raw_file}")
        return
    
    # Load all data
    with open(raw_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    print(f"Found {all_data.get('total_problems', 0)} problems")
    
    # Process all problems
    problems = processor.process_raw_problems(raw_file)
    
    # Save processed problems
    output_file = data_dir / "processed" / "codeforces_all_problems_processed.json"
    summary = processor.save_processed_problems(problems, output_file)
    
    # Create filtered exports
    processor.create_filtered_exports(problems)
    
    print("\n" + "=" * 60)
    print("FULL PROCESSING COMPLETED!")
    print("=" * 60)
    print(f"Total problems processed: {len(problems)}")
    print(f"Google-relevant problems: {summary['google_relevant']}")
    
    print("\nDifficulty distribution:")
    for level, count in summary["by_difficulty"].items():
        percentage = (count / len(problems)) * 100
        print(f"  {level}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nTop 15 tags:")
    for tag, count in list(summary["top_tags"].items())[:15]:
        print(f"  {tag}: {count:,}")
    
    if "google_relevance_stats" in summary:
        gr_stats = summary["google_relevance_stats"]
        print(f"\nGoogle Relevance Statistics:")
        print(f"  Average score: {gr_stats['avg_score']}")
        print(f"  High relevance (≥7.0): {gr_stats['high_relevance_count']:,}")
        print(f"  Tagged as Google: {summary['google_relevant']:,}")
    
    print(f"\nRating distribution:")
    print(f"  Rated problems: {summary['rating_distribution']['rated']:,}")
    print(f"  Unrated problems: {summary['rating_distribution']['unrated']:,}")
    if summary['rating_distribution']['avg_rating']:
        print(f"  Average rating: {summary['rating_distribution']['avg_rating']}")

if __name__ == "__main__":
    main()
