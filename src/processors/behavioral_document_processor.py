"""
Behavioral Document Processing Pipeline
Extracts structured questions from PDFs/DOCX and builds competency taxonomy
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import subprocess
import sys


@dataclass
class BehavioralDocumentProcessor:
    """Processes behavioral interview documents and extracts structured data"""
    
    data_dir: Path
    output_dir: Optional[Path] = None
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.data_dir / "processed" / "behavioral"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.raw_dir = self.data_dir / "raw" / "behavioral_resources"

    def _install_document_processors(self) -> bool:
        """Install required document processing libraries"""
        try:
            import docx2txt
            return True
        except ImportError:
            print("Installing document processing libraries...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "docx2txt", "beautifulsoup4"
                ])
                return True
            except subprocess.CalledProcessError as e:
                print(f"Failed to install document processors: {e}")
                return False

    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            import docx2txt
            return docx2txt.process(str(file_path))
        except Exception as e:
            print(f"Error extracting from DOCX {file_path}: {e}")
            return ""

    def _extract_text_from_html(self, file_path: Path) -> str:
        """Extract text from HTML files"""
        try:
            from bs4 import BeautifulSoup
            
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text()
        except Exception as e:
            print(f"Error extracting from HTML {file_path}: {e}")
            return ""

    def _extract_questions_from_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Extract behavioral questions from text using pattern matching"""
        questions = []
        
        # Common question patterns
        question_patterns = [
            r"Tell me about a time when[^?]*\?",
            r"Describe a situation where[^?]*\?",
            r"Give an example of[^?]*\?",
            r"How would you handle[^?]*\?",
            r"What would you do if[^?]*\?",
            r"Share an experience[^?]*\?",
            r"Can you think of a time[^?]*\?",
            r"Have you ever[^?]*\?",
            r"\d+\.\s*[A-Z][^?]*\?"  # Numbered questions
        ]
        
        # Find all questions
        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                question_text = match.group(0).strip()
                
                # Clean up the question
                question_text = re.sub(r'\s+', ' ', question_text)
                question_text = question_text.strip(' \n\r\t.')
                
                if len(question_text) > 20 and len(question_text) < 500:
                    questions.append({
                        "question": question_text,
                        "source": source,
                        "competency": self._infer_competency(question_text),
                        "type": "behavioral",
                        "difficulty": self._infer_difficulty(question_text)
                    })
        
        return questions

    def _infer_competency(self, question: str) -> str:
        """Infer competency category from question text"""
        question_lower = question.lower()
        
        competency_keywords = {
            "leadership": ["lead", "leadership", "manage", "mentor", "guide", "direct", "supervise"],
            "teamwork": ["team", "collaborate", "cooperation", "work with others", "group"],
            "problem_solving": ["problem", "solve", "challenge", "difficult", "obstacle", "issue"],
            "communication": ["communicate", "explain", "present", "discuss", "feedback", "convince"],
            "adaptability": ["change", "adapt", "flexible", "different", "new", "unexpected"],
            "conflict_resolution": ["conflict", "disagree", "tension", "difficult person", "resolution"],
            "time_management": ["deadline", "priority", "time", "schedule", "manage", "urgent"],
            "decision_making": ["decision", "choose", "decide", "judgment", "analysis"],
            "innovation": ["creative", "innovative", "improve", "better way", "efficiency"],
            "customer_focus": ["customer", "client", "user", "service", "satisfaction"]
        }
        
        scores = {}
        for competency, keywords in competency_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[competency] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return "general"

    def _infer_difficulty(self, question: str) -> str:
        """Infer question difficulty based on complexity"""
        question_lower = question.lower()
        
        # Complex scenarios usually indicate harder questions
        complexity_indicators = [
            "multiple", "complex", "challenging", "difficult", "senior", "executive",
            "strategic", "large scale", "cross-functional", "high stakes"
        ]
        
        simple_indicators = [
            "simple", "basic", "first time", "recent", "small", "individual"
        ]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in question_lower)
        simplicity_score = sum(1 for indicator in simple_indicators if indicator in question_lower)
        
        if complexity_score > simplicity_score:
            return "hard"
        elif simplicity_score > complexity_score:
            return "easy"
        else:
            return "medium"

    def process_university_documents(self) -> List[Dict[str, Any]]:
        """Process university behavioral question documents"""
        print("=== Processing University Documents ===")
        
        if not self._install_document_processors():
            print("❌ Could not install document processors")
            return []
        
        all_questions = []
        
        # Process DOCX files
        docx_files = list(self.raw_dir.glob("*.docx"))
        for docx_file in docx_files:
            print(f"Processing DOCX: {docx_file.name}")
            text = self._extract_text_from_docx(docx_file)
            if text:
                questions = self._extract_questions_from_text(text, docx_file.stem)
                all_questions.extend(questions)
                print(f"  Extracted {len(questions)} questions")
        
        # Process HTML files
        html_files = list(self.raw_dir.glob("*.html"))
        for html_file in html_files:
            print(f"Processing HTML: {html_file.name}")
            text = self._extract_text_from_html(html_file)
            if text:
                questions = self._extract_questions_from_text(text, html_file.stem)
                all_questions.extend(questions)
                print(f"  Extracted {len(questions)} questions")
        
        print(f"✅ Processed {len(all_questions)} total questions from university documents")
        return all_questions

    def build_competency_taxonomy(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical competency framework"""
        print("=== Building Competency Taxonomy ===")
        
        # Core Google competencies based on research
        google_competencies = {
            "googleyness": {
                "description": "Google-specific cultural fit and mindset",
                "sub_competencies": [
                    "intellectual_humility",
                    "collaborative_spirit", 
                    "comfort_with_ambiguity",
                    "fun_and_positive_attitude"
                ],
                "questions": []
            },
            "general_cognitive_ability": {
                "description": "Problem-solving and analytical thinking",
                "sub_competencies": [
                    "problem_solving",
                    "analytical_thinking",
                    "learning_agility",
                    "decision_making"
                ],
                "questions": []
            },
            "leadership": {
                "description": "Leadership and influence capabilities", 
                "sub_competencies": [
                    "emerging_leadership",
                    "thought_leadership",
                    "team_leadership",
                    "organizational_leadership"
                ],
                "questions": []
            },
            "role_related_knowledge": {
                "description": "Technical and domain expertise",
                "sub_competencies": [
                    "technical_depth",
                    "system_design",
                    "coding_ability",
                    "domain_knowledge"
                ],
                "questions": []
            }
        }
        
        # Map extracted questions to Google competencies
        competency_mapping = {
            "leadership": "leadership",
            "teamwork": "googleyness", 
            "problem_solving": "general_cognitive_ability",
            "communication": "googleyness",
            "adaptability": "general_cognitive_ability",
            "conflict_resolution": "leadership",
            "time_management": "general_cognitive_ability",
            "decision_making": "general_cognitive_ability",
            "innovation": "general_cognitive_ability",
            "customer_focus": "googleyness"
        }
        
        # Categorize questions
        for question in questions:
            original_competency = question.get("competency", "general")
            google_competency = competency_mapping.get(original_competency, "general_cognitive_ability")
            
            if google_competency in google_competencies:
                google_competencies[google_competency]["questions"].append(question)
        
        # Add statistics
        for competency in google_competencies:
            question_count = len(google_competencies[competency]["questions"])
            google_competencies[competency]["question_count"] = question_count
            
            # Difficulty distribution
            difficulties = [q.get("difficulty", "medium") for q in google_competencies[competency]["questions"]]
            difficulty_dist = {
                "easy": difficulties.count("easy"),
                "medium": difficulties.count("medium"), 
                "hard": difficulties.count("hard")
            }
            google_competencies[competency]["difficulty_distribution"] = difficulty_dist
        
        print(f"✅ Built competency taxonomy with {len(google_competencies)} core competencies")
        return google_competencies

    def extract_googleyness_criteria(self) -> Dict[str, Any]:
        """Extract Googleyness criteria from official documents"""
        print("=== Extracting Googleyness Criteria ===")
        
        # Check for Google official documents
        google_docs_dir = self.data_dir / "raw" / "google_official"
        
        googleyness_criteria = {
            "core_values": [
                "Focus on the user and all else will follow",
                "It's best to do one thing really, really well",
                "Fast is better than slow",
                "Democracy on the web works",
                "You don't need to be at your desk to need an answer",
                "You can make money without doing evil",
                "There's always more information out there",
                "The need for information crosses all borders",
                "You can be serious without a suit",
                "Great just isn't good enough"
            ],
            "behavioral_indicators": {
                "intellectual_humility": [
                    "Admits when wrong or uncertain",
                    "Seeks feedback and learns from mistakes",
                    "Values diverse perspectives"
                ],
                "collaborative_spirit": [
                    "Works effectively across teams",
                    "Helps others succeed",
                    "Shares knowledge and resources"
                ],
                "comfort_with_ambiguity": [
                    "Thrives in uncertain situations",
                    "Makes decisions with incomplete information",
                    "Adapts quickly to change"
                ],
                "positive_attitude": [
                    "Maintains optimism under pressure",
                    "Brings energy to team interactions",
                    "Focuses on solutions rather than problems"
                ]
            },
            "assessment_questions": []
        }
        
        # If Google docs exist, extract additional criteria
        if google_docs_dir.exists():
            html_files = list(google_docs_dir.glob("*.html"))
            for html_file in html_files:
                if "careers" in html_file.name.lower() or "how_we_hire" in html_file.name.lower():
                    text = self._extract_text_from_html(html_file)
                    # Extract relevant criteria from Google's official documentation
                    # This is a simplified extraction - in practice would be more sophisticated
                    if "googleyness" in text.lower() or "culture" in text.lower():
                        print(f"  Found relevant content in {html_file.name}")
        
        print("✅ Extracted Googleyness criteria")
        return googleyness_criteria

    def generate_conversation_templates(self, taxonomy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI conversation flow templates"""
        print("=== Generating Conversation Templates ===")
        
        conversation_templates = {}
        
        for competency, data in taxonomy.items():
            templates = {
                "opening_questions": [],
                "follow_up_prompts": [],
                "probing_questions": [],
                "evaluation_criteria": []
            }
            
            # Create opening questions for each competency
            if competency == "googleyness":
                templates["opening_questions"] = [
                    "Tell me about a time when you had to collaborate with someone whose working style was very different from yours.",
                    "Describe a situation where you had to work with incomplete information.",
                    "Give me an example of when you had to learn something completely new."
                ]
            elif competency == "general_cognitive_ability":
                templates["opening_questions"] = [
                    "Walk me through how you would solve a complex problem you've never encountered before.",
                    "Tell me about a time when you had to make a difficult decision with limited time.",
                    "Describe your approach to breaking down a large, ambiguous project."
                ]
            elif competency == "leadership":
                templates["opening_questions"] = [
                    "Tell me about a time when you had to influence someone without having direct authority over them.",
                    "Describe a situation where you had to lead a team through a challenging period.",
                    "Give me an example of when you had to make an unpopular decision."
                ]
            
            # Follow-up prompts
            templates["follow_up_prompts"] = [
                "Can you tell me more about that?",
                "What was your specific role in that situation?",
                "How did you decide on that approach?",
                "What would you do differently if you faced that situation again?",
                "What was the outcome?",
                "How did others react to your decision?"
            ]
            
            # Probing questions
            templates["probing_questions"] = [
                "What alternatives did you consider?",
                "How did you measure success?",
                "What challenges did you face?",
                "Who else was involved in the decision?",
                "What did you learn from this experience?"
            ]
            
            # Evaluation criteria based on STAR method
            templates["evaluation_criteria"] = [
                {
                    "situation": "Clearly describes the context and background",
                    "weight": 0.2
                },
                {
                    "task": "Explains their specific responsibility or goal", 
                    "weight": 0.2
                },
                {
                    "action": "Details the specific actions they took",
                    "weight": 0.4
                },
                {
                    "result": "Describes measurable outcomes and learnings",
                    "weight": 0.2
                }
            ]
            
            conversation_templates[competency] = templates
        
        print(f"✅ Generated conversation templates for {len(conversation_templates)} competencies")
        return conversation_templates

    def run_behavioral_processing_pipeline(self) -> Dict[str, Any]:
        """Run complete behavioral document processing pipeline"""
        print("=== Behavioral Document Processing Pipeline ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_status": "running",
            "components": {}
        }
        
        try:
            # 1. Process university documents
            print("\n1. Processing university behavioral documents...")
            questions = self.process_university_documents()
            results["components"]["questions_extracted"] = len(questions)
            
            # 2. Build competency taxonomy
            print("\n2. Building competency taxonomy...")
            taxonomy = self.build_competency_taxonomy(questions)
            
            # Save taxonomy
            taxonomy_file = self.output_dir / "competency_taxonomy.json"
            with taxonomy_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "total_questions": len(questions),
                        "total_competencies": len(taxonomy),
                        "timestamp": datetime.now().isoformat()
                    },
                    "taxonomy": taxonomy
                }, f, indent=2)
            results["components"]["taxonomy"] = str(taxonomy_file)
            
            # 3. Extract Googleyness criteria
            print("\n3. Extracting Googleyness criteria...")
            googleyness = self.extract_googleyness_criteria()
            
            # Save criteria
            criteria_file = self.output_dir / "googleyness_criteria.json"
            with criteria_file.open("w", encoding="utf-8") as f:
                json.dump(googleyness, f, indent=2)
            results["components"]["googleyness"] = str(criteria_file)
            
            # 4. Generate conversation templates
            print("\n4. Generating conversation templates...")
            templates = self.generate_conversation_templates(taxonomy)
            
            # Save templates
            templates_file = self.output_dir / "conversation_templates.json"
            with templates_file.open("w", encoding="utf-8") as f:
                json.dump(templates, f, indent=2)
            results["components"]["templates"] = str(templates_file)
            
            # 5. Save all extracted questions
            questions_file = self.output_dir / "behavioral_questions_structured.json"
            with questions_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "total_questions": len(questions),
                        "extraction_date": datetime.now().isoformat(),
                        "sources_processed": list(set(q.get("source", "") for q in questions))
                    },
                    "questions": questions
                }, f, indent=2)
            results["components"]["structured_questions"] = str(questions_file)
            
            results["pipeline_status"] = "success"
            results["total_questions_processed"] = len(questions)
            results["competencies_identified"] = len(taxonomy)
            
            # Save pipeline summary
            summary_file = self.output_dir / "behavioral_processing_summary.json"
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ Behavioral processing complete!")
            print(f"Questions extracted: {len(questions)}")
            print(f"Competencies identified: {len(taxonomy)}")
            
            return results
            
        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            return results


def main():
    """Main function for running behavioral document processing"""
    from pathlib import Path
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    # Create processor
    processor = BehavioralDocumentProcessor(data_dir)
    
    # Run processing pipeline
    results = processor.run_behavioral_processing_pipeline()
    
    if results["pipeline_status"] == "success":
        print("\n🎉 Behavioral document processing completed successfully!")
    else:
        print(f"\n⚠️  Pipeline completed with status: {results['pipeline_status']}")
    
    return results


if __name__ == "__main__":
    main()
