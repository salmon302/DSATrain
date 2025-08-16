from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .acquisition_logger import AcquisitionLogger


@dataclass
class BehavioralResourcesFetcher:
    data_dir: Path
    rate_limit_sleep: float = 2.0

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "behavioral_resources"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _download_document(self, url: str, filename: str) -> Optional[Path]:
        """Download a document to the raw directory"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "DSATrain-BehavioralFetcher/0.1 (Educational Research)",
                    "Accept": "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/html,*/*"
                }
            )
            output_path = self.raw_dir / filename
            with urllib.request.urlopen(req, timeout=30) as response:
                with output_path.open("wb") as f:
                    f.write(response.read())
            return output_path
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None

    def fetch_university_resources(self) -> List[Dict[str, Any]]:
        """Fetch behavioral question databases from university career centers"""
        
        # Based on research document citations
        university_resources = [
            {
                "source": "University of Washington",
                "url": "https://hr.uw.edu/talent/wp-content/uploads/sites/17/2023/02/Behavioral-Interview-Question-Inventory-by-Competency-20230213.docx",
                "filename": "uw_behavioral_questions_by_competency.docx",
                "type": "behavioral_questions",
                "description": "Behavioral interview questions categorized by competency"
            },
            {
                "source": "University of Arkansas",
                "url": "https://walton.uark.edu/career/files_career_center/Extensive_List_of_Competency-Based_Interview_Questions.pdf",
                "filename": "uark_competency_based_questions.pdf",
                "type": "behavioral_questions",
                "description": "Extensive list of competency-based behavioral interview questions"
            },
            {
                "source": "University of Utah",
                "url": "https://www.hr.utah.edu/forms/lib/Behavioral_Interview_Questions.pdf",
                "filename": "utah_behavioral_questions.pdf",
                "type": "behavioral_questions",
                "description": "Behavioral interview questions by competency area"
            },
            {
                "source": "UC Berkeley",
                "url": "https://hr.berkeley.edu/grow/grow-your-resources/uc-systemwide-core-competency-abcs/interview-questions-database",
                "filename": "ucb_interview_questions_database.html",
                "type": "behavioral_questions",
                "description": "Interview questions database with core competencies"
            },
            {
                "source": "University of New Mexico",
                "url": "https://hr.unm.edu/docs/employment/behavioral-questions-by-job-competency-for-job-interviews-(pdf).pdf",
                "filename": "unm_behavioral_questions_competency.pdf",
                "type": "behavioral_questions",
                "description": "Behavioral questions organized by job competency"
            }
        ]

        results: List[Dict[str, Any]] = []
        for resource in university_resources:
            print(f"Downloading: {resource['source']} - {resource['description']}")
            downloaded_path = self._download_document(resource["url"], resource["filename"])
            
            result = {
                "source": resource["source"],
                "type": resource["type"],
                "description": resource["description"],
                "url": resource["url"],
                "filename": resource["filename"],
                "downloaded": downloaded_path is not None,
                "local_path": str(downloaded_path) if downloaded_path else None,
                "collected_at": datetime.now().isoformat()
            }
            results.append(result)
            
            if downloaded_path:
                print(f"✅ Downloaded to: {downloaded_path}")
            else:
                print(f"❌ Failed to download")

        return results

    def fetch_star_rubrics(self) -> List[Dict[str, Any]]:
        """Fetch STAR method evaluation rubrics"""
        
        star_resources = [
            {
                "source": "Northern Arizona University",
                "url": "https://in.nau.edu/wp-content/uploads/sites/204/2018/06/STAR-Behavioral-Interview-Assignment-Rubric.pdf",
                "filename": "nau_star_rubric.pdf",
                "type": "star_rubric",
                "description": "STAR behavioral interview assignment rubric with scoring criteria"
            },
            {
                "source": "VA Wizard",
                "url": "https://www.vawizard.org/wiz-pdf/STAR_Method_Interviews.pdf",
                "filename": "va_star_method_guide.pdf",
                "type": "star_rubric",
                "description": "STAR method interviewing guide with evaluation criteria"
            },
            {
                "source": "Case Western Reserve University",
                "url": "https://case.edu/studentlife/careercenter/career-development/career-resources/tips-job-seekers/interviewing/behavior-based-interviewing/star-strategy-examples",
                "filename": "case_star_examples.html",
                "type": "star_examples",
                "description": "STAR strategy examples and best practices"
            },
            {
                "source": "MIT Career Development",
                "url": "https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/",
                "filename": "mit_star_method.html",
                "type": "star_guide",
                "description": "MIT's guide to the STAR method for behavioral interviews"
            }
        ]

        results: List[Dict[str, Any]] = []
        for resource in star_resources:
            print(f"Downloading: {resource['source']} - {resource['description']}")
            downloaded_path = self._download_document(resource["url"], resource["filename"])
            
            result = {
                "source": resource["source"],
                "type": resource["type"],
                "description": resource["description"],
                "url": resource["url"],
                "filename": resource["filename"],
                "downloaded": downloaded_path is not None,
                "local_path": str(downloaded_path) if downloaded_path else None,
                "collected_at": datetime.now().isoformat()
            }
            results.append(result)

        return results

    def run_acquisition(self) -> Dict[str, Any]:
        """Run complete behavioral resources acquisition"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            print("=== Fetching University Behavioral Question Databases ===")
            university_results = self.fetch_university_resources()
            
            print("\n=== Fetching STAR Method Rubrics ===")
            star_results = self.fetch_star_rubrics()
            
            all_results = university_results + star_results
            successful_downloads = [r for r in all_results if r["downloaded"]]
            
            # Save acquisition summary
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = self.raw_dir / f"acquisition_summary_{ts}.json"
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_attempted": len(all_results),
                "successful_downloads": len(successful_downloads),
                "failed_downloads": len(all_results) - len(successful_downloads),
                "resources": all_results
            }
            
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "attempted": len(all_results),
                "successful": len(successful_downloads),
                "output_file": str(summary_file)
            }
            
            logger.log("behavioral_resources", "document_download", 
                      records=len(successful_downloads), success=True, metadata=meta)
            
            return meta
            
        except Exception as e:
            logger.log("behavioral_resources", "document_download", 
                      records=0, success=False, error=str(e))
            raise
