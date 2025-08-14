from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError

from src.models.database import DatabaseConfig, Problem as DBProblem, Solution as DBSolution


@dataclass
class DatasetStandardizer:
	data_dir: Path
	write_unified_files: bool = True
	upsert_to_db: bool = True
	backup: bool = True

	@property
	def processed_dir(self) -> Path:
		return self.data_dir / "processed"

	def _ensure_dirs(self) -> None:
		self.processed_dir.mkdir(parents=True, exist_ok=True)

	def _normalize_difficulty(self, difficulty: Optional[str]) -> str:
		if not difficulty:
			return "Medium"
		d = difficulty.strip().lower()
		if d.startswith("e"):
			return "Easy"
		if d.startswith("h"):
			return "Hard"
		return "Medium"

	def unify_problems(self, raw_problems: List[Dict]) -> List[Dict]:
		unified: List[Dict] = []
		for p in raw_problems:
			platform = p.get("platform") or p.get("source") or "unknown"
			platform_id = p.get("platform_id") or p.get("id") or p.get("title") or ""
			problem_id = p.get("id") or f"{platform}_{platform_id}"
			unified.append({
				"id": problem_id,
				"platform": platform,
				"platform_id": str(platform_id),
				"title": p.get("title") or "",
				"difficulty": self._normalize_difficulty(p.get("difficulty")),
				"description": p.get("description") or p.get("statement") or "",
				"constraints": p.get("constraints"),
				"examples": p.get("examples"),
				"hints": p.get("hints"),
				"algorithm_tags": p.get("algorithm_tags") or p.get("tags") or [],
				"data_structures": p.get("data_structures") or [],
				"companies": p.get("companies") or [],
				"acceptance_rate": p.get("acceptance_rate"),
				"frequency_score": p.get("frequency_score"),
				"collected_at": p.get("collected_at") or datetime.now().isoformat()
			})
		return unified

	def unify_solutions(self, raw_solutions: List[Dict]) -> List[Dict]:
		unified: List[Dict] = []
		for s in raw_solutions:
			unified.append({
				"id": s.get("id") or f"{s.get('problem_id','unknown')}_sol_{len(unified)+1}",
				"problem_id": s.get("problem_id") or "",
				"code": s.get("code") or "",
				"language": (s.get("language") or "python").lower(),
				"approach_type": s.get("approach_type") or "unknown",
				"algorithm_tags": s.get("algorithm_tags") or [],
				"time_complexity": s.get("time_complexity") or "",
				"space_complexity": s.get("space_complexity") or "",
				"explanation": s.get("explanation"),
				"overall_quality_score": s.get("overall_quality_score") or 0.0,
				"collected_at": s.get("collected_at") or datetime.now().isoformat()
			})
		return unified

	def write_unified(self, problems: List[Dict], solutions: List[Dict]) -> Tuple[Path, Path]:
		self._ensure_dirs()
		p_path = self.processed_dir / "problems_unified.json"
		s_path = self.processed_dir / "solutions_unified.json"
		with p_path.open("w", encoding="utf-8") as f:
			json.dump(problems, f, ensure_ascii=False, indent=2)
		with s_path.open("w", encoding="utf-8") as f:
			json.dump(solutions, f, ensure_ascii=False, indent=2)
		return p_path, s_path

	def upsert(self, problems: List[Dict], solutions: List[Dict]) -> Dict[str, int]:
		db = DatabaseConfig()
		session = db.get_session()
		created_p = updated_p = 0
		created_s = updated_s = 0
		try:
			for p in problems:
				obj = session.get(DBProblem, p["id"])
				if obj is None:
					obj = DBProblem(
						id=p["id"],
						platform=p["platform"],
						platform_id=str(p["platform_id"]),
						title=p["title"],
						difficulty=p["difficulty"],
						description=p.get("description"),
						constraints=p.get("constraints"),
						examples=p.get("examples"),
						hints=p.get("hints"),
						algorithm_tags=p.get("algorithm_tags") or [],
						data_structures=p.get("data_structures") or [],
						acceptance_rate=p.get("acceptance_rate"),
						companies=p.get("companies") or []
					)
					session.add(obj)
					created_p += 1
				else:
					obj.title = p["title"] or obj.title
					obj.difficulty = p.get("difficulty") or obj.difficulty
					obj.description = p.get("description") or obj.description
					obj.algorithm_tags = p.get("algorithm_tags") or obj.algorithm_tags
					obj.data_structures = p.get("data_structures") or obj.data_structures
					obj.acceptance_rate = p.get("acceptance_rate") if p.get("acceptance_rate") is not None else obj.acceptance_rate
					obj.companies = p.get("companies") or obj.companies
					updated_p += 1

			session.flush()

			for s in solutions:
				existing = session.get(DBSolution, s["id"])
				if existing is None:
					sobj = DBSolution(
						id=s["id"],
						problem_id=s["problem_id"],
						code=s["code"],
						language=s["language"],
						approach_type=s["approach_type"],
						algorithm_tags=s.get("algorithm_tags") or [],
						time_complexity=s.get("time_complexity"),
						space_complexity=s.get("space_complexity"),
						overall_quality_score=float(s.get("overall_quality_score") or 0.0),
						explanation=s.get("explanation")
					)
					session.add(sobj)
					created_s += 1
				else:
					existing.code = s.get("code") or existing.code
					existing.approach_type = s.get("approach_type") or existing.approach_type
					existing.algorithm_tags = s.get("algorithm_tags") or existing.algorithm_tags
					existing.time_complexity = s.get("time_complexity") or existing.time_complexity
					existing.space_complexity = s.get("space_complexity") or existing.space_complexity
					updated_s += 1

			session.commit()
			return {"problems_created": created_p, "problems_updated": updated_p, "solutions_created": created_s, "solutions_updated": updated_s}
		except IntegrityError:
			session.rollback()
			raise
		finally:
			session.close()

	def run(self, problem_sources: List[List[Dict]], solution_sources: List[List[Dict]]) -> Dict[str, int]:
		problems = self.unify_problems([p for src in problem_sources for p in src])
		solutions = self.unify_solutions([s for src in solution_sources for s in src])
		if self.write_unified_files:
			self.write_unified(problems, solutions)
		stats = {"problems": len(problems), "solutions": len(solutions)}
		if self.upsert_to_db:
			stats.update(self.upsert(problems, solutions))
		return stats 