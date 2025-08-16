"""
AI Feature Engineering Pipeline
Creates AI-ready features from unified problem data for machine learning training
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import hashlib
import math


@dataclass
class AIFeatureEngineer:
    """Generates AI-ready features from unified problem data"""
    
    data_dir: Path
    output_dir: Optional[Path] = None
    
    # Feature engineering parameters
    EMBEDDING_DIM = 128
    MAX_VOCAB_SIZE = 10000
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.data_dir / "processed" / "ai_features"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_dir = self.data_dir / "processed"

    def _tokenize_text(self, text: str) -> List[str]:
        """Simple tokenization for text processing"""
        if not text:
            return []
        
        # Convert to lowercase and split on non-alphanumeric characters
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def _build_vocabulary(self, problems: List[Dict[str, Any]]) -> Dict[str, int]:
        """Build vocabulary from all problem text"""
        print("Building vocabulary from problem text...")
        
        word_counts = Counter()
        
        for problem in problems:
            # Tokenize title and description
            title_tokens = self._tokenize_text(problem.get("title", ""))
            desc_tokens = self._tokenize_text(problem.get("description", ""))
            
            # Count words
            word_counts.update(title_tokens)
            word_counts.update(desc_tokens)
        
        # Create vocabulary with most common words
        vocab = {"<UNK>": 0, "<PAD>": 1}
        most_common = word_counts.most_common(self.MAX_VOCAB_SIZE - 2)
        
        for i, (word, count) in enumerate(most_common):
            vocab[word] = i + 2
        
        print(f"✅ Built vocabulary with {len(vocab)} words")
        return vocab

    def _text_to_vector(self, text: str, vocab: Dict[str, int]) -> List[float]:
        """Convert text to TF-IDF-like vector"""
        if not text:
            return [0.0] * self.EMBEDDING_DIM
        
        tokens = self._tokenize_text(text)
        if not tokens:
            return [0.0] * self.EMBEDDING_DIM
        
        # Create simple embedding by averaging word indices (normalized)
        word_indices = []
        for token in tokens:
            idx = vocab.get(token, vocab["<UNK>"])
            word_indices.append(idx)
        
        if not word_indices:
            return [0.0] * self.EMBEDDING_DIM
        
        # Create embedding vector
        embedding = [0.0] * self.EMBEDDING_DIM
        
        # Simple approach: use hash-based embeddings
        for idx in word_indices:
            # Use hash to distribute word indices across embedding dimensions
            for i in range(self.EMBEDDING_DIM):
                hash_val = hash(f"{idx}_{i}") % 1000000
                embedding[i] += (hash_val / 1000000.0) / len(word_indices)
        
        # Normalize
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding

    def generate_semantic_embeddings(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate semantic embeddings for all problems"""
        print("=== Generating Semantic Embeddings ===")
        
        # Build vocabulary
        vocab = self._build_vocabulary(problems)
        
        # Generate embeddings for each problem
        embeddings = {}
        
        for i, problem in enumerate(problems):
            if i % 50 == 0:
                print(f"Generating embeddings {i}/{len(problems)}")
            
            problem_id = problem.get("id", f"unknown_{i}")
            
            # Combine title and description for embedding
            text = f"{problem.get('title', '')} {problem.get('description', '')}"
            embedding = self._text_to_vector(text, vocab)
            
            embeddings[problem_id] = {
                "embedding": embedding,
                "title_embedding": self._text_to_vector(problem.get("title", ""), vocab),
                "desc_embedding": self._text_to_vector(problem.get("description", ""), vocab)
            }
        
        # Save embeddings
        embeddings_file = self.output_dir / "semantic_embeddings.json"
        with embeddings_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "embedding_dim": self.EMBEDDING_DIM,
                    "vocab_size": len(vocab),
                    "total_problems": len(problems),
                    "timestamp": datetime.now().isoformat()
                },
                "vocabulary": vocab,
                "embeddings": embeddings
            }, f, indent=2)
        
        print(f"✅ Generated embeddings for {len(problems)} problems")
        return {
            "embeddings_file": str(embeddings_file),
            "total_embeddings": len(embeddings),
            "embedding_dim": self.EMBEDDING_DIM
        }

    def build_difficulty_vectors(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build multi-dimensional difficulty vectors"""
        print("=== Building Difficulty Vectors ===")
        
        difficulty_vectors = {}
        
        # Define difficulty dimensions
        dimensions = {
            "algorithmic_complexity": 0,    # Based on algorithmic concepts
            "implementation_difficulty": 1, # Code complexity to implement
            "mathematical_content": 2,      # Math knowledge required
            "data_structure_usage": 3,      # Advanced data structures
            "optimization_required": 4      # Need for optimization
        }
        
        for problem in problems:
            problem_id = problem.get("id", "")
            tags = problem.get("unified_tags", [])
            title = problem.get("title", "").lower()
            
            # Initialize vector
            vector = [0.0] * len(dimensions)
            
            # Algorithmic complexity
            algo_tags = ["dynamic_programming", "graphs", "trees", "shortest_paths", 
                        "minimum_spanning_tree", "topological_sort"]
            vector[0] = sum(1 for tag in tags if tag in algo_tags) / len(algo_tags)
            
            # Implementation difficulty
            impl_tags = ["implementation", "simulation", "constructive_algorithms"]
            has_complex_impl = any(word in title for word in ["complex", "hard", "difficult"])
            vector[1] = (sum(1 for tag in tags if tag in impl_tags) / len(impl_tags)) + (0.3 if has_complex_impl else 0)
            
            # Mathematical content
            math_tags = ["mathematics", "number_theory", "combinatorics", "geometry"]
            vector[2] = sum(1 for tag in tags if tag in math_tags) / len(math_tags)
            
            # Data structure usage
            ds_tags = ["data_structures", "trees", "graphs", "heaps", "hash_tables"]
            vector[3] = sum(1 for tag in tags if tag in ds_tags) / len(ds_tags)
            
            # Optimization required
            opt_tags = ["binary_search", "two_pointers", "greedy", "optimization"]
            vector[4] = sum(1 for tag in tags if tag in opt_tags) / len(opt_tags)
            
            # Normalize to [0, 1] range
            vector = [min(1.0, max(0.0, v)) for v in vector]
            
            difficulty_vectors[problem_id] = {
                "vector": vector,
                "dimensions": dimensions,
                "overall_difficulty": sum(vector) / len(vector)
            }
        
        # Save difficulty vectors
        vectors_file = self.output_dir / "difficulty_vectors.json"
        with vectors_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "dimensions": dimensions,
                    "total_problems": len(problems),
                    "timestamp": datetime.now().isoformat()
                },
                "vectors": difficulty_vectors
            }, f, indent=2)
        
        print(f"✅ Built difficulty vectors for {len(problems)} problems")
        return {
            "vectors_file": str(vectors_file),
            "total_vectors": len(difficulty_vectors),
            "dimensions": len(dimensions)
        }

    def construct_concept_graph(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Construct concept prerequisite graph"""
        print("=== Constructing Concept Graph ===")
        
        # Define concept prerequisites
        concept_prerequisites = {
            "dynamic_programming": ["arrays", "recursion"],
            "graphs": ["arrays", "data_structures"],
            "trees": ["recursion", "data_structures"],
            "binary_search": ["arrays", "sorting"],
            "greedy": ["sorting", "mathematics"],
            "shortest_paths": ["graphs", "greedy"],
            "minimum_spanning_tree": ["graphs", "greedy"],
            "topological_sort": ["graphs", "depth_first_search"],
            "segment_trees": ["trees", "data_structures"],
            "fenwick_trees": ["trees", "data_structures"]
        }
        
        # Build concept graph
        concept_graph = {
            "nodes": {},
            "edges": [],
            "problem_concepts": {}
        }
        
        # Create nodes for each concept
        all_concepts = set()
        for problem in problems:
            tags = problem.get("unified_tags", [])
            all_concepts.update(tags)
        
        for concept in all_concepts:
            concept_graph["nodes"][concept] = {
                "name": concept,
                "prerequisites": concept_prerequisites.get(concept, []),
                "problem_count": 0,
                "difficulty_level": 1
            }
        
        # Count problems per concept and assign difficulty levels
        for problem in problems:
            problem_id = problem.get("id", "")
            tags = problem.get("unified_tags", [])
            
            concept_graph["problem_concepts"][problem_id] = tags
            
            for tag in tags:
                if tag in concept_graph["nodes"]:
                    concept_graph["nodes"][tag]["problem_count"] += 1
        
        # Assign difficulty levels based on prerequisites
        def calculate_difficulty_level(concept, visited=None):
            if visited is None:
                visited = set()
            
            if concept in visited:
                return 1  # Circular dependency, assign basic level
            
            visited.add(concept)
            prereqs = concept_prerequisites.get(concept, [])
            
            if not prereqs:
                return 1  # No prerequisites = basic level
            
            max_prereq_level = max(
                calculate_difficulty_level(prereq, visited.copy()) 
                for prereq in prereqs
                if prereq in concept_graph["nodes"]
            ) if prereqs else 0
            
            return max_prereq_level + 1
        
        for concept in concept_graph["nodes"]:
            concept_graph["nodes"][concept]["difficulty_level"] = calculate_difficulty_level(concept)
        
        # Create edges based on prerequisites
        for concept, prereqs in concept_prerequisites.items():
            if concept in concept_graph["nodes"]:
                for prereq in prereqs:
                    if prereq in concept_graph["nodes"]:
                        concept_graph["edges"].append({
                            "from": prereq,
                            "to": concept,
                            "type": "prerequisite"
                        })
        
        # Save concept graph
        graph_file = self.output_dir / "concept_graph.json"
        with graph_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "total_concepts": len(concept_graph["nodes"]),
                    "total_edges": len(concept_graph["edges"]),
                    "total_problems": len(problems),
                    "timestamp": datetime.now().isoformat()
                },
                "graph": concept_graph
            }, f, indent=2)
        
        print(f"✅ Built concept graph with {len(concept_graph['nodes'])} concepts")
        return {
            "graph_file": str(graph_file),
            "total_concepts": len(concept_graph["nodes"]),
            "total_edges": len(concept_graph["edges"])
        }

    def calculate_interview_features(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate Google interview relevance features"""
        print("=== Calculating Interview Features ===")
        
        interview_features = {}
        
        # Load quality engine for scoring
        quality_engine_file = self.data_dir / "processed" / "academic_datasets" / "code_quality_engine.json"
        quality_criteria = {}
        
        if quality_engine_file.exists():
            with quality_engine_file.open("r") as f:
                quality_data = json.load(f)
                quality_criteria = quality_data.get("evaluation_framework", {})
        
        for problem in problems:
            problem_id = problem.get("id", "")
            
            # Base interview probability from existing google_relevance
            base_probability = problem.get("google_relevance", 0.0)
            
            # Enhance with additional features
            features = {
                "base_google_relevance": base_probability,
                "frequency_score": 0.0,
                "difficulty_appropriateness": 0.0,
                "concept_coverage": 0.0,
                "implementation_complexity": 0.0,
                "final_interview_probability": 0.0
            }
            
            # Frequency score (higher for common interview topics)
            common_topics = ["arrays", "strings", "dynamic_programming", "graphs", "trees"]
            tags = problem.get("unified_tags", [])
            features["frequency_score"] = len([tag for tag in tags if tag in common_topics]) / len(common_topics)
            
            # Difficulty appropriateness (Google likes medium-hard)
            difficulty = problem.get("difficulty", {})
            diff_level = difficulty.get("level", "medium")
            if diff_level == "medium":
                features["difficulty_appropriateness"] = 1.0
            elif diff_level == "hard":
                features["difficulty_appropriateness"] = 0.7
            else:
                features["difficulty_appropriateness"] = 0.3
            
            # Concept coverage (more concepts = more comprehensive)
            features["concept_coverage"] = min(1.0, len(tags) / 5.0)
            
            # Implementation complexity (moderate complexity preferred)
            title_complexity = len(problem.get("title", "").split())
            desc_complexity = len(problem.get("description", "").split())
            total_complexity = title_complexity + desc_complexity
            features["implementation_complexity"] = min(1.0, total_complexity / 100.0)
            
            # Calculate final interview probability
            weights = {
                "base_google_relevance": 0.3,
                "frequency_score": 0.25,
                "difficulty_appropriateness": 0.25,
                "concept_coverage": 0.1,
                "implementation_complexity": 0.1
            }
            
            final_prob = sum(
                features[key] * weight 
                for key, weight in weights.items()
            )
            
            features["final_interview_probability"] = min(1.0, final_prob)
            
            interview_features[problem_id] = features
        
        # Save interview features
        features_file = self.output_dir / "interview_features.json"
        with features_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "total_problems": len(problems),
                    "feature_weights": {
                        "base_google_relevance": 0.3,
                        "frequency_score": 0.25,
                        "difficulty_appropriateness": 0.25,
                        "concept_coverage": 0.1,
                        "implementation_complexity": 0.1
                    },
                    "timestamp": datetime.now().isoformat()
                },
                "features": interview_features
            }, f, indent=2)
        
        print(f"✅ Calculated interview features for {len(problems)} problems")
        return {
            "features_file": str(features_file),
            "total_features": len(interview_features)
        }

    def run_feature_engineering_pipeline(self) -> Dict[str, Any]:
        """Run complete AI feature engineering pipeline"""
        print("=== AI Feature Engineering Pipeline ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_status": "running",
            "components": {}
        }
        
        try:
            # Load unified problems
            problems_file = self.processed_dir / "problems_unified_complete.json"
            if not problems_file.exists():
                raise FileNotFoundError(f"Unified problems file not found: {problems_file}")
            
            print("Loading unified problems...")
            with problems_file.open("r", encoding="utf-8") as f:
                problems_data = json.load(f)
            
            problems = problems_data.get("problems", [])
            print(f"Loaded {len(problems)} unified problems")
            
            # 1. Generate semantic embeddings
            print("\n1. Generating semantic embeddings...")
            embeddings_result = self.generate_semantic_embeddings(problems)
            results["components"]["embeddings"] = embeddings_result
            
            # 2. Build difficulty vectors
            print("\n2. Building difficulty vectors...")
            vectors_result = self.build_difficulty_vectors(problems)
            results["components"]["difficulty_vectors"] = vectors_result
            
            # 3. Construct concept graph
            print("\n3. Constructing concept graph...")
            graph_result = self.construct_concept_graph(problems)
            results["components"]["concept_graph"] = graph_result
            
            # 4. Calculate interview features
            print("\n4. Calculating interview features...")
            interview_result = self.calculate_interview_features(problems)
            results["components"]["interview_features"] = interview_result
            
            # Determine overall success
            all_successful = all(
                "file" in str(comp) for comp in results["components"].values()
            )
            
            results["pipeline_status"] = "success" if all_successful else "partial_success"
            results["success_count"] = len(results["components"])
            results["total_components"] = 4
            
            # Save pipeline summary
            summary_file = self.output_dir / "ai_features_summary.json"
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ AI feature engineering complete!")
            print(f"Success: {results['success_count']}/{results['total_components']} components")
            
            return results
            
        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            return results


def main():
    """Main function for running AI feature engineering"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Create engineer
    engineer = AIFeatureEngineer(data_dir)
    
    # Run feature engineering pipeline
    results = engineer.run_feature_engineering_pipeline()
    
    if results["pipeline_status"] == "success":
        print("\n🎉 AI feature engineering completed successfully!")
    else:
        print(f"\n⚠️  Pipeline completed with status: {results['pipeline_status']}")
    
    return results


if __name__ == "__main__":
    main()
