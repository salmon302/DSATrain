"""
Data Processing Pipeline for DSATrain Platform
Converts raw data from various sources into standardized schemas
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.schemas import (
    Problem, Solution, Difficulty, DifficultyLevel, SourcePlatform,
    ProblemMetadata, AcquisitionMethod, TestCase, Constraints,
    ProgrammingLanguage, SolutionType
)


class CodeforcesProcessor:
    """
    Process raw Codeforces data into standardized format
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw" / "codeforces"
        self.processed_dir = data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def _convert_rating_to_difficulty(self, rating: Optional[int]) -> DifficultyLevel:
        """Convert Codeforces rating to difficulty level"""
        if rating is None:
            return DifficultyLevel.MEDIUM
        
        if rating <= 1200:
            return DifficultyLevel.EASY
        elif rating <= 2000:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
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
    
    def process_raw_problems(self, input_file: Path) -> List[Problem]:
        """
        Process raw Codeforces problems into standardized format
        """
        print(f"Processing {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        problems = []
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
                
                # Create difficulty
                difficulty = Difficulty(
                    level=self._convert_rating_to_difficulty(rating),
                    rating=rating,
                    source_scale="codeforces_rating"
                )
                
                # Create constraints (basic info from points/rating)
                constraints = None
                if points or rating:
                    time_limit = "2000ms"  # Default for most CF problems
                    memory_limit = "256MB"  # Default for most CF problems
                    constraints = Constraints(
                        time_limit=time_limit,
                        memory_limit=memory_limit,
                        input_size=f"Based on {rating} rating" if rating else "Standard"
                    )
                
                # Create source URL
                source_url = None
                if contest_id != "unknown":
                    source_url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"
                
                # Calculate Google relevance
                google_score = self._calculate_google_relevance_score(tags, rating)
                company_tags = ["google"] if google_score >= 7.0 else []
                
                # Create metadata
                metadata = ProblemMetadata(
                    created_date=datetime.now(),
                    last_updated=datetime.now(),
                    source_url=source_url,
                    acquisition_method=AcquisitionMethod.API
                )
                
                # Create problem
                problem = Problem(
                    id=problem_id,
                    source=SourcePlatform.CODEFORCES,
                    title=title,
                    description=f"Problem: {title}\nTags: {', '.join(tags)}\nRating: {rating or 'Unrated'}",
                    difficulty=difficulty,
                    tags=tags,
                    company_tags=company_tags,
                    constraints=constraints,
                    test_cases=[],  # Would need separate scraping
                    editorial=None,  # Would need separate scraping
                    metadata=metadata
                )
                
                problems.append(problem)
                
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1}/{len(raw_problems)} problems...")
                    
            except Exception as e:
                print(f"Error processing problem {i}: {e}")
                continue
        
        print(f"Successfully processed {len(problems)} problems")
        return problems
    
    def save_processed_problems(self, problems: List[Problem], output_file: Path):
        """Save processed problems to JSON file"""
        print(f"Saving {len(problems)} problems to {output_file}...")
        
        # Convert to dict format
        problems_data = []
        for problem in problems:
            problem_dict = problem.dict()
            # Convert datetime objects to strings
            problem_dict["metadata"]["created_date"] = problem.metadata.created_date.isoformat()
            problem_dict["metadata"]["last_updated"] = problem.metadata.last_updated.isoformat()
            problems_data.append(problem_dict)
        
        # Create summary statistics
        summary = self._create_processing_summary(problems)
        
        output_data = {
            "processing_date": datetime.now().isoformat(),
            "source": "codeforces_api",
            "total_problems": len(problems),
            "summary": summary,
            "problems": problems_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved processed data to {output_file}")
        
        # Save summary separately
        summary_file = output_file.parent / f"{output_file.stem}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved summary to {summary_file}")
    
    def _create_processing_summary(self, problems: List[Problem]) -> Dict[str, Any]:
        """Create summary statistics for processed problems"""
        summary = {
            "total_problems": len(problems),
            "by_difficulty": {},
            "by_rating_range": {},
            "top_tags": {},
            "google_relevant": 0,
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
        
        for problem in problems:
            # Difficulty distribution
            diff_level = problem.difficulty.level.value
            summary["by_difficulty"][diff_level] = summary["by_difficulty"].get(diff_level, 0) + 1
            
            # Rating distribution
            rating = problem.difficulty.rating
            if rating:
                ratings.append(rating)
                summary["rating_distribution"]["rated"] += 1
                rating_range = f"{(rating // 200) * 200}-{((rating // 200) + 1) * 200 - 1}"
                summary["by_rating_range"][rating_range] = summary["by_rating_range"].get(rating_range, 0) + 1
            else:
                summary["rating_distribution"]["unrated"] += 1
            
            # Tag frequency
            for tag in problem.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Google relevance
            if "google" in problem.company_tags:
                summary["google_relevant"] += 1
        
        # Calculate rating statistics
        if ratings:
            summary["rating_distribution"]["avg_rating"] = sum(ratings) / len(ratings)
            summary["rating_distribution"]["min_rating"] = min(ratings)
            summary["rating_distribution"]["max_rating"] = max(ratings)
        
        # Top 20 tags
        summary["top_tags"] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return summary


def main():
    """Main processing function"""
    print("DSATrain Data Processing Pipeline")
    print("=" * 50)
    
    # Setup paths
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    # Initialize processor
    processor = CodeforcesProcessor(data_dir)
    
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
        processor.save_processed_problems(problems, output_file)
        
        print("\n" + "=" * 50)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Input file: {raw_file}")
        print(f"Output file: {output_file}")
        print(f"Problems processed: {len(problems)}")
        
        # Show some statistics
        google_relevant = sum(1 for p in problems if "google" in p.company_tags)
        print(f"Google-relevant problems: {google_relevant}")
        
        difficulty_counts = {}
        for p in problems:
            level = p.difficulty.level.value
            difficulty_counts[level] = difficulty_counts.get(level, 0) + 1
        
        print("Difficulty distribution:")
        for level, count in difficulty_counts.items():
            print(f"  {level}: {count}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
