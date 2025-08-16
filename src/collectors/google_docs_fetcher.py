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
class GoogleDocsFetcher:
    data_dir: Path
    rate_limit_sleep: float = 2.0

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "google_official"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _fetch_page(self, url: str) -> str:
        """Fetch a web page with appropriate headers"""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DSATrain-GoogleDocsFetcher/0.1 (Educational Research)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="ignore")

    def fetch_hiring_documentation(self) -> List[Dict[str, Any]]:
        """Fetch Google's official hiring and engineering documentation"""
        
        google_resources = [
            {
                "source": "Google Engineering Practices",
                "url": "https://google.github.io/eng-practices/",
                "filename": "google_eng_practices_index.html",
                "type": "engineering_practices",
                "description": "Google's engineering practices documentation"
            },
            {
                "source": "Google Code Review Guidelines",
                "url": "https://google.github.io/eng-practices/review/reviewer/standard.html",
                "filename": "google_code_review_standards.html",
                "type": "code_review",
                "description": "The standard of code review at Google"
            },
            {
                "source": "Google Code Review Developer Guide",
                "url": "https://google.github.io/eng-practices/review/developer/",
                "filename": "google_code_review_developer.html",
                "type": "code_review",
                "description": "Code review developer guide"
            },
            {
                "source": "Google Careers - How We Hire",
                "url": "https://www.google.com/about/careers/applications/how-we-hire/",
                "filename": "google_how_we_hire.html",
                "type": "hiring_process",
                "description": "Google's official hiring process documentation"
            },
            {
                "source": "Google Careers Help",
                "url": "https://support.google.com/googlecareers/answer/6095391?hl=en",
                "filename": "google_careers_help.html",
                "type": "hiring_process",
                "description": "Google careers application help"
            }
        ]

        results: List[Dict[str, Any]] = []
        
        for resource in google_resources:
            print(f"Fetching: {resource['source']}")
            try:
                content = self._fetch_page(resource["url"])
                
                # Save the raw HTML
                output_path = self.raw_dir / resource["filename"]
                with output_path.open("w", encoding="utf-8") as f:
                    f.write(content)
                
                # Extract key information
                extracted_info = self._extract_key_info(content, resource["type"])
                
                result = {
                    "source": resource["source"],
                    "type": resource["type"],
                    "description": resource["description"],
                    "url": resource["url"],
                    "filename": resource["filename"],
                    "content_length": len(content),
                    "extracted_info": extracted_info,
                    "local_path": str(output_path),
                    "collected_at": datetime.now().isoformat()
                }
                results.append(result)
                
                print(f"✅ Saved to: {output_path} ({len(content)} chars)")
                time.sleep(self.rate_limit_sleep)
                
            except Exception as e:
                print(f"❌ Failed to fetch {resource['url']}: {e}")
                result = {
                    "source": resource["source"],
                    "type": resource["type"],
                    "description": resource["description"],
                    "url": resource["url"],
                    "filename": resource["filename"],
                    "error": str(e),
                    "collected_at": datetime.now().isoformat()
                }
                results.append(result)

        return results

    def _extract_key_info(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Extract key information from HTML content based on document type"""
        info: Dict[str, Any] = {}
        
        if doc_type == "code_review":
            # Extract code review principles
            principles = []
            # Look for list items or headings that contain principles
            principle_patterns = [
                r"<h[1-6][^>]*>([^<]*(?:principle|standard|guideline|rule)[^<]*)</h[1-6]>",
                r"<li[^>]*>([^<]*(?:should|must|always|never)[^<]*)</li>",
                r"<p[^>]*><strong>([^<]*(?:principle|rule)[^<]*)</strong>"
            ]
            
            for pattern in principle_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    principle = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                    if len(principle) > 10:  # Filter out very short matches
                        principles.append(principle)
            
            info["principles"] = principles[:20]  # Limit to top 20
            
        elif doc_type == "hiring_process":
            # Extract hiring criteria and process steps
            criteria = []
            criteria_patterns = [
                r"<h[1-6][^>]*>([^<]*(?:criteria|evaluation|assess|skill|competenc)[^<]*)</h[1-6]>",
                r"<li[^>]*>([^<]*(?:look for|evaluate|assess|consider)[^<]*)</li>"
            ]
            
            for pattern in criteria_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    criterion = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                    if len(criterion) > 10:
                        criteria.append(criterion)
            
            info["evaluation_criteria"] = criteria[:15]
            
        elif doc_type == "engineering_practices":
            # Extract engineering practice categories
            practices = []
            practice_patterns = [
                r"<h[1-6][^>]*>([^<]*(?:practice|guideline|standard)[^<]*)</h[1-6]>",
                r"<a[^>]*href=\"[^\"]*\">([^<]*(?:review|style|design|test)[^<]*)</a>"
            ]
            
            for pattern in practice_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    practice = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                    if len(practice) > 5:
                        practices.append(practice)
            
            info["practices"] = practices[:20]
        
        # Extract "Googleyness" related content
        googleyness_keywords = ["googleyness", "google values", "culture", "collaborative", "adaptable", "intellectual humility"]
        googleyness_content = []
        
        for keyword in googleyness_keywords:
            pattern = rf"[^.]*{keyword}[^.]*\."
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                sentence = re.sub(r"<[^>]+>", "", match.group(0)).strip()
                if len(sentence) > 20:
                    googleyness_content.append(sentence)
        
        if googleyness_content:
            info["googleyness_content"] = googleyness_content[:10]
        
        return info

    def run_acquisition(self) -> Dict[str, Any]:
        """Run complete Google documentation acquisition"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            print("=== Fetching Google Official Documentation ===")
            results = self.fetch_hiring_documentation()
            
            successful_fetches = [r for r in results if "error" not in r]
            
            # Save acquisition summary
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = self.raw_dir / f"google_docs_summary_{ts}.json"
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_attempted": len(results),
                "successful_fetches": len(successful_fetches),
                "failed_fetches": len(results) - len(successful_fetches),
                "documents": results
            }
            
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "attempted": len(results),
                "successful": len(successful_fetches),
                "output_file": str(summary_file)
            }
            
            logger.log("google_official", "documentation_fetch", 
                      records=len(successful_fetches), success=True, metadata=meta)
            
            return meta
            
        except Exception as e:
            logger.log("google_official", "documentation_fetch", 
                      records=0, success=False, error=str(e))
            raise
