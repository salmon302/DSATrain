"""
Data Import Service
Imports processed data from the data framework into the database
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.database import (
    DatabaseConfig, Problem, Solution, get_database_stats
)
from models.ai_features_models import (
    ProblemEmbedding, ProblemDifficultyVector, ConceptNode, 
    ConceptPrerequisite, ProblemConceptMapping, GoogleInterviewFeatures,
    ProblemQualityScore, BehavioralCompetency, BehavioralQuestion,
    ConversationTemplate, DataPipelineStatus
)


class DataImportService:
    """Service for importing processed data into database"""
    
    def __init__(self, data_dir: Path, db_config: DatabaseConfig):
        self.data_dir = data_dir
        self.db_config = db_config
        self.processed_dir = data_dir / "processed"
        
    def import_unified_problems(self, session: Session) -> Dict[str, Any]:
        """Import unified problems into database"""
        print("=== Importing Unified Problems ===")
        
        problems_file = self.processed_dir / "problems_unified_complete.json"
        if not problems_file.exists():
            return {"status": "failed", "error": "Unified problems file not found"}
        
        try:
            with problems_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            problems = data.get("problems", [])
            imported_count = 0
            updated_count = 0
            
            for problem_data in problems:
                problem_id = problem_data.get("id")
                if not problem_id:
                    continue
                
                # Check if problem exists
                existing = session.query(Problem).filter(Problem.id == problem_id).first()
                
                if existing:
                    # Update existing problem
                    self._update_problem_from_unified_data(existing, problem_data)
                    updated_count += 1
                else:
                    # Create new problem
                    problem = self._create_problem_from_unified_data(problem_data)
                    session.add(problem)
                    imported_count += 1
            
            session.commit()
            
            result = {
                "status": "success",
                "imported": imported_count,
                "updated": updated_count,
                "total_processed": len(problems)
            }
            
            print(f"✅ Imported {imported_count} new problems, updated {updated_count}")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to import problems: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _create_problem_from_unified_data(self, data: Dict[str, Any]) -> Problem:
        """Create Problem instance from unified data"""
        return Problem(
            id=data.get("id"),
            platform=data.get("source", "unknown"),
            platform_id=data.get("original_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", {}).get("level", "medium"),
            difficulty_rating=float(data.get("difficulty", {}).get("rating", 1500)),
            algorithm_tags=data.get("unified_tags", []),
            company_tags=data.get("company_tags", []),
            google_interview_relevance=float(data.get("google_relevance", 0.0)),
            quality_score=float(data.get("quality_scores", {}).get("overall", 0.0)),
            constraints=data.get("constraints", {}),
            created_at=datetime.now(),
            collected_at=datetime.now()
        )
    
    def _update_problem_from_unified_data(self, problem: Problem, data: Dict[str, Any]):
        """Update existing problem with unified data"""
        problem.title = data.get("title", problem.title)
        problem.description = data.get("description", problem.description)
        problem.difficulty = data.get("difficulty", {}).get("level", problem.difficulty)
        problem.difficulty_rating = float(data.get("difficulty", {}).get("rating", problem.difficulty_rating))
        problem.algorithm_tags = data.get("unified_tags", problem.algorithm_tags)
        problem.company_tags = data.get("company_tags", problem.company_tags)
        problem.google_interview_relevance = float(data.get("google_relevance", problem.google_interview_relevance))
        problem.quality_score = float(data.get("quality_scores", {}).get("overall", problem.quality_score))
        problem.updated_at = datetime.now()
    
    def import_problem_embeddings(self, session: Session) -> Dict[str, Any]:
        """Import semantic embeddings into database"""
        print("=== Importing Problem Embeddings ===")
        
        embeddings_file = self.processed_dir / "ai_features" / "semantic_embeddings.json"
        if not embeddings_file.exists():
            return {"status": "failed", "error": "Embeddings file not found"}
        
        try:
            with embeddings_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            embeddings = data.get("embeddings", {})
            imported_count = 0
            
            for problem_id, embedding_data in embeddings.items():
                # Check if problem exists
                problem = session.query(Problem).filter(Problem.id == problem_id).first()
                if not problem:
                    continue
                
                # Check if embedding already exists
                existing = session.query(ProblemEmbedding).filter(
                    ProblemEmbedding.problem_id == problem_id
                ).first()
                
                if existing:
                    # Update existing embedding
                    existing.title_embedding = embedding_data.get("title_embedding", [])
                    existing.description_embedding = embedding_data.get("desc_embedding", [])
                    existing.combined_embedding = embedding_data.get("embedding", [])
                    existing.updated_at = datetime.now()
                else:
                    # Create new embedding
                    embedding = ProblemEmbedding(
                        problem_id=problem_id,
                        title_embedding=embedding_data.get("title_embedding", []),
                        description_embedding=embedding_data.get("desc_embedding", []),
                        combined_embedding=embedding_data.get("embedding", []),
                        embedding_model="dsatrain_v1",
                        embedding_dimension=len(embedding_data.get("embedding", [])),
                        embedding_quality_score=0.8
                    )
                    session.add(embedding)
                
                imported_count += 1
            
            session.commit()
            
            result = {
                "status": "success",
                "imported": imported_count,
                "total_embeddings": len(embeddings)
            }
            
            print(f"✅ Imported {imported_count} problem embeddings")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to import embeddings: {e}")
            return {"status": "failed", "error": str(e)}
    
    def import_difficulty_vectors(self, session: Session) -> Dict[str, Any]:
        """Import difficulty vectors into database"""
        print("=== Importing Difficulty Vectors ===")
        
        vectors_file = self.processed_dir / "ai_features" / "difficulty_vectors.json"
        if not vectors_file.exists():
            return {"status": "failed", "error": "Difficulty vectors file not found"}
        
        try:
            with vectors_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            vectors = data.get("vectors", {})
            imported_count = 0
            
            for problem_id, vector_data in vectors.items():
                # Check if problem exists
                problem = session.query(Problem).filter(Problem.id == problem_id).first()
                if not problem:
                    continue
                
                vector = vector_data.get("vector", [])
                if len(vector) < 5:
                    continue
                
                # Check if vector already exists
                existing = session.query(ProblemDifficultyVector).filter(
                    ProblemDifficultyVector.problem_id == problem_id
                ).first()
                
                if existing:
                    # Update existing vector
                    existing.algorithmic_complexity = vector[0]
                    existing.implementation_difficulty = vector[1]
                    existing.mathematical_content = vector[2]
                    existing.data_structure_usage = vector[3]
                    existing.optimization_required = vector[4]
                    existing.overall_difficulty = vector_data.get("overall_difficulty", sum(vector) / len(vector))
                    existing.updated_at = datetime.now()
                else:
                    # Create new vector
                    difficulty_vector = ProblemDifficultyVector(
                        problem_id=problem_id,
                        algorithmic_complexity=vector[0],
                        implementation_difficulty=vector[1],
                        mathematical_content=vector[2],
                        data_structure_usage=vector[3],
                        optimization_required=vector[4],
                        overall_difficulty=vector_data.get("overall_difficulty", sum(vector) / len(vector)),
                        difficulty_confidence=0.8
                    )
                    session.add(difficulty_vector)
                
                imported_count += 1
            
            session.commit()
            
            result = {
                "status": "success",
                "imported": imported_count,
                "total_vectors": len(vectors)
            }
            
            print(f"✅ Imported {imported_count} difficulty vectors")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to import difficulty vectors: {e}")
            return {"status": "failed", "error": str(e)}
    
    def import_concept_graph(self, session: Session) -> Dict[str, Any]:
        """Import concept graph into database"""
        print("=== Importing Concept Graph ===")
        
        graph_file = self.processed_dir / "ai_features" / "concept_graph.json"
        if not graph_file.exists():
            return {"status": "failed", "error": "Concept graph file not found"}
        
        try:
            with graph_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            graph = data.get("graph", {})
            nodes = graph.get("nodes", {})
            edges = graph.get("edges", [])
            
            concepts_imported = 0
            prerequisites_imported = 0
            
            # Import concept nodes
            for concept_id, node_data in nodes.items():
                existing = session.query(ConceptNode).filter(ConceptNode.id == concept_id).first()
                
                if existing:
                    # Update existing
                    existing.name = concept_id.replace("_", " ").title()
                    existing.difficulty_level = node_data.get("difficulty_level", 1)
                    existing.problem_count = node_data.get("problem_count", 0)
                    existing.updated_at = datetime.now()
                else:
                    # Create new
                    concept = ConceptNode(
                        id=concept_id,
                        name=concept_id.replace("_", " ").title(),
                        difficulty_level=node_data.get("difficulty_level", 1),
                        problem_count=node_data.get("problem_count", 0)
                    )
                    session.add(concept)
                
                concepts_imported += 1
            
            session.commit()
            
            # Import prerequisite relationships
            for edge in edges:
                from_concept = edge.get("from")
                to_concept = edge.get("to")
                
                if not from_concept or not to_concept:
                    continue
                
                # Check if relationship exists
                existing = session.query(ConceptPrerequisite).filter(
                    ConceptPrerequisite.concept_id == to_concept,
                    ConceptPrerequisite.prerequisite_id == from_concept
                ).first()
                
                if not existing:
                    prerequisite = ConceptPrerequisite(
                        concept_id=to_concept,
                        prerequisite_id=from_concept,
                        importance=1.0
                    )
                    session.add(prerequisite)
                    prerequisites_imported += 1
            
            session.commit()
            
            result = {
                "status": "success",
                "concepts_imported": concepts_imported,
                "prerequisites_imported": prerequisites_imported
            }
            
            print(f"✅ Imported {concepts_imported} concepts and {prerequisites_imported} prerequisites")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to import concept graph: {e}")
            return {"status": "failed", "error": str(e)}
    
    def import_quality_scores(self, session: Session) -> Dict[str, Any]:
        """Import quality scores into database"""
        print("=== Importing Quality Scores ===")
        
        scores_file = self.processed_dir / "quality_scoring" / "quality_scores.json"
        if not scores_file.exists():
            return {"status": "failed", "error": "Quality scores file not found"}
        
        try:
            with scores_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            scores = data.get("scores", {})
            imported_count = 0
            
            for problem_id, score_data in scores.items():
                # Check if problem exists
                problem = session.query(Problem).filter(Problem.id == problem_id).first()
                if not problem:
                    continue
                
                content_quality = score_data.get("content_quality", {})
                google_relevance = score_data.get("google_relevance", {})
                
                # Check if scores already exist
                existing = session.query(ProblemQualityScore).filter(
                    ProblemQualityScore.problem_id == problem_id
                ).first()
                
                if existing:
                    # Update existing scores
                    self._update_quality_scores(existing, content_quality, google_relevance, score_data)
                else:
                    # Create new scores
                    quality_score = ProblemQualityScore(
                        problem_id=problem_id,
                        completeness_score=content_quality.get("completeness", 0.0),
                        clarity_score=content_quality.get("clarity", 0.0),
                        specificity_score=content_quality.get("specificity", 0.0),
                        educational_value_score=content_quality.get("educational_value", 0.0),
                        content_quality_overall=content_quality.get("overall", 0.0),
                        topic_relevance=google_relevance.get("topic_relevance", 0.0),
                        difficulty_appropriateness=google_relevance.get("difficulty_appropriateness", 0.0),
                        frequency_score=google_relevance.get("frequency_score", 0.0),
                        company_alignment=google_relevance.get("company_alignment", 0.0),
                        google_relevance_overall=google_relevance.get("overall_relevance", 0.0),
                        overall_quality_score=score_data.get("overall_score", 0.0),
                        recommendation=score_data.get("recommendation", "not_recommended")
                    )
                    session.add(quality_score)
                
                imported_count += 1
            
            session.commit()
            
            result = {
                "status": "success",
                "imported": imported_count,
                "total_scores": len(scores)
            }
            
            print(f"✅ Imported {imported_count} quality scores")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to import quality scores: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _update_quality_scores(self, existing, content_quality, google_relevance, score_data):
        """Update existing quality scores"""
        existing.completeness_score = content_quality.get("completeness", existing.completeness_score)
        existing.clarity_score = content_quality.get("clarity", existing.clarity_score)
        existing.specificity_score = content_quality.get("specificity", existing.specificity_score)
        existing.educational_value_score = content_quality.get("educational_value", existing.educational_value_score)
        existing.content_quality_overall = content_quality.get("overall", existing.content_quality_overall)
        existing.topic_relevance = google_relevance.get("topic_relevance", existing.topic_relevance)
        existing.difficulty_appropriateness = google_relevance.get("difficulty_appropriateness", existing.difficulty_appropriateness)
        existing.frequency_score = google_relevance.get("frequency_score", existing.frequency_score)
        existing.company_alignment = google_relevance.get("company_alignment", existing.company_alignment)
        existing.google_relevance_overall = google_relevance.get("overall_relevance", existing.google_relevance_overall)
        existing.overall_quality_score = score_data.get("overall_score", existing.overall_quality_score)
        existing.recommendation = score_data.get("recommendation", existing.recommendation)
        existing.updated_at = datetime.now()
    
    def run_complete_import(self) -> Dict[str, Any]:
        """Run complete data import pipeline"""
        print("=== Running Complete Data Import ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "import_status": "running",
            "components": {}
        }
        
        session = self.db_config.get_session()
        
        try:
            # 1. Import unified problems
            problems_result = self.import_unified_problems(session)
            results["components"]["unified_problems"] = problems_result
            
            # 2. Import embeddings
            embeddings_result = self.import_problem_embeddings(session)
            results["components"]["embeddings"] = embeddings_result
            
            # 3. Import difficulty vectors
            vectors_result = self.import_difficulty_vectors(session)
            results["components"]["difficulty_vectors"] = vectors_result
            
            # 4. Import concept graph
            graph_result = self.import_concept_graph(session)
            results["components"]["concept_graph"] = graph_result
            
            # 5. Import quality scores
            scores_result = self.import_quality_scores(session)
            results["components"]["quality_scores"] = scores_result
            
            # Update pipeline status
            self._update_pipeline_status(session, results)
            
            # Check overall success
            all_successful = all(
                comp.get("status") == "success" 
                for comp in results["components"].values()
            )
            
            results["import_status"] = "success" if all_successful else "partial_success"
            
            # Get final stats
            final_stats = get_database_stats(session)
            results["final_database_stats"] = final_stats
            
            print(f"\n✅ Data import complete!")
            print(f"Database now contains:")
            for table, count in final_stats.items():
                if count > 0:
                    print(f"  {table}: {count}")
            
            return results
            
        except Exception as e:
            session.rollback()
            results["import_status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Import failed: {e}")
            return results
            
        finally:
            session.close()
    
    def _update_pipeline_status(self, session: Session, results: Dict[str, Any]):
        """Update pipeline status in database"""
        try:
            status = DataPipelineStatus(
                pipeline_component="data_import",
                status="healthy" if results["import_status"] == "success" else "degraded",
                total_records=sum(
                    comp.get("total_processed", comp.get("total_embeddings", comp.get("total_scores", 0)))
                    for comp in results["components"].values()
                ),
                processed_records=sum(
                    comp.get("imported", 0)
                    for comp in results["components"].values()
                ),
                quality_score=1.0 if results["import_status"] == "success" else 0.5,
                status_message="Data import completed successfully" if results["import_status"] == "success" else "Partial import failure",
                pipeline_version="v1.0"
            )
            session.add(status)
            session.commit()
        except Exception as e:
            print(f"Warning: Could not update pipeline status: {e}")


def main():
    """Main function for running data import"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Initialize database
    db_config = DatabaseConfig()
    
    # Create AI features tables
    try:
        from ..models.ai_features_models import Base
        Base.metadata.create_all(bind=db_config.engine)
        print("✅ Created AI features tables")
    except Exception as e:
        print(f"Warning: Could not create AI features tables: {e}")
    
    # Create import service
    import_service = DataImportService(data_dir, db_config)
    
    # Run import
    results = import_service.run_complete_import()
    
    if results["import_status"] == "success":
        print("\n🎉 Complete data import successful!")
    else:
        print(f"\n⚠️  Import completed with status: {results['import_status']}")
    
    return results


if __name__ == "__main__":
    main()
