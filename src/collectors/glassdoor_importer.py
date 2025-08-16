from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .acquisition_logger import AcquisitionLogger


@dataclass
class GlassdoorImporter:
    data_dir: Path

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "glassdoor"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _read_csv_safe(self, path: Path) -> List[Dict[str, str]]:
        if not path.exists():
            return []
        rows: List[Dict[str, str]] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows

    def _read_json_safe(self, path: Path) -> List[Dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "interviews" in data:
                return data["interviews"]
            elif isinstance(data, dict) and "reviews" in data:
                return data["reviews"]
            return []

    def load_interview_data(self) -> List[Dict]:
        # Expected files from Apify Glassdoor scraper or manual exports
        json_files = [
            "google_interviews.json",
            "tech_interviews.json",
            "apify_glassdoor_export.json",
        ]
        csv_files = [
            "google_interviews.csv",
            "tech_interviews.csv",
        ]

        items: List[Dict] = []
        
        # Load JSON files
        for fname in json_files:
            items.extend(self._read_json_safe(self.raw_dir / fname))
        
        # Load CSV files
        for fname in csv_files:
            csv_data = self._read_csv_safe(self.raw_dir / fname)
            items.extend(csv_data)

        # Standardize fields across different Glassdoor export formats
        standardized: List[Dict] = []
        for item in items:
            # Handle various field name formats from different scrapers
            company = (
                item.get("companyName") or 
                item.get("company") or 
                item.get("employer") or 
                "Unknown"
            )
            
            # Interview questions can be in different fields
            questions = (
                item.get("interviewQuestions") or
                item.get("questions") or
                item.get("interview_questions") or
                item.get("questionText") or
                ""
            )
            
            # Experience/review text
            experience = (
                item.get("interviewExperience") or
                item.get("experience") or
                item.get("review") or
                item.get("text") or
                ""
            )
            
            difficulty = item.get("difficulty") or item.get("interviewDifficulty") or ""
            outcome = item.get("outcome") or item.get("offer") or item.get("result") or ""
            
            standardized.append({
                "source": "glassdoor",
                "company": company,
                "position": item.get("position") or item.get("jobTitle") or "",
                "questions": questions,
                "experience": experience,
                "difficulty": difficulty,
                "outcome": outcome,
                "rating": item.get("rating") or item.get("overallRating"),
                "date": item.get("date") or item.get("dateTime") or item.get("reviewDate"),
                "url": item.get("url") or item.get("reviewUrl"),
                "collected_at": datetime.now().isoformat()
            })

        return standardized

    def run_import(self) -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        try:
            items = self.load_interview_data()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = self.raw_dir / f"glassdoor_standardized_{ts}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump({"items": items}, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "count": len(items),
                "output_file": str(out_file),
                "companies": list(set(item["company"] for item in items if item["company"]))[:10]
            }
            logger.log("glassdoor", "import_local_files", records=len(items), success=True, metadata=meta)
            return meta
        except Exception as e:
            logger.log("glassdoor", "import_local_files", records=0, success=False, error=str(e))
            raise
