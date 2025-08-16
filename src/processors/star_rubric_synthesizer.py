from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class STARRubricSynthesizer:
    data_dir: Path

    @property
    def processed_dir(self) -> Path:
        p = self.data_dir / "processed"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def synthesize_master_rubric(self) -> Dict[str, Any]:
        """
        Synthesize a master STAR evaluation rubric from research-based sources
        Based on university rubrics and Google's behavioral interview standards
        """
        
        # Core STAR components with detailed evaluation criteria
        star_components = {
            "situation": {
                "description": "Context and background of the scenario",
                "evaluation_criteria": [
                    "Clarity of context - Is the situation clearly described?",
                    "Relevance to role - Does the situation relate to job requirements?", 
                    "Appropriate scope - Is the situation neither too simple nor overly complex?",
                    "Professional setting - Is it from a work/academic environment?"
                ],
                "scoring_levels": {
                    1: "Vague or unclear context, difficult to understand the scenario",
                    2: "Basic context provided but lacks important details", 
                    3: "Clear context with sufficient detail to understand the scenario",
                    4: "Comprehensive context that sets up the challenge effectively",
                    5: "Exceptional context that demonstrates sophisticated problem framing"
                }
            },
            "task": {
                "description": "Specific responsibility, goal, or challenge to address",
                "evaluation_criteria": [
                    "Specificity - Is the task/goal clearly defined?",
                    "Personal ownership - Is their specific role/responsibility clear?",
                    "Complexity level - Is the task appropriately challenging?", 
                    "Measurable outcome - Can success/failure be evaluated?"
                ],
                "scoring_levels": {
                    1: "Task unclear or too vague to understand what was needed",
                    2: "General task identified but lacks specificity",
                    3: "Clear task with defined expectations and personal responsibility", 
                    4: "Well-defined task with clear success criteria and ownership",
                    5: "Sophisticated task requiring strategic thinking and leadership"
                }
            },
            "action": {
                "description": "Specific steps taken to address the task/challenge", 
                "evaluation_criteria": [
                    "Personal accountability - Uses 'I' rather than 'we' statements",
                    "Specific details - Concrete actions rather than generalizations",
                    "Logical progression - Actions follow a coherent sequence",
                    "Problem-solving approach - Demonstrates systematic thinking",
                    "Adaptability - Shows flexibility when obstacles arise"
                ],
                "scoring_levels": {
                    1: "Vague actions, mostly 'we' statements, lacks personal ownership",
                    2: "Some specific actions but limited personal accountability",
                    3: "Clear personal actions with specific details and logical flow",
                    4: "Comprehensive action plan with strong problem-solving approach", 
                    5: "Exceptional actions showing leadership, innovation, and adaptability"
                }
            },
            "result": {
                "description": "Outcome achieved and lessons learned",
                "evaluation_criteria": [
                    "Quantified impact - Uses numbers, percentages, or measurable outcomes",
                    "Positive outcome - Demonstrates successful resolution", 
                    "Learning demonstrated - Shows growth and self-reflection",
                    "Broader impact - Considers effect on team/organization",
                    "Follow-up actions - Describes how lessons were applied later"
                ],
                "scoring_levels": {
                    1: "No clear outcome or impact described",
                    2: "General positive outcome but no specific measurements",
                    3: "Clear positive result with some quantification",
                    4: "Strong quantified results with demonstrated learning",
                    5: "Exceptional results with measurable impact and strategic insights"
                }
            }
        }

        # Google-specific behavioral competencies
        google_competencies = {
            "googleyness": {
                "description": "Comfort with ambiguity, bias for action, collaboration, intellectual humility", 
                "indicators": [
                    "Handles uncertainty and changing requirements well",
                    "Takes initiative without waiting for perfect information",
                    "Collaborates effectively across teams and functions",
                    "Admits mistakes and learns from feedback",
                    "Shows growth mindset and continuous learning"
                ]
            },
            "leadership": {
                "description": "Ability to influence, motivate, and guide others",
                "indicators": [
                    "Takes ownership of outcomes beyond personal tasks",
                    "Influences without formal authority",
                    "Develops and mentors others",
                    "Makes decisions under pressure",
                    "Drives results through others"
                ]
            },
            "general_cognitive_ability": {
                "description": "Problem-solving, learning agility, and analytical thinking",
                "indicators": [
                    "Breaks down complex problems systematically", 
                    "Learns quickly from new information",
                    "Identifies patterns and root causes",
                    "Makes data-driven decisions",
                    "Adapts approach based on feedback"
                ]
            },
            "role_related_knowledge": {
                "description": "Technical skills and domain expertise relevant to the position",
                "indicators": [
                    "Demonstrates deep technical knowledge",
                    "Applies expertise to solve novel problems", 
                    "Stays current with industry trends",
                    "Transfers knowledge across domains",
                    "Builds on existing expertise effectively"
                ]
            }
        }

        # Overall response quality factors
        response_quality = {
            "communication": {
                "clarity": "Response is well-organized and easy to follow",
                "conciseness": "Appropriate level of detail without unnecessary information",
                "engagement": "Maintains interviewer interest throughout the story"
            },
            "authenticity": {
                "believability": "Story seems genuine and realistic",
                "personal_insight": "Shows self-awareness and reflection", 
                "emotional_intelligence": "Demonstrates understanding of interpersonal dynamics"
            },
            "strategic_thinking": {
                "systems_perspective": "Considers broader organizational context",
                "long_term_impact": "Thinks beyond immediate problem resolution",
                "stakeholder_awareness": "Recognizes multiple perspectives and interests"
            }
        }

        # Synthesized master rubric
        master_rubric = {
            "framework_name": "DSATrain STAR Evaluation Rubric v1.0",
            "based_on_sources": [
                "Northern Arizona University STAR Rubric",
                "University of Washington Behavioral Competencies", 
                "Google Engineering Practices Documentation",
                "MIT Career Development STAR Guidelines",
                "Academic research on behavioral interviewing"
            ],
            "star_components": star_components,
            "google_competencies": google_competencies,
            "response_quality": response_quality,
            "overall_scoring": {
                "scale": "1-5 points per component (Situation, Task, Action, Result)",
                "bonus_points": "Up to 2 additional points for exceptional Googleyness demonstration",
                "total_possible": 22,
                "interpretation": {
                    "18-22": "Exceptional response - Strong hire recommendation",
                    "14-17": "Good response - Hire recommendation", 
                    "10-13": "Adequate response - Marginal hire",
                    "6-9": "Weak response - No hire recommendation",
                    "1-5": "Poor response - Strong no hire"
                }
            },
            "evaluation_guidelines": [
                "Focus on specific behaviors and concrete examples",
                "Look for personal accountability ('I' vs 'we' statements)",
                "Assess problem-solving process, not just outcomes",
                "Consider cultural fit and Google values alignment",
                "Weight recent examples more heavily than distant ones",
                "Probe for details if initial response lacks specificity"
            ],
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        return master_rubric

    def create_sample_responses(self) -> List[Dict[str, Any]]:
        """
        Create sample STAR responses at different quality levels for training
        These serve as seed examples for expert labeling
        """
        
        sample_responses = [
            {
                "id": "sample_001",
                "question": "Tell me about a time when you had to work with a difficult team member.",
                "competencies": ["Teamwork", "Conflict Resolution", "Communication"],
                "response": {
                    "situation": "I was working on a software project with a team of 5 developers. One team member, let's call him John, consistently missed deadlines and didn't communicate his progress. This was causing delays for the entire project and frustration among other team members.",
                    "task": "As the project lead, I needed to address John's performance issues while maintaining team morale and keeping the project on track. We had a hard deadline in 3 weeks for a client demo.",
                    "action": "First, I scheduled a private one-on-one meeting with John to understand if there were any underlying issues. I discovered he was struggling with a new technology we were using and felt embarrassed to ask for help. I arranged for him to pair program with our most experienced developer for 2 days. I also restructured his tasks to focus on areas where he was more confident while he learned the new technology. I set up daily check-ins to monitor progress and provide support.",
                    "result": "Within a week, John's productivity improved significantly. He successfully completed his portion of the project on time, and we delivered the demo successfully. The team dynamic improved, and John later thanked me for the support. I learned the importance of probing deeper when team members are struggling rather than assuming the worst."
                },
                "expected_scores": {
                    "situation": 4,
                    "task": 4, 
                    "action": 5,
                    "result": 4,
                    "googleyness_bonus": 1,
                    "total": 18
                },
                "quality_level": "excellent",
                "reasoning": "Clear context, specific actions, personal ownership, quantified results, shows leadership and empathy"
            },
            {
                "id": "sample_002", 
                "question": "Describe a time when you had to solve a complex technical problem.",
                "competencies": ["Problem Solving", "Technical Expertise", "Persistence"],
                "response": {
                    "situation": "We had a performance issue in our production system where page load times increased to 5+ seconds during peak hours.",
                    "task": "I was assigned to identify and fix the root cause as quickly as possible since it was affecting user experience.",
                    "action": "I started by analyzing the logs and noticed the database queries were taking longer. I used profiling tools to identify the slowest queries and found that one particular query was missing an index. I created the index and tested it in staging first.",
                    "result": "The page load times went back to under 2 seconds. Users were happy and we didn't lose any customers."
                },
                "expected_scores": {
                    "situation": 3,
                    "task": 3,
                    "action": 3, 
                    "result": 2,
                    "googleyness_bonus": 0,
                    "total": 11
                },
                "quality_level": "adequate",
                "reasoning": "Basic STAR structure but lacks detail, doesn't show deeper problem-solving process, minimal learning demonstrated"
            },
            {
                "id": "sample_003",
                "question": "Tell me about a time when you had to adapt to a significant change at work.",
                "competencies": ["Adaptability", "Change Management", "Resilience"], 
                "response": {
                    "situation": "There was a big reorganization at my company.",
                    "task": "We had to adjust to new processes.",
                    "action": "I adapted to the changes and helped my team.",
                    "result": "Everything worked out fine in the end."
                },
                "expected_scores": {
                    "situation": 1,
                    "task": 1,
                    "action": 1,
                    "result": 1, 
                    "googleyness_bonus": 0,
                    "total": 4
                },
                "quality_level": "poor",
                "reasoning": "Extremely vague, no specific details, lacks personal ownership, no measurable outcomes"
            },
            {
                "id": "sample_004",
                "question": "Describe a time when you had to make a difficult decision with limited information.",
                "competencies": ["Decision Making", "Leadership", "Risk Management"],
                "response": {
                    "situation": "I was leading a product feature development when our main competitor announced a similar feature would launch in 6 weeks. Our original timeline was 10 weeks, and we had limited data on user preferences for some design choices.",
                    "task": "I had to decide whether to rush our timeline, modify our feature scope, or proceed as planned. Each option carried significant risks - rushing could compromise quality, reducing scope might make us less competitive, and maintaining timeline meant launching after the competitor.",
                    "action": "I called an emergency meeting with engineering, design, and product stakeholders. I created a decision matrix weighing each option against our success metrics: user satisfaction, time to market, and code quality. I gathered what user data we had and conducted rapid user testing with 20 customers over 2 days. Based on this analysis, I decided to accelerate timeline by 3 weeks while reducing scope to focus on the most validated user needs. I negotiated with engineering to accept some technical debt in exchange for faster delivery, with a plan to address it in the following sprint.",
                    "result": "We launched 1 week ahead of our competitor with a more focused feature set. User adoption was 40% higher than projected, and the technical debt was resolved within 3 weeks. The experience taught me the value of rapid validation and stakeholder alignment in high-pressure decisions. I've since implemented a standard decision framework for similar situations."
                },
                "expected_scores": {
                    "situation": 5,
                    "task": 5,
                    "action": 5,
                    "result": 5,
                    "googleyness_bonus": 2,
                    "total": 22
                },
                "quality_level": "exceptional",
                "reasoning": "Outstanding example with complex situation, clear decision process, quantified results, demonstrates all Google competencies"
            }
        ]

        return sample_responses

    def create_labeling_guidelines(self) -> Dict[str, Any]:
        """Create detailed guidelines for expert labelers"""
        
        guidelines = {
            "overview": "Guidelines for expert evaluation of STAR method responses",
            "evaluator_qualifications": [
                "5+ years experience in technical hiring",
                "Familiarity with Google interview process preferred", 
                "Background in behavioral interviewing techniques",
                "Experience with STAR method evaluation"
            ],
            "evaluation_process": {
                "step_1": "Read the complete response without scoring",
                "step_2": "Identify each STAR component (Situation, Task, Action, Result)",
                "step_3": "Score each component using the 1-5 scale", 
                "step_4": "Evaluate Google competencies demonstrated",
                "step_5": "Assign bonus points for exceptional Googleyness (0-2)",
                "step_6": "Calculate total score and provide brief reasoning"
            },
            "scoring_calibration": [
                "Score 1: Missing or extremely poor quality",
                "Score 2: Below expectations, major gaps",
                "Score 3: Meets basic expectations", 
                "Score 4: Above expectations, good quality",
                "Score 5: Exceptional, outstanding example"
            ],
            "common_pitfalls": [
                "Don't be swayed by impressive outcomes if process was poor",
                "Watch for 'we' vs 'I' - personal accountability is crucial",
                "Vague responses should score lower regardless of outcome",
                "Recent examples are generally more valuable than old ones",
                "Technical complexity doesn't automatically mean higher score"
            ],
            "quality_assurance": {
                "inter_rater_reliability": "Each response should be scored by 2-3 evaluators",
                "consensus_requirement": "Scores within 2 points are acceptable", 
                "dispute_resolution": "Major disagreements require discussion and re-evaluation",
                "calibration_sessions": "Regular sessions to maintain scoring consistency"
            }
        }

        return guidelines

    def run_synthesis(self) -> Dict[str, Any]:
        """Create the complete expert labeling framework"""
        
        print("=== Synthesizing Master STAR Evaluation Rubric ===")
        
        # Generate all components
        master_rubric = self.synthesize_master_rubric()
        sample_responses = self.create_sample_responses()
        labeling_guidelines = self.create_labeling_guidelines()
        
        # Save all components
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        rubric_file = self.processed_dir / f"star_master_rubric_{ts}.json"
        with rubric_file.open("w", encoding="utf-8") as f:
            json.dump(master_rubric, f, ensure_ascii=False, indent=2)
        
        samples_file = self.processed_dir / f"star_sample_responses_{ts}.json"
        with samples_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "purpose": "Training samples for expert labelers",
                    "count": len(sample_responses)
                },
                "sample_responses": sample_responses
            }, f, ensure_ascii=False, indent=2)
        
        guidelines_file = self.processed_dir / f"star_labeling_guidelines_{ts}.json"
        with guidelines_file.open("w", encoding="utf-8") as f:
            json.dump(labeling_guidelines, f, ensure_ascii=False, indent=2)
        
        # Create comprehensive framework summary
        framework_summary = {
            "framework_name": "DSATrain Expert STAR Labeling Framework",
            "created_at": datetime.now().isoformat(),
            "components": {
                "master_rubric": {
                    "file": str(rubric_file),
                    "description": "Comprehensive evaluation criteria synthesized from research",
                    "scoring_scale": "1-5 per component + 0-2 bonus points"
                },
                "sample_responses": {
                    "file": str(samples_file), 
                    "description": "Calibrated examples at different quality levels",
                    "count": len(sample_responses)
                },
                "labeling_guidelines": {
                    "file": str(guidelines_file),
                    "description": "Detailed instructions for expert evaluators"
                }
            },
            "next_steps": [
                "Recruit qualified expert evaluators (3-5 recommended)",
                "Conduct calibration session using sample responses",
                "Begin labeling production dataset (target: 500-1000 responses)",
                "Implement inter-rater reliability checks",
                "Use labeled dataset for STAR evaluation model fine-tuning"
            ],
            "success_metrics": [
                "Inter-rater reliability > 0.8",
                "Coverage of all major competency areas",
                "Balanced distribution across quality levels",
                "Sufficient volume for model training (500+ samples)"
            ]
        }
        
        framework_file = self.processed_dir / f"star_labeling_framework_{ts}.json"
        with framework_file.open("w", encoding="utf-8") as f:
            json.dump(framework_summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Master rubric created: {rubric_file}")
        print(f"✅ Sample responses created: {samples_file}")
        print(f"✅ Labeling guidelines created: {guidelines_file}")
        print(f"✅ Framework summary: {framework_file}")
        
        return {
            "framework_file": str(framework_file),
            "rubric_file": str(rubric_file),
            "samples_file": str(samples_file),
            "guidelines_file": str(guidelines_file),
            "total_components": 3,
            "sample_count": len(sample_responses)
        }
