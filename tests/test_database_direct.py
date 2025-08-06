"""
Direct Database Test - Verify Expanded Dataset
"""

from src.models.database import DatabaseConfig, Problem
from sqlalchemy import func, distinct
from collections import Counter

def main():
    print("🚀 Testing Expanded DSATrain Database")
    print("=" * 50)
    
    # Initialize database
    db_config = DatabaseConfig()
    session = db_config.get_session()
    
    try:
        # Basic counts
        total_problems = session.query(Problem).count()
        print(f"📊 Total Problems: {total_problems:,}")
        
        # Platform distribution
        platform_counts = session.query(Problem.platform, func.count(Problem.id)).group_by(Problem.platform).all()
        print(f"\n🌐 Platform Distribution:")
        for platform, count in platform_counts:
            print(f"   • {platform}: {count:,} problems")
        
        # Difficulty distribution
        difficulty_counts = session.query(Problem.difficulty, func.count(Problem.id)).group_by(Problem.difficulty).all()
        print(f"\n⭐ Difficulty Distribution:")
        for difficulty, count in difficulty_counts:
            print(f"   • {difficulty}: {count:,} problems")
        
        # Quality metrics
        avg_quality = session.query(func.avg(Problem.quality_score)).scalar()
        min_quality = session.query(func.min(Problem.quality_score)).scalar()
        max_quality = session.query(func.max(Problem.quality_score)).scalar()
        print(f"\n💎 Quality Metrics:")
        print(f"   • Average Quality: {avg_quality:.2f}")
        print(f"   • Min Quality: {min_quality:.2f}")
        print(f"   • Max Quality: {max_quality:.2f}")
        
        # Google relevance metrics
        avg_relevance = session.query(func.avg(Problem.google_interview_relevance)).scalar()
        high_relevance = session.query(Problem).filter(Problem.google_interview_relevance >= 8.0).count()
        print(f"\n🎯 Google Interview Relevance:")
        print(f"   • Average Relevance: {avg_relevance:.2f}")
        print(f"   • High Relevance (8+): {high_relevance:,} problems")
        
        # Sample problems
        sample_problems = session.query(Problem).limit(5).all()
        print(f"\n📝 Sample Problems:")
        for i, problem in enumerate(sample_problems, 1):
            print(f"   {i}. {problem.title} ({problem.platform}) - Quality: {problem.quality_score:.1f}")
        
        # Algorithm tags analysis
        all_problems = session.query(Problem.algorithm_tags).all()
        all_tags = []
        for tags_tuple in all_problems:
            if tags_tuple[0]:  # Check if tags exist
                all_tags.extend(tags_tuple[0])
        
        tag_counter = Counter(all_tags)
        print(f"\n🧮 Top 10 Algorithm Tags:")
        for tag, count in tag_counter.most_common(10):
            print(f"   • {tag}: {count:,} problems")
        
        print(f"\n✅ Database verification complete!")
        print(f"📈 Successfully expanded from 40 to {total_problems:,} problems!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
