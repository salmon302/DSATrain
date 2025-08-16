from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.collectors.acquisition_logger import AcquisitionLogger


@dataclass
class InterviewTrendMonitor:
    data_dir: Path
    rate_limit_sleep: float = 3.0

    @property
    def monitoring_dir(self) -> Path:
        p = self.data_dir / "monitoring"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def monitor_google_engineering_updates(self) -> Dict[str, Any]:
        """Monitor Google's engineering documentation for changes"""
        
        print("=== Monitoring Google Engineering Practice Updates ===")
        
        google_sources = [
            {
                "name": "Google Engineering Practices",
                "url": "https://google.github.io/eng-practices/",
                "type": "engineering_practices",
                "key_indicators": ["hiring", "interview", "code review", "standard"]
            },
            {
                "name": "Google Careers Blog",
                "url": "https://www.blog.google/inside-google/life-at-google/",
                "type": "careers_blog", 
                "key_indicators": ["hiring", "interview", "engineering", "career"]
            },
            {
                "name": "Google Developer Documentation",
                "url": "https://developers.google.com/",
                "type": "developer_docs",
                "key_indicators": ["best practices", "guidelines", "standards"]
            }
        ]
        
        monitoring_results = []
        
        for source in google_sources:
            try:
                print(f"Checking: {source['name']}")
                
                content = self._fetch_page(source["url"])
                changes = self._detect_content_changes(source, content)
                relevance_score = self._assess_hiring_relevance(content, source["key_indicators"])
                
                result = {
                    "source": source["name"],
                    "url": source["url"],
                    "type": source["type"],
                    "checked_at": datetime.now().isoformat(),
                    "content_hash": hash(content),
                    "content_length": len(content),
                    "changes_detected": changes["has_changes"],
                    "change_summary": changes["summary"],
                    "hiring_relevance_score": relevance_score,
                    "key_terms_found": self._extract_key_terms(content, source["key_indicators"])
                }
                
                monitoring_results.append(result)
                time.sleep(self.rate_limit_sleep)
                
            except Exception as e:
                print(f"❌ Failed to monitor {source['name']}: {e}")
                monitoring_results.append({
                    "source": source["name"],
                    "url": source["url"],
                    "checked_at": datetime.now().isoformat(),
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "monitoring_type": "google_engineering_updates",
            "timestamp": datetime.now().isoformat(),
            "sources_checked": len(google_sources),
            "successful_checks": len([r for r in monitoring_results if "error" not in r]),
            "results": monitoring_results
        }

    def monitor_interview_discussions(self) -> Dict[str, Any]:
        """Monitor public forums for Google interview discussion trends"""
        
        print("=== Monitoring Interview Discussion Trends ===")
        
        discussion_sources = [
            {
                "name": "Reddit r/cscareerquestions",
                "base_url": "https://www.reddit.com/r/cscareerquestions/search.json",
                "query": "google interview",
                "type": "reddit_search"
            },
            {
                "name": "Reddit r/leetcode", 
                "base_url": "https://www.reddit.com/r/leetcode/search.json",
                "query": "google",
                "type": "reddit_search"
            },
            {
                "name": "Hacker News",
                "base_url": "https://hn.algolia.com/api/v1/search",
                "query": "google interview",
                "type": "hn_search"
            }
        ]
        
        discussion_results = []
        
        for source in discussion_sources:
            try:
                print(f"Monitoring: {source['name']}")
                
                if source["type"] == "reddit_search":
                    trends = self._monitor_reddit_trends(source)
                elif source["type"] == "hn_search":
                    trends = self._monitor_hn_trends(source)
                else:
                    trends = {"status": "unsupported"}
                
                discussion_results.append({
                    "source": source["name"],
                    "checked_at": datetime.now().isoformat(),
                    "trends": trends
                })
                
                time.sleep(self.rate_limit_sleep)
                
            except Exception as e:
                print(f"❌ Failed to monitor {source['name']}: {e}")
                discussion_results.append({
                    "source": source["name"],
                    "checked_at": datetime.now().isoformat(),
                    "error": str(e)
                })
        
        return {
            "monitoring_type": "interview_discussions",
            "timestamp": datetime.now().isoformat(),
            "sources_checked": len(discussion_sources),
            "results": discussion_results
        }

    def monitor_competitive_platforms(self) -> Dict[str, Any]:
        """Monitor competitive programming platforms for trend changes"""
        
        print("=== Monitoring Competitive Platform Trends ===")
        
        # Check for new problem patterns, difficulty trends, company tags
        platform_checks = []
        
        # LeetCode trending problems (public data)
        try:
            leetcode_trends = self._check_leetcode_trends()
            platform_checks.append({
                "platform": "LeetCode",
                "checked_at": datetime.now().isoformat(),
                "trends": leetcode_trends
            })
        except Exception as e:
            platform_checks.append({
                "platform": "LeetCode",
                "checked_at": datetime.now().isoformat(),
                "error": str(e)
            })
        
        # Codeforces recent contests
        try:
            cf_trends = self._check_codeforces_trends()
            platform_checks.append({
                "platform": "Codeforces",
                "checked_at": datetime.now().isoformat(),
                "trends": cf_trends
            })
        except Exception as e:
            platform_checks.append({
                "platform": "Codeforces", 
                "checked_at": datetime.now().isoformat(),
                "error": str(e)
            })
        
        return {
            "monitoring_type": "competitive_platforms",
            "timestamp": datetime.now().isoformat(),
            "platforms_checked": len(platform_checks),
            "results": platform_checks
        }

    def _fetch_page(self, url: str) -> str:
        """Fetch web page content"""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DSATrain-TrendMonitor/0.1 (Educational Research)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="ignore")

    def _detect_content_changes(self, source: Dict[str, Any], current_content: str) -> Dict[str, Any]:
        """Detect changes from previous monitoring runs"""
        
        # Load previous content hash if available
        history_file = self.monitoring_dir / f"{source['name'].lower().replace(' ', '_')}_history.json"
        
        if history_file.exists():
            with history_file.open("r", encoding="utf-8") as f:
                history = json.load(f)
                
            previous_hash = history.get("last_content_hash")
            current_hash = hash(current_content)
            
            has_changes = previous_hash != current_hash
            
            # Update history
            history["last_content_hash"] = current_hash
            history["last_checked"] = datetime.now().isoformat()
            if has_changes:
                history["change_count"] = history.get("change_count", 0) + 1
                history["last_change"] = datetime.now().isoformat()
        else:
            # First time monitoring this source
            history = {
                "source": source["name"],
                "first_monitored": datetime.now().isoformat(),
                "last_content_hash": hash(current_content),
                "last_checked": datetime.now().isoformat(),
                "change_count": 0
            }
            has_changes = False
        
        # Save updated history
        with history_file.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return {
            "has_changes": has_changes,
            "summary": f"Content {'changed' if has_changes else 'unchanged'} since last check",
            "change_count": history.get("change_count", 0)
        }

    def _assess_hiring_relevance(self, content: str, key_indicators: List[str]) -> float:
        """Assess how relevant content is to hiring practices"""
        
        content_lower = content.lower()
        relevance_keywords = [
            "interview", "hiring", "candidate", "recruitment", "assessment",
            "evaluation", "skill", "competency", "behavioral", "technical",
            "coding", "algorithm", "system design", "leadership", "googleyness"
        ]
        
        # Count keyword occurrences
        total_score = 0
        for keyword in relevance_keywords:
            count = content_lower.count(keyword)
            total_score += min(count, 5)  # Cap at 5 occurrences per keyword
        
        # Bonus for key indicators
        for indicator in key_indicators:
            if indicator.lower() in content_lower:
                total_score += 10
        
        # Normalize to 0-100 scale
        max_possible = len(relevance_keywords) * 5 + len(key_indicators) * 10
        return min(100, (total_score / max_possible) * 100) if max_possible > 0 else 0

    def _extract_key_terms(self, content: str, indicators: List[str]) -> List[str]:
        """Extract key terms related to hiring and interviews"""
        
        found_terms = []
        content_lower = content.lower()
        
        # Check for exact indicator matches
        for indicator in indicators:
            if indicator.lower() in content_lower:
                found_terms.append(indicator)
        
        # Look for hiring-related terms in context
        hiring_patterns = [
            r"interview\s+process",
            r"hiring\s+criteria",
            r"assessment\s+method",
            r"evaluation\s+rubric",
            r"coding\s+interview",
            r"behavioral\s+interview",
            r"system\s+design\s+interview",
            r"technical\s+assessment"
        ]
        
        for pattern in hiring_patterns:
            matches = re.finditer(pattern, content_lower)
            for match in matches:
                found_terms.append(match.group(0))
        
        return list(set(found_terms))  # Remove duplicates

    def _monitor_reddit_trends(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor Reddit for interview discussion trends"""
        
        # Build Reddit search URL
        params = {
            "q": source["query"],
            "sort": "new",
            "limit": "25",
            "t": "week"  # Last week
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{source['base_url']}?{query_string}"
        
        try:
            content = self._fetch_page(url)
            data = json.loads(content)
            
            posts = data.get("data", {}).get("children", [])
            
            # Analyze trending topics
            trending_topics = {}
            total_posts = len(posts)
            
            for post in posts:
                post_data = post.get("data", {})
                title = post_data.get("title", "").lower()
                
                # Count topic mentions
                topics = ["leetcode", "system design", "behavioral", "coding", "oa", "onsite", "phone screen"]
                for topic in topics:
                    if topic in title:
                        trending_topics[topic] = trending_topics.get(topic, 0) + 1
            
            return {
                "total_posts": total_posts,
                "trending_topics": trending_topics,
                "analysis_period": "last_week",
                "top_trend": max(trending_topics.items(), key=lambda x: x[1]) if trending_topics else None
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _monitor_hn_trends(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor Hacker News for interview discussion trends"""
        
        # Build HN API URL
        url = f"{source['base_url']}?query={source['query']}&tags=story&hitsPerPage=20"
        
        try:
            content = self._fetch_page(url)
            data = json.loads(content)
            
            hits = data.get("hits", [])
            
            # Analyze story trends
            story_analysis = {
                "total_stories": len(hits),
                "time_range": "recent",
                "topics": {},
                "avg_points": 0
            }
            
            if hits:
                total_points = sum(hit.get("points", 0) for hit in hits)
                story_analysis["avg_points"] = total_points / len(hits)
                
                # Extract trending topics from titles
                for hit in hits:
                    title = hit.get("title", "").lower()
                    if "interview" in title:
                        story_analysis["topics"]["interview"] = story_analysis["topics"].get("interview", 0) + 1
                    if "hiring" in title:
                        story_analysis["topics"]["hiring"] = story_analysis["topics"].get("hiring", 0) + 1
                    if "coding" in title:
                        story_analysis["topics"]["coding"] = story_analysis["topics"].get("coding", 0) + 1
            
            return story_analysis
            
        except Exception as e:
            return {"error": str(e)}

    def _check_leetcode_trends(self) -> Dict[str, Any]:
        """Check LeetCode for trending problem patterns (public data only)"""
        
        # Note: This would require LeetCode's public API or web scraping
        # For now, return placeholder structure for trend analysis
        return {
            "note": "LeetCode trend monitoring requires API access or web scraping",
            "implementation_status": "placeholder",
            "suggested_metrics": [
                "New problems with Google tag",
                "Difficulty distribution changes",
                "New algorithm categories",
                "Contest problem patterns"
            ]
        }

    def _check_codeforces_trends(self) -> Dict[str, Any]:
        """Check Codeforces for recent contest and problem trends"""
        
        try:
            # Get recent contests
            contests_url = "https://codeforces.com/api/contest.list?gym=false"
            content = self._fetch_page(contests_url)
            data = json.loads(content)
            
            if data.get("status") == "OK":
                contests = data.get("result", [])
                recent_contests = [c for c in contests if c.get("phase") in ["FINISHED", "CODING"]][:10]
                
                return {
                    "recent_contests": len(recent_contests),
                    "contest_types": list(set(c.get("type", "unknown") for c in recent_contests)),
                    "avg_duration": sum(c.get("durationSeconds", 0) for c in recent_contests) / len(recent_contests) if recent_contests else 0,
                    "status": "success"
                }
            else:
                return {"error": "Codeforces API returned error status"}
                
        except Exception as e:
            return {"error": str(e)}

    def generate_trend_report(self) -> Dict[str, Any]:
        """Generate comprehensive trend monitoring report"""
        
        print("=== Generating Comprehensive Trend Report ===")
        
        # Run all monitoring checks
        google_updates = self.monitor_google_engineering_updates()
        discussion_trends = self.monitor_interview_discussions() 
        platform_trends = self.monitor_competitive_platforms()
        
        # Analyze overall trends
        trend_summary = {
            "monitoring_timestamp": datetime.now().isoformat(),
            "monitoring_scope": [
                "Google engineering documentation",
                "Public interview discussions",
                "Competitive programming platforms"
            ],
            "google_updates": google_updates,
            "discussion_trends": discussion_trends,
            "platform_trends": platform_trends,
            "alerts": self._generate_alerts(google_updates, discussion_trends, platform_trends),
            "recommendations": self._generate_recommendations(google_updates, discussion_trends, platform_trends)
        }
        
        # Save trend report
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.monitoring_dir / f"trend_report_{ts}.json"
        
        with report_file.open("w", encoding="utf-8") as f:
            json.dump(trend_summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Trend report saved: {report_file}")
        return trend_summary

    def _generate_alerts(self, google_updates: Dict, discussion_trends: Dict, platform_trends: Dict) -> List[Dict[str, Any]]:
        """Generate alerts for significant changes"""
        
        alerts = []
        
        # Check for Google documentation changes
        for result in google_updates.get("results", []):
            if result.get("changes_detected"):
                alerts.append({
                    "type": "documentation_change",
                    "severity": "medium",
                    "source": result["source"],
                    "message": f"Changes detected in {result['source']}",
                    "action_required": "Review changes for hiring practice updates"
                })
        
        # Check for high engagement discussions
        for result in discussion_trends.get("results", []):
            trends = result.get("trends", {})
            if isinstance(trends, dict) and trends.get("total_posts", 0) > 50:
                alerts.append({
                    "type": "high_discussion_activity",
                    "severity": "low",
                    "source": result["source"],
                    "message": f"High discussion activity detected: {trends['total_posts']} posts",
                    "action_required": "Monitor for emerging interview patterns"
                })
        
        return alerts

    def _generate_recommendations(self, google_updates: Dict, discussion_trends: Dict, platform_trends: Dict) -> List[str]:
        """Generate actionable recommendations based on trends"""
        
        recommendations = []
        
        # Always recommend regular monitoring
        recommendations.append("Continue regular monitoring of Google engineering documentation")
        recommendations.append("Track discussion trends for emerging interview patterns")
        
        # Check if any sources had errors
        total_checks = (google_updates.get("sources_checked", 0) + 
                       discussion_trends.get("sources_checked", 0) + 
                       platform_trends.get("platforms_checked", 0))
        
        successful_checks = (google_updates.get("successful_checks", 0) + 
                           len([r for r in discussion_trends.get("results", []) if "error" not in r]) +
                           len([r for r in platform_trends.get("results", []) if "error" not in r]))
        
        if successful_checks < total_checks:
            recommendations.append("Investigate and fix monitoring sources that returned errors")
        
        # Recommend data updates if changes detected
        changes_detected = any(r.get("changes_detected", False) for r in google_updates.get("results", []))
        if changes_detected:
            recommendations.append("Update Google official documentation dataset with latest changes")
            recommendations.append("Review and update evaluation rubrics if hiring criteria changed")
        
        return recommendations

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run complete monitoring cycle and log results"""
        
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            trend_report = self.generate_trend_report()
            
            # Count successful monitoring activities
            total_sources = (trend_report["google_updates"].get("sources_checked", 0) +
                           trend_report["discussion_trends"].get("sources_checked", 0) + 
                           trend_report["platform_trends"].get("platforms_checked", 0))
            
            alerts_count = len(trend_report.get("alerts", []))
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "sources_monitored": total_sources,
                "alerts_generated": alerts_count,
                "monitoring_types": ["google_updates", "discussion_trends", "platform_trends"]
            }
            
            logger.log("trend_monitoring", "comprehensive_cycle", 
                      records=total_sources, success=True, metadata=meta)
            
            return {
                "status": "success",
                "sources_monitored": total_sources,
                "alerts_generated": alerts_count,
                "report_location": str(self.monitoring_dir / f"trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            }
            
        except Exception as e:
            logger.log("trend_monitoring", "comprehensive_cycle", 
                      records=0, success=False, error=str(e))
            raise
