"""
Main data collection script for DSATrain Platform
Implements Phase 1 of Technical_Coding_Data_Strategy.md

This script orchestrates the collection of data from multiple sources:
1. Codeforces API (Priority 1.1)
2. Kaggle LeetCode datasets (Priority 1.2) 
3. HackerRank Interview Kit (Priority 1.3)
4. Academic datasets (Priority 1.4)
"""

import asyncio
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from config import *
from collectors.codeforces_client import CodeforcesAPIClient


async def collect_codeforces_data():
    """
    Priority 1.1: Collect data from Codeforces API
    """
    print("=" * 60)
    print("PHASE 1.1: CODEFORCES API COLLECTION")
    print("=" * 60)
    
    try:
        client = CodeforcesAPIClient(DATA_DIR)
        problems = await client.collect_all_problems()
        await client.save_problems_to_files(problems)
        
        return {
            "success": True,
            "problems_collected": len(problems),
            "source": "codeforces_api"
        }
        
    except Exception as e:
        print(f"Error collecting Codeforces data: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "source": "codeforces_api"
        }


def collect_kaggle_leetcode_data():
    """
    Priority 1.2: Process Kaggle LeetCode datasets
    Note: This function creates placeholder structure.
    Manual download of Kaggle datasets required.
    """
    print("=" * 60)
    print("PHASE 1.2: KAGGLE LEETCODE DATASETS")
    print("=" * 60)
    
    # Create instruction file for manual dataset download
    instructions = {
        "title": "Kaggle LeetCode Dataset Collection Instructions",
        "datasets_to_download": [
            {
                "name": "LeetCode Problems Dataset",
                "url": "https://www.kaggle.com/datasets/leetcode/leetcode-problems",
                "files_needed": ["problems.csv", "solutions.csv"],
                "destination": str(LEETCODE_RAW_DIR)
            },
            {
                "name": "LeetCode Solutions with Companies",
                "url": "https://www.kaggle.com/datasets/datafiniti/leetcode-problems-and-solutions",
                "files_needed": ["leetcode_problems.csv", "leetcode_solutions.csv"],
                "destination": str(LEETCODE_RAW_DIR)
            }
        ],
        "instructions": [
            "1. Visit the Kaggle URLs above",
            "2. Download the datasets (requires Kaggle account)",
            "3. Extract CSV files to the destination directories",
            "4. Run the collection script again to process the files",
            "5. The processor will automatically detect and process available files"
        ],
        "status": "manual_download_required",
        "created": datetime.now().isoformat()
    }
    
    instructions_file = LEETCODE_RAW_DIR / "download_instructions.json"
    LEETCODE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(instructions_file, 'w', encoding='utf-8') as f:
        json.dump(instructions, f, indent=JSON_INDENT, ensure_ascii=False)
    
    print(f"Created download instructions: {instructions_file}")
    print("Manual download of Kaggle datasets is required.")
    print("Please follow the instructions in the JSON file.")
    
    return {
        "success": True,
        "action": "instructions_created",
        "source": "kaggle_leetcode",
        "instructions_file": str(instructions_file)
    }


def collect_hackerrank_data():
    """
    Priority 1.3: Collect HackerRank Interview Preparation Kit
    Note: This creates a structure for future implementation
    """
    print("=" * 60)
    print("PHASE 1.3: HACKERRANK INTERVIEW KIT")
    print("=" * 60)
    
    # Create placeholder structure for HackerRank data
    hackerrank_structure = {
        "title": "HackerRank Interview Preparation Kit Collection",
        "target_url": "https://www.hackerrank.com/interview/interview-preparation-kit",
        "topics": [
            "Arrays", "Linked Lists", "Trees", "Balanced Trees", "Stacks and Queues",
            "Heap", "Dynamic Programming", "Recursion and Backtracking", "Graphs",
            "Greedy Algorithms", "Search", "Sorting", "String Manipulation", "Miscellaneous"
        ],
        "collection_method": "web_scraping_required",
        "estimated_problems": 100,
        "status": "implementation_pending",
        "created": datetime.now().isoformat()
    }
    
    HACKERRANK_RAW_DIR.mkdir(parents=True, exist_ok=True)
    structure_file = HACKERRANK_RAW_DIR / "collection_plan.json"
    
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(hackerrank_structure, f, indent=JSON_INDENT, ensure_ascii=False)
    
    print(f"Created HackerRank collection plan: {structure_file}")
    print("Web scraping implementation required for full collection.")
    
    return {
        "success": True,
        "action": "plan_created",
        "source": "hackerrank",
        "plan_file": str(structure_file)
    }


def collect_academic_datasets():
    """
    Priority 1.4: Set up academic datasets collection
    """
    print("=" * 60)
    print("PHASE 1.4: ACADEMIC DATASETS")
    print("=" * 60)
    
    # Create structure for academic datasets
    academic_info = {
        "title": "Academic Code Quality Datasets Collection",
        "datasets": [
            {
                "name": "CodeComplex Dataset",
                "description": "4,900 Java + 4,900 Python solutions with complexity annotations",
                "source": "Research paper with dataset links",
                "labels": "Time complexity classes (O(1) to exponential)",
                "format": "CSV/JSON with code and complexity labels",
                "status": "research_required"
            },
            {
                "name": "Hugging Face py_ast",
                "description": "150,000 Python AST trees",
                "source": "Hugging Face datasets",
                "access": "huggingface.co/datasets",
                "status": "api_available"
            },
            {
                "name": "ml4code-dataset (CUHK-ARISE)",
                "description": "Index of multiple code datasets",
                "source": "Academic research collections",
                "access": "GitHub repositories",
                "status": "catalog_available"
            }
        ],
        "collection_priority": "after_primary_sources",
        "legal_status": "academic_research_permitted",
        "created": datetime.now().isoformat()
    }
    
    ACADEMIC_RAW_DIR.mkdir(parents=True, exist_ok=True)
    info_file = ACADEMIC_RAW_DIR / "datasets_info.json"
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(academic_info, f, indent=JSON_INDENT, ensure_ascii=False)
    
    print(f"Created academic datasets info: {info_file}")
    print("Academic dataset collection requires research and API integration.")
    
    return {
        "success": True,
        "action": "info_created",
        "source": "academic_datasets",
        "info_file": str(info_file)
    }


def create_collection_summary(results):
    """
    Create a summary of the collection process
    """
    summary = {
        "collection_date": datetime.now().isoformat(),
        "phase": "Phase 1 - Accessible Datasets",
        "results": results,
        "statistics": {
            "successful_sources": sum(1 for r in results if r.get("success", False)),
            "total_sources": len(results),
            "total_problems_collected": sum(r.get("problems_collected", 0) for r in results)
        },
        "next_steps": [
            "Download Kaggle LeetCode datasets manually",
            "Implement HackerRank web scraping",
            "Research and integrate academic datasets",
            "Process collected data through standardization pipeline",
            "Implement data quality assessment",
            "Create unified database schema"
        ]
    }
    
    summary_file = DATA_DIR / "collection_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=JSON_INDENT, ensure_ascii=False)
    
    return summary_file


async def main():
    """
    Main collection orchestrator
    """
    print("DSATrain Data Collection - Phase 1")
    print(f"Starting collection at: {datetime.now()}")
    print(f"Data directory: {DATA_DIR}")
    print()
    
    # Ensure all directories exist
    for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ENRICHED_DATA_DIR, EXPORTS_DATA_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    try:
        # Phase 1.1: Codeforces API (Highest Priority)
        codeforces_result = await collect_codeforces_data()
        results.append(codeforces_result)
        
        # Phase 1.2: Kaggle LeetCode datasets
        leetcode_result = collect_kaggle_leetcode_data()
        results.append(leetcode_result)
        
        # Phase 1.3: HackerRank Interview Kit
        hackerrank_result = collect_hackerrank_data()
        results.append(hackerrank_result)
        
        # Phase 1.4: Academic datasets
        academic_result = collect_academic_datasets()
        results.append(academic_result)
        
        # Create summary
        summary_file = create_collection_summary(results)
        
        print("=" * 60)
        print("COLLECTION COMPLETED")
        print("=" * 60)
        print(f"Summary saved to: {summary_file}")
        
        # Print results
        for result in results:
            source = result.get("source", "unknown")
            success = result.get("success", False)
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{source}: {status}")
            
            if "problems_collected" in result:
                print(f"  Problems collected: {result['problems_collected']}")
            if "error" in result:
                print(f"  Error: {result['error']}")
            if "action" in result:
                print(f"  Action: {result['action']}")
        
        total_problems = sum(r.get("problems_collected", 0) for r in results)
        print(f"\nTotal problems collected: {total_problems}")
        
        if total_problems > 0:
            print("\n🎉 Phase 1 collection partially successful!")
            print("Next: Process collected data and implement remaining collectors.")
        else:
            print("\n⚠️  No problems collected automatically.")
            print("Manual steps required - check instructions files created.")
    
    except Exception as e:
        print(f"Fatal error in collection process: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run the collection process
    asyncio.run(main())
