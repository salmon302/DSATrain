from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .acquisition_logger import AcquisitionLogger


@dataclass
class SystemDesignFetcher:
    data_dir: Path
    rate_limit_sleep: float = 2.0

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "system_design"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _fetch_page(self, url: str) -> str:
        """Fetch a web page with appropriate headers"""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DSATrain-SystemDesignFetcher/0.1 (Educational Research)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="ignore")

    def fetch_reddit_45_questions(self) -> Dict[str, Any]:
        """Fetch the famous 45 system design questions from Reddit"""
        print("=== Fetching Reddit 45 System Design Questions ===")
        
        reddit_url = "https://www.reddit.com/r/leetcode/comments/1j9a8u6/45_system_design_questions_i_curated_for/"
        
        try:
            # Fetch the Reddit page in JSON format
            json_url = reddit_url + ".json"
            content = self._fetch_page(json_url)
            reddit_data = json.loads(content)
            
            # Extract the post content
            post_data = reddit_data[0]['data']['children'][0]['data']
            post_title = post_data['title']
            post_text = post_data.get('selftext', '')
            
            # Parse questions from the post text
            questions = self._extract_questions_from_text(post_text)
            
            result = {
                "source": "Reddit r/leetcode",
                "post_title": post_title,
                "post_url": reddit_url,
                "total_questions": len(questions),
                "questions": questions,
                "collected_at": datetime.now().isoformat()
            }
            
            # Save the raw data
            output_file = self.raw_dir / "reddit_45_questions.json"
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Extracted {len(questions)} questions from Reddit post")
            return result
            
        except Exception as e:
            print(f"❌ Failed to fetch Reddit questions: {e}")
            # Return hardcoded version based on research document
            return self._get_fallback_questions()

    def _extract_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract system design questions from Reddit post text"""
        questions = []
        
        # Common patterns for system design questions
        patterns = [
            r"(?:Design|Build|Create|Implement)\s+([^.\n]+)",
            r"How would you (?:design|build|implement)\s+([^?\n]+)",
            r"\d+\.\s*([^.\n]+(?:system|service|platform|app)[^.\n]*)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question_text = match.group(1).strip()
                if len(question_text) > 10 and any(keyword in question_text.lower() 
                                                 for keyword in ['system', 'design', 'service', 'platform', 'app', 'database']):
                    questions.append({
                        "question": question_text,
                        "type": "system_design",
                        "difficulty": "intermediate",
                        "companies": ["Google", "Facebook", "Amazon", "Microsoft"],  # Common for system design
                        "extracted_by": "regex_pattern"
                    })
        
        return questions[:45]  # Limit to 45 as mentioned

    def _get_fallback_questions(self) -> Dict[str, Any]:
        """Fallback questions based on research document and common patterns"""
        
        fallback_questions = [
            "Design a Distributed Metrics Logging and Aggregation System",
            "Design Google Drive",
            "Design a URL Shortener (like bit.ly)",
            "Design a Social Media Feed",
            "Design a Chat System (like WhatsApp)",
            "Design a Video Streaming Service (like YouTube)",
            "Design a Ride-Sharing Service (like Uber)",
            "Design a Search Engine",
            "Design a Recommendation System",
            "Design a Distributed Cache",
            "Design a Rate Limiter",
            "Design a Load Balancer",
            "Design a Notification System",
            "Design a Payment System",
            "Design a Content Delivery Network (CDN)",
            "Design a Distributed Database",
            "Design a Message Queue",
            "Design a File Storage System",
            "Design a Web Crawler",
            "Design a Real-time Analytics System",
            "Design a Booking System",
            "Design a E-commerce Platform",
            "Design a Gaming Leaderboard",
            "Design a Stock Trading System",
            "Design a Collaborative Editor (like Google Docs)",
            "Design a Music Streaming Service",
            "Design a Job Scheduler",
            "Design a Monitoring System",
            "Design a Authentication System",
            "Design a API Gateway",
            "Design a Distributed Lock Service",
            "Design a Time Series Database",
            "Design a Event Streaming Platform",
            "Design a Graph Database",
            "Design a Machine Learning Platform",
            "Design a Container Orchestration System",
            "Design a Backup and Recovery System",
            "Design a Logging Infrastructure",
            "Design a Configuration Management System",
            "Design a Service Discovery System",
            "Design a Distributed Consensus System",
            "Design a Blockchain System",
            "Design a IoT Data Processing Platform",
            "Design a Real-time Bidding System",
            "Design a Fraud Detection System"
        ]
        
        questions = []
        for i, q in enumerate(fallback_questions):
            questions.append({
                "question": q,
                "type": "system_design",
                "difficulty": "intermediate" if i < 30 else "advanced",
                "companies": ["Google", "Facebook", "Amazon", "Microsoft", "Netflix", "Uber"],
                "topics": self._infer_topics(q),
                "extracted_by": "fallback_curated"
            })
        
        return {
            "source": "Curated Fallback",
            "post_title": "45 System Design Questions (Curated)",
            "total_questions": len(questions),
            "questions": questions,
            "collected_at": datetime.now().isoformat()
        }

    def _infer_topics(self, question: str) -> List[str]:
        """Infer technical topics from question text"""
        topics = []
        question_lower = question.lower()
        
        topic_keywords = {
            "databases": ["database", "sql", "nosql", "storage"],
            "caching": ["cache", "redis", "memcached"],
            "messaging": ["queue", "message", "kafka", "streaming"],
            "networking": ["cdn", "load balancer", "api gateway"],
            "scalability": ["distributed", "scale", "partition", "shard"],
            "real_time": ["real-time", "realtime", "live", "streaming"],
            "security": ["auth", "security", "payment", "fraud"],
            "analytics": ["analytics", "metrics", "monitoring", "logging"],
            "search": ["search", "index", "crawler", "recommendation"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]

    def fetch_github_collections(self) -> List[Dict[str, Any]]:
        """Fetch system design question collections from GitHub"""
        print("=== Fetching GitHub System Design Collections ===")
        
        github_repos = [
            {
                "repo": "donnemartin/system-design-primer",
                "api_url": "https://api.github.com/repos/donnemartin/system-design-primer",
                "description": "System design primer with examples and solutions"
            },
            {
                "repo": "checkcheckzz/system-design-interview",
                "api_url": "https://api.github.com/repos/checkcheckzz/system-design-interview",
                "description": "System design interview questions and solutions"
            },
            {
                "repo": "shashank88/system_design",
                "api_url": "https://api.github.com/repos/shashank88/system_design",
                "description": "System design concepts and interview questions"
            }
        ]
        
        results = []
        
        for repo_info in github_repos:
            try:
                print(f"Fetching: {repo_info['repo']}")
                
                # Get repository information
                req = urllib.request.Request(
                    repo_info["api_url"],
                    headers={
                        "User-Agent": "DSATrain-SystemDesignFetcher/0.1",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    repo_data = json.loads(response.read().decode("utf-8"))
                
                result = {
                    "repository": repo_info["repo"],
                    "description": repo_info["description"],
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                    "url": repo_data.get("html_url"),
                    "topics": repo_data.get("topics", []),
                    "language": repo_data.get("language"),
                    "last_updated": repo_data.get("updated_at"),
                    "collected_at": datetime.now().isoformat()
                }
                
                results.append(result)
                print(f"✅ {repo_info['repo']}: {result['stars']} stars")
                
                time.sleep(self.rate_limit_sleep)
                
            except Exception as e:
                print(f"❌ Failed to fetch {repo_info['repo']}: {e}")
                results.append({
                    "repository": repo_info["repo"],
                    "description": repo_info["description"],
                    "error": str(e),
                    "collected_at": datetime.now().isoformat()
                })
        
        return results

    def create_expanded_collection(self) -> Dict[str, Any]:
        """Create an expanded collection of system design scenarios"""
        print("=== Creating Expanded System Design Collection ===")
        
        # Advanced scenarios based on research document architectural patterns
        advanced_scenarios = [
            {
                "scenario": "Design a globally distributed database with eventual consistency",
                "difficulty": "advanced",
                "key_concepts": ["CAP theorem", "eventual consistency", "vector clocks", "conflict resolution"],
                "companies": ["Google", "Amazon", "Facebook"],
                "evaluation_focus": ["trade-off analysis", "consistency models", "partition tolerance"]
            },
            {
                "scenario": "Design a real-time collaborative editing system",
                "difficulty": "advanced", 
                "key_concepts": ["operational transformation", "conflict resolution", "real-time sync"],
                "companies": ["Google", "Microsoft", "Notion"],
                "evaluation_focus": ["concurrency control", "user experience", "data consistency"]
            },
            {
                "scenario": "Design a microservices architecture for e-commerce",
                "difficulty": "advanced",
                "key_concepts": ["service mesh", "API gateway", "distributed transactions", "saga pattern"],
                "companies": ["Amazon", "eBay", "Shopify"],
                "evaluation_focus": ["service boundaries", "data consistency", "failure handling"]
            },
            {
                "scenario": "Design a machine learning inference platform",
                "difficulty": "advanced",
                "key_concepts": ["model serving", "A/B testing", "feature stores", "model versioning"],
                "companies": ["Google", "Netflix", "Uber"],
                "evaluation_focus": ["scalability", "latency requirements", "model lifecycle"]
            },
            {
                "scenario": "Design a blockchain-based cryptocurrency system",
                "difficulty": "expert",
                "key_concepts": ["consensus algorithms", "merkle trees", "proof of work", "smart contracts"],
                "companies": ["Coinbase", "Ripple", "Ethereum"],
                "evaluation_focus": ["security", "decentralization", "scalability trilemma"]
            }
        ]
        
        # Intermediate scenarios for skill building
        intermediate_scenarios = [
            {
                "scenario": "Design a URL shortener with custom domains",
                "difficulty": "intermediate",
                "key_concepts": ["hashing", "base62 encoding", "database sharding", "caching"],
                "companies": ["Bitly", "Google", "Twitter"],
                "evaluation_focus": ["URL generation strategies", "database design", "caching strategy"]
            },
            {
                "scenario": "Design a rate limiting system",
                "difficulty": "intermediate",
                "key_concepts": ["token bucket", "sliding window", "distributed rate limiting"],
                "companies": ["Twitter", "GitHub", "Stripe"],
                "evaluation_focus": ["algorithm choice", "storage considerations", "performance"]
            },
            {
                "scenario": "Design a notification system",
                "difficulty": "intermediate",
                "key_concepts": ["push notifications", "email delivery", "message queues", "fan-out"],
                "companies": ["Facebook", "Instagram", "Slack"],
                "evaluation_focus": ["delivery guarantees", "personalization", "scale"]
            }
        ]
        
        expanded_collection = {
            "collection_name": "Expanded System Design Scenarios",
            "total_scenarios": len(advanced_scenarios) + len(intermediate_scenarios),
            "difficulty_levels": ["intermediate", "advanced", "expert"],
            "advanced_scenarios": advanced_scenarios,
            "intermediate_scenarios": intermediate_scenarios,
            "evaluation_framework": {
                "technical_depth": "Assess understanding of core concepts and trade-offs",
                "scalability_thinking": "Evaluate ability to reason about scale and performance",
                "design_process": "Observe systematic approach to problem decomposition",
                "communication": "Assess clarity in explaining technical decisions"
            },
            "created_at": datetime.now().isoformat()
        }
        
        return expanded_collection

    def run_acquisition(self) -> Dict[str, Any]:
        """Run complete system design scenarios acquisition"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            print("=== System Design Scenarios Acquisition ===")
            
            # Fetch Reddit 45 questions
            reddit_questions = self.fetch_reddit_45_questions()
            
            # Fetch GitHub collections
            github_collections = self.fetch_github_collections()
            
            # Create expanded collection
            expanded_collection = self.create_expanded_collection()
            
            # Save all results
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save GitHub collections
            github_file = self.raw_dir / f"github_collections_{ts}.json"
            with github_file.open("w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "collections": github_collections
                }, f, ensure_ascii=False, indent=2)
            
            # Save expanded collection
            expanded_file = self.raw_dir / f"expanded_scenarios_{ts}.json"
            with expanded_file.open("w", encoding="utf-8") as f:
                json.dump(expanded_collection, f, ensure_ascii=False, indent=2)
            
            # Create comprehensive summary
            summary = {
                "timestamp": datetime.now().isoformat(),
                "reddit_questions": reddit_questions["total_questions"],
                "github_repositories": len(github_collections),
                "expanded_scenarios": expanded_collection["total_scenarios"],
                "total_scenarios": reddit_questions["total_questions"] + expanded_collection["total_scenarios"],
                "files_created": [
                    str(self.raw_dir / "reddit_45_questions.json"),
                    str(github_file),
                    str(expanded_file)
                ]
            }
            
            summary_file = self.raw_dir / f"system_design_summary_{ts}.json"
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": summary["total_scenarios"],
                "output_files": summary["files_created"],
                "summary_file": str(summary_file)
            }
            
            logger.log("system_design", "scenario_collection", 
                      records=summary["total_scenarios"], success=True, metadata=meta)
            
            return meta
            
        except Exception as e:
            logger.log("system_design", "scenario_collection", 
                      records=0, success=False, error=str(e))
            raise
