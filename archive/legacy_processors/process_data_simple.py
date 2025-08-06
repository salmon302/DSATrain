"""
Simple Data Processing Pipeline for DSATrain Platform
Converts raw Codeforces data into standardized JSON format
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class SimpleCodeforcesProcessor:
    """
    Process raw Codeforces data into standardized format without external dependencies
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw" / "codeforces"
        self.processed_dir = data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def _convert_rating_to_difficulty(self, rating: Optional[int]) -> str:
        """Convert Codeforces rating to difficulty level"""
        if rating is None:
            return "medium"
        
        if rating <= 1200:
            return "easy"
        elif rating <= 2000:
            return "medium"
        else:
            return "hard"
    
    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """Normalize and clean tags"""
        normalized = []
        for tag in tags:
            # Convert to lowercase and replace spaces with underscores
            clean_tag = tag.lower().replace(" ", "_").replace("-", "_")
            normalized.append(clean_tag)
        return normalized
    
    def _calculate_google_relevance_score(self, tags: List[str], rating: Optional[int]) -> float:
        """
        Calculate how relevant a problem is for Google interviews
        Based on tags and difficulty rating
        """
        google_relevant_tags = {
            "algorithms", "data_structures", "dynamic_programming", "graphs", 
            "trees", "arrays", "strings", "binary_search", "sorting", "hashing",
            "greedy", "divide_and_conquer", "backtracking", "recursion", "math",
            "geometry", "implementation", "two_pointers", "brute_force", "dp",
            "graph", "tree", "string", "array", "hash", "sort", "search"
        }
        
        score = 0.0
        
        # Tag relevance (0-5 points)
        relevant_tag_count = sum(1 for tag in tags if any(gt in tag for gt in google_relevant_tags))
        score += min(relevant_tag_count * 1.25, 5.0)
        
        # Difficulty preference (0-3 points) - Google prefers medium difficulty
        if rating:
            if 1200 <= rating <= 2200:  # Sweet spot for interviews
                score += 3.0
            elif 800 <= rating < 1200 or 2200 < rating <= 2800:
                score += 2.0
            elif rating < 800 or rating > 2800:
                score += 1.0
        else:
            score += 1.5  # Default for unrated
        
        # Bonus for specific high-value tags (0-2 points)
        high_value_tags = ["dynamic_programming", "graphs", "trees", "binary_search"]
        bonus = sum(0.5 for tag in tags if any(hvt in tag for hvt in high_value_tags))
        score += min(bonus, 2.0)
        
        return min(score, 10.0)  # Cap at 10
    
    def process_raw_problems(self, input_file: Path) -> List[Dict[str, Any]]:
        """
        Process raw Codeforces problems into standardized format
        """
        print(f"Processing {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        problems = []
        # Handle both formats: direct list or nested in "problems" key
        if isinstance(data, list):
            raw_problems = data
        else:
            raw_problems = data.get("problems", [])
        
        print(f"Converting {len(raw_problems)} raw problems...")
        
        for i, raw_problem in enumerate(raw_problems):
            try:
                # Create unique ID
                contest_id = raw_problem.get("contestId", "unknown")
                index = raw_problem.get("index", str(i))
                problem_id = f"cf_{contest_id}_{index}"
                
                # Extract basic info
                title = raw_problem.get("name", "Untitled Problem")
                tags = self._normalize_tags(raw_problem.get("tags", []))
                rating = raw_problem.get("rating")
                points = raw_problem.get("points")
                
                # Calculate Google relevance
                google_score = self._calculate_google_relevance_score(tags, rating)
                company_tags = ["google"] if google_score >= 7.0 else []
                
                # Create standardized problem object
                problem = {
                    "id": problem_id,
                    "source": "codeforces",
                    "title": title,
                    "description": f"Problem: {title}\nTags: {', '.join(tags)}\nRating: {rating or 'Unrated'}",
                    "difficulty": {
                        "level": self._convert_rating_to_difficulty(rating),
                        "rating": rating,
                        "source_scale": "codeforces_rating"
                    },
                    "tags": tags,
                    "company_tags": company_tags,
                    "google_relevance_score": round(google_score, 2),
                    "constraints": {
                        "time_limit": "2000ms",
                        "memory_limit": "256MB",
                        "input_size": f"Based on {rating} rating" if rating else "Standard"
                    },
                    "source_url": f"https://codeforces.com/contest/{contest_id}/problem/{index}" if contest_id != "unknown" else None,
                    "metadata": {
                        "created_date": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "acquisition_method": "api",
                        "original_points": points
                    }
                }
                
                problems.append(problem)
                
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1}/{len(raw_problems)} problems...")
                    
            except Exception as e:
                print(f"Error processing problem {i}: {e}")
                continue
        
        print(f"Successfully processed {len(problems)} problems")
        return problems
    
    def save_processed_problems(self, problems: List[Dict[str, Any]], output_file: Path):
        """Save processed problems to JSON file"""
        print(f"Saving {len(problems)} problems to {output_file}...")
        
        # Create summary statistics
        summary = self._create_processing_summary(problems)
        
        output_data = {
            "processing_date": datetime.now().isoformat(),
            "source": "codeforces_api",
            "total_problems": len(problems),
            "summary": summary,
            "problems": problems
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved processed data to {output_file}")
        
        # Save summary separately
        summary_file = output_file.parent / f"{output_file.stem}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved summary to {summary_file}")
        return summary
    
    def _create_processing_summary(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary statistics for processed problems"""
        summary = {
            "total_problems": len(problems),
            "by_difficulty": {},
            "by_rating_range": {},
            "top_tags": {},
            "google_relevant": 0,
            "google_relevance_distribution": {},
            "rating_distribution": {
                "rated": 0,
                "unrated": 0,
                "avg_rating": 0,
                "min_rating": None,
                "max_rating": None
            }
        }
        
        ratings = []
        tag_counts = {}
        google_scores = []
        
        for problem in problems:
            # Difficulty distribution
            diff_level = problem["difficulty"]["level"]
            summary["by_difficulty"][diff_level] = summary["by_difficulty"].get(diff_level, 0) + 1
            
            # Rating distribution
            rating = problem["difficulty"]["rating"]
            if rating:
                ratings.append(rating)
                summary["rating_distribution"]["rated"] += 1
                rating_range = f"{(rating // 200) * 200}-{((rating // 200) + 1) * 200 - 1}"
                summary["by_rating_range"][rating_range] = summary["by_rating_range"].get(rating_range, 0) + 1
            else:
                summary["rating_distribution"]["unrated"] += 1
            
            # Tag frequency
            for tag in problem["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Google relevance
            google_score = problem["google_relevance_score"]
            google_scores.append(google_score)
            
            if "google" in problem["company_tags"]:
                summary["google_relevant"] += 1
            
            # Google score distribution
            score_range = f"{int(google_score)}-{int(google_score)+1}"
            summary["google_relevance_distribution"][score_range] = summary["google_relevance_distribution"].get(score_range, 0) + 1
        
        # Calculate rating statistics
        if ratings:
            summary["rating_distribution"]["avg_rating"] = round(sum(ratings) / len(ratings), 1)
            summary["rating_distribution"]["min_rating"] = min(ratings)
            summary["rating_distribution"]["max_rating"] = max(ratings)
        
        # Google score statistics
        if google_scores:
            summary["google_relevance_stats"] = {
                "avg_score": round(sum(google_scores) / len(google_scores), 2),
                "min_score": round(min(google_scores), 2),
                "max_score": round(max(google_scores), 2),
                "high_relevance_count": sum(1 for score in google_scores if score >= 7.0)
            }
        
        # Top 20 tags
        summary["top_tags"] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return summary
    
    def create_filtered_exports(self, problems: List[Dict[str, Any]]):
        """Create filtered datasets for specific use cases"""
        exports_dir = self.data_dir / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Google-tagged problems
        google_problems = [p for p in problems if "google" in p["company_tags"]]
        google_file = exports_dir / "google_tagged_problems.json"
        with open(google_file, 'w', encoding='utf-8') as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "description": "Problems tagged as Google-relevant based on algorithmic analysis",
                "count": len(google_problems),
                "problems": google_problems
            }, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(google_problems)} Google-relevant problems to {google_file}")
        
        # Interview practice set (medium difficulty, high relevance)
        practice_problems = [
            p for p in problems 
            if p["difficulty"]["level"] == "medium" 
            and p["google_relevance_score"] >= 5.0
            and p["difficulty"]["rating"] is not None
            and 1200 <= p["difficulty"]["rating"] <= 2000
        ]
        practice_file = exports_dir / "interview_practice_set.json"
        with open(practice_file, 'w', encoding='utf-8') as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "description": "Curated interview practice problems (medium difficulty, high relevance)",
                "selection_criteria": {
                    "difficulty": "medium",
                    "min_google_relevance": 5.0,
                    "rating_range": "1200-2000"
                },
                "count": len(practice_problems),
                "problems": practice_problems
            }, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(practice_problems)} practice problems to {practice_file}")
        
        # Easy starter problems
        easy_problems = [
            p for p in problems 
            if p["difficulty"]["level"] == "easy"
            and p["google_relevance_score"] >= 4.0
            and len(p["tags"]) >= 2
        ][:200]  # Limit to 200 for starter set
        easy_file = exports_dir / "easy_starter_problems.json"
        with open(easy_file, 'w', encoding='utf-8') as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "description": "Easy problems for getting started with algorithmic practice",
                "selection_criteria": {
                    "difficulty": "easy",
                    "min_google_relevance": 4.0,
                    "min_tags": 2
                },
                "count": len(easy_problems),
                "problems": easy_problems
            }, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(easy_problems)} easy starter problems to {easy_file}")


def main():
    """Main processing function"""
    print("DSATrain Simple Data Processing Pipeline")
    print("=" * 50)
    
    # Setup paths
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    # Initialize processor
    processor = SimpleCodeforcesProcessor(data_dir)
    
    # Find raw Codeforces data
    raw_file = data_dir / "raw" / "codeforces" / "problems" / "problems_simple.json"
    
    if not raw_file.exists():
        print(f"Error: Raw data file not found: {raw_file}")
        print("Please run the data collection script first.")
        return
    
    try:
        # Process problems
        problems = processor.process_raw_problems(raw_file)
        
        # Save processed problems
        output_file = data_dir / "processed" / "codeforces_problems_processed.json"
        summary = processor.save_processed_problems(problems, output_file)
        
        # Create filtered exports
        processor.create_filtered_exports(problems)
        
        print("\n" + "=" * 50)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Input file: {raw_file}")
        print(f"Output file: {output_file}")
        print(f"Problems processed: {len(problems)}")
        print(f"Google-relevant problems: {summary['google_relevant']}")
        
        print("\nDifficulty distribution:")
        for level, count in summary["by_difficulty"].items():
            percentage = (count / len(problems)) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
        
        print(f"\nTop 10 tags:")
        for tag, count in list(summary["top_tags"].items())[:10]:
            print(f"  {tag}: {count}")
        
        if "google_relevance_stats" in summary:
            gr_stats = summary["google_relevance_stats"]
            print(f"\nGoogle Relevance Statistics:")
            print(f"  Average score: {gr_stats['avg_score']}")
            print(f"  High relevance (≥7.0): {gr_stats['high_relevance_count']}")
            print(f"  Tagged as Google: {summary['google_relevant']}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
