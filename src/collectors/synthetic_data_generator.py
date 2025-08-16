from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .acquisition_logger import AcquisitionLogger


@dataclass
class SyntheticDataGenerator:
    data_dir: Path
    
    @property
    def output_dir(self) -> Path:
        p = self.data_dir / "synthetic"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def generate_behavioral_scenarios(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate synthetic behavioral interview scenarios using templates"""
        
        # Core competencies from university research
        competencies = [
            "Leadership", "Teamwork", "Communication", "Problem Solving", 
            "Adaptability", "Conflict Resolution", "Decision Making", "Initiative",
            "Time Management", "Customer Focus", "Innovation", "Resilience"
        ]
        
        # Scenario templates with variable components
        scenario_templates = [
            {
                "situation": "Working on a {project_type} project with a team of {team_size} people",
                "task": "Need to {task_action} within {timeframe}",
                "complications": ["tight deadline", "conflicting priorities", "resource constraints", "team disagreements"],
                "skills": ["Leadership", "Time Management", "Teamwork"]
            },
            {
                "situation": "Customer reported a {severity} issue with {product_component}",
                "task": "Resolve the issue and prevent future occurrences",
                "complications": ["unclear requirements", "missing information", "multiple stakeholders"],
                "skills": ["Problem Solving", "Communication", "Customer Focus"]
            },
            {
                "situation": "Team member {conflict_type} during {project_phase}",
                "task": "Address the situation while maintaining team productivity",
                "complications": ["personality conflicts", "different working styles", "skill gaps"],
                "skills": ["Conflict Resolution", "Leadership", "Communication"]
            },
            {
                "situation": "Unexpected {change_type} required significant adjustment to project plan",
                "task": "Adapt strategy and keep project on track",
                "complications": ["budget changes", "scope creep", "technology shifts"],
                "skills": ["Adaptability", "Problem Solving", "Decision Making"]
            }
        ]
        
        # Variable components for templates
        variables = {
            "project_type": ["software development", "data analysis", "system migration", "process improvement"],
            "team_size": ["3", "5", "8", "12"],
            "task_action": ["deliver the solution", "improve performance", "resolve bugs", "implement new features"],
            "timeframe": ["2 weeks", "1 month", "3 months", "by end of quarter"],
            "product_component": ["authentication system", "payment processing", "user interface", "database"],
            "severity": ["critical", "high-priority", "performance-related", "security"],
            "conflict_type": ["disagreed with approach", "missed deadlines", "had different priorities"],
            "project_phase": ["planning", "development", "testing", "deployment"],
            "change_type": ["requirement change", "technology update", "resource reduction", "timeline compression"]
        }
        
        scenarios = []
        
        for i in range(count):
            template = random.choice(scenario_templates)
            
            # Fill in template variables
            situation = template["situation"]
            task = template["task"]
            
            for var, options in variables.items():
                if f"{{{var}}}" in situation:
                    situation = situation.replace(f"{{{var}}}", random.choice(options))
                if f"{{{var}}}" in task:
                    task = task.replace(f"{{{var}}}", random.choice(options))
            
            # Add complications
            complications = random.sample(template["complications"], random.randint(1, 2))
            
            scenario = {
                "id": f"synthetic_behavioral_{i+1:03d}",
                "type": "behavioral_scenario",
                "situation": situation,
                "task": task,
                "complications": complications,
                "target_competencies": template["skills"],
                "difficulty": random.choice(["junior", "mid", "senior"]),
                "expected_star_components": {
                    "situation": "Clear context and background",
                    "task": "Specific responsibility or goal",
                    "action": "Concrete steps taken (use 'I' not 'we')",
                    "result": "Quantified outcome and lessons learned"
                },
                "evaluation_criteria": [
                    "Specificity and detail in response",
                    "Personal ownership and accountability",
                    "Problem-solving approach",
                    "Quantified results",
                    "Lessons learned and growth"
                ],
                "generated_at": datetime.now().isoformat()
            }
            
            scenarios.append(scenario)
        
        return scenarios

    def generate_coding_problems(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate synthetic coding problems using algorithmic patterns"""
        
        problem_patterns = [
            {
                "category": "Array/String Manipulation",
                "templates": [
                    "Given an array of {data_type}, find {target_description}",
                    "Implement a function to {operation} in a {data_structure}",
                    "Given a string, {string_operation}"
                ],
                "variables": {
                    "data_type": ["integers", "strings", "characters", "objects"],
                    "target_description": ["the maximum sum subarray", "duplicates", "the kth largest element"],
                    "operation": ["insert", "delete", "search", "sort", "merge"],
                    "data_structure": ["sorted array", "circular buffer", "hash table"],
                    "string_operation": ["reverse words", "check if palindrome", "find longest substring"]
                },
                "complexity": {"time": "O(n)", "space": "O(1)"},
                "difficulty": "easy"
            },
            {
                "category": "Dynamic Programming",
                "templates": [
                    "Given {dp_input}, find the {optimization_goal}",
                    "You have {resource_constraints}, determine {dp_question}"
                ],
                "variables": {
                    "dp_input": ["a sequence of numbers", "a grid", "multiple arrays"],
                    "optimization_goal": ["minimum cost path", "maximum profit", "number of ways"],
                    "resource_constraints": ["limited capacity", "multiple choices", "time windows"],
                    "dp_question": ["optimal strategy", "minimum operations needed", "maximum value"]
                },
                "complexity": {"time": "O(n²)", "space": "O(n)"},
                "difficulty": "medium"
            },
            {
                "category": "Graph Algorithms",
                "templates": [
                    "Given a {graph_type}, find {graph_problem}",
                    "Implement {graph_algorithm} for {graph_application}"
                ],
                "variables": {
                    "graph_type": ["directed graph", "weighted graph", "tree", "binary tree"],
                    "graph_problem": ["shortest path", "connected components", "cycle detection"],
                    "graph_algorithm": ["DFS", "BFS", "Dijkstra's algorithm", "Union-Find"],
                    "graph_application": ["social network analysis", "route planning", "dependency resolution"]
                },
                "complexity": {"time": "O(V + E)", "space": "O(V)"},
                "difficulty": "hard"
            }
        ]
        
        problems = []
        
        for i in range(count):
            pattern = random.choice(problem_patterns)
            template = random.choice(pattern["templates"])
            
            # Fill template variables
            description = template
            for var, options in pattern["variables"].items():
                if f"{{{var}}}" in description:
                    description = description.replace(f"{{{var}}}", random.choice(options))
            
            problem = {
                "id": f"synthetic_coding_{i+1:03d}",
                "type": "coding_problem",
                "title": f"Problem {i+1}: {pattern['category']}",
                "description": description,
                "category": pattern["category"],
                "difficulty": pattern["difficulty"],
                "time_complexity": pattern["complexity"]["time"],
                "space_complexity": pattern["complexity"]["space"],
                "tags": [pattern["category"].lower().replace(" ", "_"), pattern["difficulty"]],
                "companies": random.sample(["Google", "Facebook", "Amazon", "Microsoft", "Apple"], 
                                         random.randint(2, 4)),
                "google_interview_relevance": random.randint(3, 5),
                "test_cases": self._generate_test_cases(pattern["category"]),
                "hints": self._generate_hints(pattern["category"]),
                "generated_at": datetime.now().isoformat()
            }
            
            problems.append(problem)
        
        return problems

    def _generate_test_cases(self, category: str) -> List[Dict[str, Any]]:
        """Generate sample test cases for coding problems"""
        if "Array" in category:
            return [
                {"input": "[1, 2, 3, 4, 5]", "output": "Expected result based on problem"},
                {"input": "[]", "output": "Edge case: empty array"},
                {"input": "[1]", "output": "Edge case: single element"}
            ]
        elif "Dynamic" in category:
            return [
                {"input": "n=5, constraints=[1,2,3]", "output": "Optimal value"},
                {"input": "n=0", "output": "Base case"},
                {"input": "Large input", "output": "Performance test"}
            ]
        elif "Graph" in category:
            return [
                {"input": "nodes=5, edges=[[0,1],[1,2]]", "output": "Graph traversal result"},
                {"input": "Empty graph", "output": "No connections"},
                {"input": "Disconnected components", "output": "Multiple components"}
            ]
        else:
            return [
                {"input": "Sample input", "output": "Expected output"},
                {"input": "Edge case", "output": "Edge case result"}
            ]

    def _generate_hints(self, category: str) -> List[str]:
        """Generate hints for coding problems"""
        hints_map = {
            "Array/String Manipulation": [
                "Consider using two pointers technique",
                "Think about sorting the array first",
                "Use a hash map for O(1) lookups"
            ],
            "Dynamic Programming": [
                "Identify the optimal substructure",
                "Define your state variables clearly",
                "Consider bottom-up vs top-down approach"
            ],
            "Graph Algorithms": [
                "Think about the graph representation",
                "Consider using BFS for shortest path",
                "Check for cycles before processing"
            ]
        }
        
        return hints_map.get(category, ["Think about the problem step by step", "Consider edge cases"])

    def generate_system_design_problems(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate synthetic system design problems"""
        
        system_components = [
            "messaging service", "file storage system", "recommendation engine",
            "authentication service", "payment processor", "notification system",
            "search engine", "analytics platform", "streaming service"
        ]
        
        scale_requirements = [
            "millions of users", "billions of requests per day", "petabytes of data",
            "global distribution", "real-time processing", "99.9% uptime"
        ]
        
        constraints = [
            "low latency requirements", "high availability needs", "cost optimization",
            "security compliance", "data consistency", "horizontal scaling"
        ]
        
        problems = []
        
        for i in range(count):
            component = random.choice(system_components)
            scale = random.choice(scale_requirements)
            constraint = random.choice(constraints)
            
            problem = {
                "id": f"synthetic_system_design_{i+1:03d}",
                "type": "system_design_problem",
                "title": f"Design a {component}",
                "description": f"Design a {component} that can handle {scale} with {constraint}",
                "scale_requirements": scale,
                "key_constraints": [constraint],
                "evaluation_areas": [
                    "High-level architecture",
                    "Database design",
                    "API design", 
                    "Scalability considerations",
                    "Trade-offs discussion"
                ],
                "expected_components": [
                    "Load balancers",
                    "Application servers", 
                    "Databases",
                    "Caching layers",
                    "Message queues"
                ],
                "difficulty": random.choice(["intermediate", "advanced"]),
                "companies": ["Google", "Facebook", "Amazon", "Netflix"],
                "generated_at": datetime.now().isoformat()
            }
            
            problems.append(problem)
        
        return problems

    def run_generation(self, 
                      behavioral_count: int = 100,
                      coding_count: int = 50, 
                      system_design_count: int = 20) -> Dict[str, Any]:
        """Run complete synthetic data generation"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            print("=== Synthetic Data Generation ===")
            
            # Generate each type of synthetic data
            print(f"Generating {behavioral_count} behavioral scenarios...")
            behavioral_scenarios = self.generate_behavioral_scenarios(behavioral_count)
            
            print(f"Generating {coding_count} coding problems...")
            coding_problems = self.generate_coding_problems(coding_count)
            
            print(f"Generating {system_design_count} system design problems...")
            system_design_problems = self.generate_system_design_problems(system_design_count)
            
            # Save generated data
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            behavioral_file = self.output_dir / f"behavioral_scenarios_{ts}.json"
            with behavioral_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "count": len(behavioral_scenarios),
                        "type": "synthetic_behavioral_scenarios"
                    },
                    "scenarios": behavioral_scenarios
                }, f, ensure_ascii=False, indent=2)
            
            coding_file = self.output_dir / f"coding_problems_{ts}.json"
            with coding_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "count": len(coding_problems),
                        "type": "synthetic_coding_problems"
                    },
                    "problems": coding_problems
                }, f, ensure_ascii=False, indent=2)
            
            system_design_file = self.output_dir / f"system_design_problems_{ts}.json"
            with system_design_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "count": len(system_design_problems),
                        "type": "synthetic_system_design_problems"
                    },
                    "problems": system_design_problems
                }, f, ensure_ascii=False, indent=2)
            
            # Create comprehensive summary
            summary = {
                "timestamp": datetime.now().isoformat(),
                "behavioral_scenarios": len(behavioral_scenarios),
                "coding_problems": len(coding_problems),
                "system_design_problems": len(system_design_problems),
                "total_generated": len(behavioral_scenarios) + len(coding_problems) + len(system_design_problems),
                "files_created": [
                    str(behavioral_file),
                    str(coding_file),
                    str(system_design_file)
                ],
                "generation_method": "template_based_with_randomization",
                "quality_notes": [
                    "Behavioral scenarios use research-based competency frameworks",
                    "Coding problems follow standard algorithmic patterns",
                    "System design problems include evaluation criteria",
                    "All generated content includes metadata for training"
                ]
            }
            
            summary_file = self.output_dir / f"generation_summary_{ts}.json"
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "total_generated": summary["total_generated"],
                "output_files": summary["files_created"],
                "summary_file": str(summary_file)
            }
            
            logger.log("synthetic_generation", "template_based_generation", 
                      records=summary["total_generated"], success=True, metadata=meta)
            
            print(f"✅ Generated {summary['total_generated']} synthetic data items")
            print(f"   📄 {summary['behavioral_scenarios']} behavioral scenarios")
            print(f"   💻 {summary['coding_problems']} coding problems")
            print(f"   🏗️ {summary['system_design_problems']} system design problems")
            
            return meta
            
        except Exception as e:
            logger.log("synthetic_generation", "template_based_generation", 
                      records=0, success=False, error=str(e))
            raise
