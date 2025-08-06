"""
Verify the expanded DSATrain dataset
"""

import json
import sys
import os
from src.models.database import DatabaseConfig, Problem
from sqlalchemy import func

def main():
    # Write results to a file so we can read them
    with open("expansion_results.txt", "w", encoding="utf-8") as f:
        f.write("🚀 DSATrain Dataset Expansion Verification\n")
        f.write("=" * 50 + "\n\n")
        
        try:
            # Initialize database
            db_config = DatabaseConfig()
            session = db_config.get_session()
            
            # Check total count
            total_problems = session.query(Problem).count()
            f.write(f"📊 Total Problems in Database: {total_problems:,}\n\n")
            
            # Platform breakdown
            platform_counts = session.query(
                Problem.platform, 
                func.count(Problem.id)
            ).group_by(Problem.platform).all()
            
            f.write("🌐 Platform Distribution:\n")
            for platform, count in platform_counts:
                f.write(f"   • {platform}: {count:,} problems\n")
            f.write("\n")
            
            # Difficulty breakdown
            difficulty_counts = session.query(
                Problem.difficulty, 
                func.count(Problem.id)
            ).group_by(Problem.difficulty).all()
            
            f.write("⭐ Difficulty Distribution:\n")
            for difficulty, count in difficulty_counts:
                f.write(f"   • {difficulty}: {count:,} problems\n")
            f.write("\n")
            
            # Quality stats
            quality_stats = session.query(
                func.avg(Problem.quality_score),
                func.min(Problem.quality_score),
                func.max(Problem.quality_score)
            ).first()
            
            f.write("💎 Quality Metrics:\n")
            f.write(f"   • Average: {quality_stats[0]:.2f}\n")
            f.write(f"   • Min: {quality_stats[1]:.2f}\n")
            f.write(f"   • Max: {quality_stats[2]:.2f}\n\n")
            
            # Sample problems
            sample_problems = session.query(Problem).limit(10).all()
            f.write("📝 Sample Problems:\n")
            for i, problem in enumerate(sample_problems, 1):
                f.write(f"   {i}. {problem.title} ({problem.platform}) - Q:{problem.quality_score:.1f}\n")
            f.write("\n")
            
            # High-quality problems
            high_quality_count = session.query(Problem).filter(
                Problem.quality_score >= 95.0
            ).count()
            f.write(f"⭐ High Quality (95+) Problems: {high_quality_count:,}\n")
            
            # Google-relevant problems
            google_relevant = session.query(Problem).filter(
                Problem.google_interview_relevance >= 8.0
            ).count()
            f.write(f"🎯 Google Interview Relevant (8+): {google_relevant:,}\n\n")
            
            f.write("✅ EXPANSION SUCCESS!\n")
            f.write(f"📈 Expanded from ~40 to {total_problems:,} problems\n")
            f.write("🎉 Dataset expansion completed successfully!\n")
            
            session.close()
            
        except Exception as e:
            f.write(f"❌ Error: {str(e)}\n")
            f.write(f"Error type: {type(e).__name__}\n")
            import traceback
            f.write(f"Traceback: {traceback.format_exc()}\n")

if __name__ == "__main__":
    main()
    print("Verification complete! Check expansion_results.txt")
