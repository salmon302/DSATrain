from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .acquisition_logger import AcquisitionLogger


@dataclass 
class ExpertResponseCollector:
    data_dir: Path

    @property
    def output_dir(self) -> Path:
        p = self.data_dir / "expert_labeled"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def generate_response_prompts(self, count: int = 200) -> List[Dict[str, Any]]:
        """
        Generate diverse behavioral interview prompts for expert response collection
        These will be used to create the expert-labeled training dataset
        """
        
        # Core competency areas from Google and university research
        competency_prompts = {
            "leadership": [
                "Tell me about a time when you had to lead a team through a difficult situation.",
                "Describe a situation where you had to influence others without having formal authority.",
                "Give me an example of when you had to make a tough decision that affected your team.",
                "Tell me about a time when you had to take ownership of a failure.",
                "Describe a situation where you had to motivate an underperforming team member."
            ],
            "teamwork": [
                "Tell me about a time when you had to work with a difficult team member.",
                "Describe a situation where you had to collaborate with people from different backgrounds.",
                "Give me an example of when you had to compromise on your preferred approach for the team's benefit.",
                "Tell me about a time when you had to resolve a conflict within your team.",
                "Describe a situation where you had to build consensus among stakeholders with different priorities."
            ],
            "problem_solving": [
                "Tell me about the most complex problem you've had to solve.",
                "Describe a time when you had to find a creative solution to a challenging problem.",
                "Give me an example of when you had to solve a problem with limited resources.",
                "Tell me about a time when your first approach to solving a problem didn't work.",
                "Describe a situation where you had to analyze data to make a decision."
            ],
            "adaptability": [
                "Tell me about a time when you had to adapt to a significant change at work.",
                "Describe a situation where you had to learn something completely new quickly.",
                "Give me an example of when priorities changed suddenly and you had to adjust.",
                "Tell me about a time when you had to work in an ambiguous situation.",
                "Describe a situation where you had to change your communication style for different audiences."
            ],
            "communication": [
                "Tell me about a time when you had to explain a complex technical concept to non-technical stakeholders.",
                "Describe a situation where you had to deliver bad news to your team or manager.",
                "Give me an example of when you had to present your ideas to senior leadership.",
                "Tell me about a time when you had to persuade someone to see things from your perspective.", 
                "Describe a situation where you had to gather requirements from multiple stakeholders."
            ],
            "innovation": [
                "Tell me about a time when you came up with a novel solution to a problem.",
                "Describe a situation where you challenged the status quo.",
                "Give me an example of when you implemented a process improvement.",
                "Tell me about a time when you took a calculated risk that paid off.",
                "Describe a situation where you had to think outside the box."
            ],
            "customer_focus": [
                "Tell me about a time when you went above and beyond for a customer.",
                "Describe a situation where you had to balance customer needs with business constraints.",
                "Give me an example of when you received difficult customer feedback and how you handled it.",
                "Tell me about a time when you identified and solved a customer pain point.",
                "Describe a situation where you had to make a decision that prioritized customer experience."
            ],
            "conflict_resolution": [
                "Tell me about a time when you had to mediate a disagreement between team members.", 
                "Describe a situation where you disagreed with your manager's approach.",
                "Give me an example of when you had to address a performance issue with a colleague.",
                "Tell me about a time when you had to navigate competing priorities from different stakeholders.",
                "Describe a situation where you had to find a win-win solution in a difficult negotiation."
            ]
        }

        # Generate diverse prompts
        prompts = []
        prompt_id = 1

        for competency, questions in competency_prompts.items():
            for question in questions:
                # Create variations for different experience levels
                variations = [
                    {"level": "junior", "context": "early in your career"},
                    {"level": "mid", "context": "as you gained more experience"},
                    {"level": "senior", "context": "in a senior role"}
                ]
                
                for variation in variations:
                    if len(prompts) >= count:
                        break
                        
                    prompt = {
                        "id": f"prompt_{prompt_id:03d}",
                        "question": question,
                        "competency": competency,
                        "experience_level": variation["level"],
                        "context_hint": f"Think about an example {variation['context']}",
                        "evaluation_focus": self._get_evaluation_focus(competency),
                        "follow_up_questions": self._get_follow_up_questions(competency),
                        "created_at": datetime.now().isoformat()
                    }
                    prompts.append(prompt)
                    prompt_id += 1

        # Shuffle to avoid clustering by competency
        random.shuffle(prompts)
        return prompts[:count]

    def _get_evaluation_focus(self, competency: str) -> List[str]:
        """Get specific evaluation criteria for each competency"""
        focus_map = {
            "leadership": [
                "Demonstrates influence without formal authority",
                "Takes ownership of team outcomes", 
                "Shows ability to motivate and guide others",
                "Makes difficult decisions confidently"
            ],
            "teamwork": [
                "Collaborates effectively with diverse groups",
                "Contributes to team success beyond individual tasks",
                "Handles interpersonal challenges constructively",
                "Builds consensus and shared understanding"
            ],
            "problem_solving": [
                "Breaks down complex problems systematically", 
                "Uses analytical thinking and data",
                "Considers multiple solution approaches",
                "Learns from failed attempts"
            ],
            "adaptability": [
                "Handles ambiguity and uncertainty well",
                "Learns quickly in new situations",
                "Adjusts approach based on feedback",
                "Maintains effectiveness during change"
            ],
            "communication": [
                "Tailors message to audience needs",
                "Listens actively and responds appropriately", 
                "Presents complex information clearly",
                "Builds rapport and trust through communication"
            ],
            "innovation": [
                "Challenges existing approaches constructively",
                "Generates creative solutions",
                "Takes calculated risks for improvement",
                "Implements ideas effectively"
            ],
            "customer_focus": [
                "Understands and advocates for customer needs",
                "Balances customer and business perspectives",
                "Seeks customer feedback proactively",
                "Delivers value from customer perspective"
            ],
            "conflict_resolution": [
                "Addresses conflicts directly and constructively",
                "Finds win-win solutions",
                "Maintains relationships during disagreements",
                "Prevents escalation through early intervention"
            ]
        }
        return focus_map.get(competency, ["Demonstrates competency effectively"])

    def _get_follow_up_questions(self, competency: str) -> List[str]:
        """Get potential follow-up questions for deeper exploration"""
        followup_map = {
            "leadership": [
                "How did you measure the success of your leadership approach?",
                "What would you do differently if you faced a similar situation again?",
                "How did you ensure team buy-in for your decisions?"
            ],
            "teamwork": [
                "What specific role did you play in the team's success?",
                "How did you handle any resistance or disagreement?",
                "What did you learn about effective collaboration from this experience?"
            ],
            "problem_solving": [
                "What other approaches did you consider?",
                "How did you validate that your solution was working?",
                "What tools or resources did you use in your analysis?"
            ],
            "adaptability": [
                "What was the most challenging aspect of the change?",
                "How did you help others adapt to the new situation?",
                "What strategies do you use to stay flexible in uncertain situations?"
            ],
            "communication": [
                "How did you prepare for this communication?",
                "What feedback did you receive on your communication style?",
                "How did you ensure your message was understood?"
            ],
            "innovation": [
                "What inspired this innovative approach?",
                "How did you overcome resistance to your new idea?",
                "What was the long-term impact of your innovation?"
            ],
            "customer_focus": [
                "How did you measure customer satisfaction with the outcome?",
                "What did you learn about customer needs from this experience?",
                "How do you balance customer requests with technical constraints?"
            ],
            "conflict_resolution": [
                "What techniques did you use to de-escalate the situation?",
                "How did you ensure all parties felt heard?",
                "What was the long-term impact on working relationships?"
            ]
        }
        return followup_map.get(competency, ["Can you provide more specific details about your approach?"])

    def create_expert_collection_package(self, prompt_count: int = 200) -> Dict[str, Any]:
        """
        Create a complete package for expert response collection
        """
        
        print("=== Creating Expert Response Collection Package ===")
        
        # Generate prompts
        prompts = self.generate_response_prompts(prompt_count)
        
        # Create instructions for experts
        expert_instructions = {
            "overview": "Instructions for providing high-quality STAR method responses",
            "purpose": "These responses will be used to train an AI system to evaluate behavioral interviews",
            "expectations": [
                "Provide realistic, detailed responses using the STAR method",
                "Draw from actual experiences when possible",
                "Vary response quality to include excellent, good, and poor examples",
                "Ensure personal accountability (use 'I' rather than 'we')",
                "Include specific details, metrics, and outcomes where appropriate"
            ],
            "star_method_reminder": {
                "situation": "Set the context - Where, when, who was involved?",
                "task": "What was your specific responsibility or goal?", 
                "action": "What specific steps did you take? (Focus on YOUR actions)",
                "result": "What was the outcome? Include metrics if possible. What did you learn?"
            },
            "response_guidelines": [
                "Aim for 200-400 words per response",
                "Be specific rather than general",
                "Include quantifiable results when possible",
                "Show learning and growth from the experience",
                "Demonstrate the target competency clearly"
            ],
            "quality_levels_to_include": {
                "excellent": "30% - Outstanding examples with all STAR components, specific details, strong results",
                "good": "40% - Solid examples with clear STAR structure and good details",
                "adequate": "20% - Basic examples that meet minimum requirements",
                "poor": "10% - Weak examples with vague details or missing components"
            }
        }

        # Create collection template
        collection_template = {
            "expert_info": {
                "name": "[Expert Name]",
                "background": "[Brief description of relevant experience]", 
                "years_experience": "[Number]",
                "specialization": "[Technical area or role type]"
            },
            "responses": [
                {
                    "prompt_id": "prompt_001",
                    "question": "[Question text]",
                    "competency": "[Target competency]",
                    "response": {
                        "situation": "[Your response]",
                        "task": "[Your response]", 
                        "action": "[Your response]",
                        "result": "[Your response]"
                    },
                    "self_assessment": {
                        "quality_level": "[excellent/good/adequate/poor]",
                        "competency_demonstration": "[How well does this demonstrate the target competency?]",
                        "areas_for_improvement": "[What could make this response stronger?]"
                    }
                }
            ]
        }

        # Save all components
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        prompts_file = self.output_dir / f"expert_prompts_{ts}.json"
        with prompts_file.open("w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "purpose": "Behavioral interview prompts for expert response collection",
                    "count": len(prompts)
                },
                "prompts": prompts
            }, f, ensure_ascii=False, indent=2)

        instructions_file = self.output_dir / f"expert_instructions_{ts}.json"
        with instructions_file.open("w", encoding="utf-8") as f:
            json.dump(expert_instructions, f, ensure_ascii=False, indent=2)

        template_file = self.output_dir / f"collection_template_{ts}.json"
        with template_file.open("w", encoding="utf-8") as f:
            json.dump(collection_template, f, ensure_ascii=False, indent=2)

        # Create comprehensive package summary
        package_summary = {
            "package_name": "Expert STAR Response Collection Package",
            "created_at": datetime.now().isoformat(),
            "components": {
                "prompts": {
                    "file": str(prompts_file),
                    "count": len(prompts),
                    "competencies_covered": list(set(p["competency"] for p in prompts)),
                    "experience_levels": ["junior", "mid", "senior"]
                },
                "instructions": {
                    "file": str(instructions_file),
                    "description": "Detailed guidelines for expert respondents"
                },
                "template": {
                    "file": str(template_file),
                    "description": "JSON template for structured response collection"
                }
            },
            "collection_plan": {
                "target_experts": "3-5 experienced professionals",
                "responses_per_expert": "40-60 responses",
                "total_target": "200+ labeled responses",
                "timeline": "2-3 weeks for collection + 1 week for validation"
            },
            "success_metrics": [
                "High inter-rater reliability (>0.8)",
                "Balanced distribution across competencies",
                "Quality level distribution: 30% excellent, 40% good, 20% adequate, 10% poor",
                "Sufficient volume for model training (200+ responses)"
            ]
        }

        package_file = self.output_dir / f"collection_package_{ts}.json"
        with package_file.open("w", encoding="utf-8") as f:
            json.dump(package_summary, f, ensure_ascii=False, indent=2)

        print(f"✅ Expert prompts created: {prompts_file}")
        print(f"✅ Instructions created: {instructions_file}")
        print(f"✅ Collection template created: {template_file}")
        print(f"✅ Package summary: {package_file}")

        return {
            "package_file": str(package_file),
            "prompts_file": str(prompts_file),
            "instructions_file": str(instructions_file),
            "template_file": str(template_file),
            "prompt_count": len(prompts),
            "competencies": list(set(p["competency"] for p in prompts))
        }

    def run_collection_setup(self, prompt_count: int = 200) -> Dict[str, Any]:
        """Set up the complete expert response collection framework"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            package_info = self.create_expert_collection_package(prompt_count)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "prompts_generated": package_info["prompt_count"],
                "competencies_covered": len(package_info["competencies"]),
                "package_file": package_info["package_file"]
            }
            
            logger.log("expert_collection", "setup_framework", 
                      records=package_info["prompt_count"], success=True, metadata=meta)
            
            return meta
            
        except Exception as e:
            logger.log("expert_collection", "setup_framework", 
                      records=0, success=False, error=str(e))
            raise
