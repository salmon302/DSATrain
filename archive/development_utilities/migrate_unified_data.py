"""
DSATrain Data Migration Script
Import all problems from unified dataset into Phase 4 database
"""

import json
import sys
from typing import List, Dict, Any
from src.models.database import DatabaseConfig, Problem
from sqlalchemy.orm import Session
from datetime import datetime

def load_unified_problems() -> List[Dict[str, Any]]:
    """Load all problems from the unified dataset"""
    try:
        with open('data/unified/all_problems_unified.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} problems from unified dataset")
        return data
    except Exception as e:
        print(f"❌ Error loading unified data: {e}")
        return []

def convert_problem_to_db_format(problem_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert unified problem format to database schema format"""
    
    # Extract platform from source
    platform = problem_data.get('source', 'unknown')
    if platform == 'unknown':
        # Try to infer from ID
        problem_id = problem_data.get('id', '')
        if problem_id.startswith('cf_'):
            platform = 'codeforces'
        elif problem_id.startswith('lc_'):
            platform = 'leetcode'
        elif problem_id.startswith('hr_'):
            platform = 'hackerrank'
        elif problem_id.startswith('ac_'):
            platform = 'atcoder'
        elif problem_id.startswith('cc_'):
            platform = 'codechef'
    
    # Extract difficulty
    difficulty_info = problem_data.get('difficulty', {})
    if isinstance(difficulty_info, dict):
        difficulty = difficulty_info.get('standardized_level', 'medium')
        difficulty_rating = difficulty_info.get('standardized_rating', 1500)
    else:
        difficulty = str(difficulty_info) if difficulty_info else 'medium'
        difficulty_rating = 1500
    
    # Standardize difficulty levels
    difficulty_mapping = {
        'easy': 'Easy',
        'medium': 'Medium', 
        'hard': 'Hard',
        'beginner': 'Easy',
        'intermediate': 'Medium',
        'advanced': 'Hard',
        'expert': 'Hard'
    }
    difficulty = difficulty_mapping.get(difficulty.lower(), 'Medium')
    
    # Extract algorithm tags
    algorithm_tags = problem_data.get('tags', [])
    if not isinstance(algorithm_tags, list):
        algorithm_tags = []
    
    # Extract company tags
    companies = problem_data.get('company_tags', [])
    if not isinstance(companies, list):
        companies = []
    
    # Calculate quality score based on available metadata
    quality_score = 75.0  # Base score
    
    # Boost quality for problems with more metadata
    if problem_data.get('description'):
        quality_score += 10.0
    if algorithm_tags:
        quality_score += 5.0
    if companies:
        quality_score += 5.0
    if problem_data.get('constraints'):
        quality_score += 5.0
    
    # Platform-based quality adjustments
    platform_quality = {
        'leetcode': 5.0,
        'codeforces': 3.0,
        'hackerrank': 2.0,
        'atcoder': 3.0,
        'codechef': 2.0
    }
    quality_score += platform_quality.get(platform, 0.0)
    
    # Cap at 100
    quality_score = min(quality_score, 100.0)
    
    # Google interview relevance score
    google_relevance = problem_data.get('google_relevance_score', 0)
    if not isinstance(google_relevance, (int, float)):
        google_relevance = 0
    
    # Convert to database format
    db_problem = {
        'id': problem_data.get('id', f"{platform}_{hash(problem_data.get('title', ''))}"),
        'platform': platform,
        'platform_id': str(problem_data.get('id', '')),
        'title': problem_data.get('title', 'Untitled Problem'),
        'difficulty': difficulty,
        'category': algorithm_tags[0] if algorithm_tags else 'general',
        'description': problem_data.get('description', ''),
        'constraints': problem_data.get('constraints', {}),
        'examples': problem_data.get('test_cases', []),
        'hints': [],
        'algorithm_tags': algorithm_tags,
        'data_structures': [],  # Could be extracted from tags later
        'complexity_class': _infer_complexity_class(algorithm_tags),
        'google_interview_relevance': float(google_relevance),
        'difficulty_rating': float(difficulty_rating),
        'quality_score': quality_score,
        'popularity_score': 50.0,  # Default value
        'acceptance_rate': None,
        'frequency_score': None,
        'companies': companies,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'collected_at': datetime.now()
    }
    
    return db_problem

def _infer_complexity_class(tags: List[str]) -> str:
    """Infer complexity class from algorithm tags"""
    if not tags:
        return 'polynomial'
    
    # Check for specific algorithm patterns
    exponential_patterns = ['backtracking', 'brute_force', 'exhaustive_search']
    logarithmic_patterns = ['binary_search', 'divide_and_conquer']
    linear_patterns = ['two_pointers', 'sliding_window', 'greedy']
    
    tags_lower = [tag.lower() for tag in tags]
    
    for pattern in exponential_patterns:
        if any(pattern in tag for tag in tags_lower):
            return 'exponential'
    
    for pattern in logarithmic_patterns:
        if any(pattern in tag for tag in tags_lower):
            return 'logarithmic'
    
    for pattern in linear_patterns:
        if any(pattern in tag for tag in tags_lower):
            return 'linear'
    
    return 'polynomial'

def batch_insert_problems(db_session: Session, problems: List[Dict[str, Any]], batch_size: int = 100):
    """Insert problems in batches for better performance"""
    total_inserted = 0
    total_skipped = 0
    
    for i in range(0, len(problems), batch_size):
        batch = problems[i:i + batch_size]
        batch_inserted = 0
        
        for problem_data in batch:
            try:
                # Check if problem already exists
                existing = db_session.query(Problem).filter(Problem.id == problem_data['id']).first()
                if existing:
                    total_skipped += 1
                    continue
                
                # Create new problem
                problem = Problem(**problem_data)
                db_session.add(problem)
                batch_inserted += 1
                
            except Exception as e:
                print(f"❌ Error inserting problem {problem_data.get('id', 'unknown')}: {e}")
                continue
        
        # Commit batch
        try:
            db_session.commit()
            total_inserted += batch_inserted
            print(f"✅ Inserted batch {i//batch_size + 1}: {batch_inserted} problems (Total: {total_inserted})")
        except Exception as e:
            print(f"❌ Error committing batch {i//batch_size + 1}: {e}")
            db_session.rollback()
    
    return total_inserted, total_skipped

def main():
    """Main migration function"""
    print("🚀 Starting DSATrain Data Migration")
    print("=" * 50)
    
    # Load unified problems
    unified_problems = load_unified_problems()
    if not unified_problems:
        print("❌ No problems to migrate")
        return
    
    print(f"📊 Found {len(unified_problems)} problems to migrate")
    
    # Initialize database
    db_config = DatabaseConfig()
    
    # Ensure tables exist
    try:
        db_config.create_tables()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return
    
    # Convert problems to database format
    print("🔄 Converting problems to database format...")
    db_problems = []
    conversion_errors = 0
    
    for i, problem in enumerate(unified_problems):
        try:
            db_problem = convert_problem_to_db_format(problem)
            db_problems.append(db_problem)
            
            if i % 1000 == 0:
                print(f"   Processed {i}/{len(unified_problems)} problems...")
                
        except Exception as e:
            conversion_errors += 1
            if conversion_errors <= 10:  # Only show first 10 errors
                print(f"❌ Conversion error for problem {i}: {e}")
    
    print(f"✅ Converted {len(db_problems)} problems ({conversion_errors} errors)")
    
    # Insert into database
    print("📥 Inserting problems into database...")
    session = db_config.get_session()
    
    try:
        inserted, skipped = batch_insert_problems(session, db_problems)
        print(f"✅ Migration complete!")
        print(f"   📈 Inserted: {inserted} problems")
        print(f"   ⏭️ Skipped: {skipped} problems (already exist)")
        print(f"   ❌ Errors: {conversion_errors} problems")
        
        # Final statistics
        total_in_db = session.query(Problem).count()
        print(f"   📊 Total problems in database: {total_in_db}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
    finally:
        session.close()
    
    print("=" * 50)
    print("🎉 Migration process completed!")

if __name__ == "__main__":
    main()
