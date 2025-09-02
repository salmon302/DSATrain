"""
SRSService: Spaced Repetition scheduling and logging.

Implements a simple SM-2-like algorithm for interval/ease updates.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.models.database import ReviewCard, ReviewHistory, RetrievalPractice


class SRSService:
    def __init__(self, db: Session):
        self.db = db

    def get_due_cards(self, limit: int = 10, deck: Optional[str] = None) -> List[ReviewCard]:
        now = datetime.now()
        query = self.db.query(ReviewCard).filter(
            (ReviewCard.next_review_at == None) | (ReviewCard.next_review_at <= now)
        )
        if deck:
            query = query.filter(ReviewCard.deck == deck)
        return query.order_by(ReviewCard.next_review_at.asc().nullsfirst()).limit(limit).all()

    def review(self, problem_id: str, outcome: str) -> Dict[str, Any]:
        """
        Record a review and update scheduling.
        outcome: one of again|hard|good|easy
        """
        # Get or create card
        card = self.db.query(ReviewCard).filter(ReviewCard.problem_id == problem_id).first()
        created = False
        if not card:
            card = ReviewCard(problem_id=problem_id, interval_days=1, ease=2.5, reps=0, lapses=0, deck="problems")
            self.db.add(card)
            created = True

        # Insert history
        history = ReviewHistory(problem_id=problem_id, outcome=outcome, time_spent=0)
        self.db.add(history)
        # Ensure pending inserts are visible within this transaction prior to updates/commit
        try:
            self.db.flush()
        except Exception:
            # Non-fatal: proceed to commit path which will flush as well
            pass

        # Update SM-2 like
        ease = card.ease or 2.5
        reps = card.reps or 0
        interval = card.interval_days or 1

        if outcome == 'again':
            reps = 0
            interval = 1
            ease = max(1.3, ease - 0.2)
            card.lapses = (card.lapses or 0) + 1
        elif outcome == 'hard':
            reps += 1
            interval = max(1, int(interval * 1.2))
            ease = max(1.3, ease - 0.15)
        elif outcome == 'good':
            reps += 1
            interval = int(interval * ease)
            interval = max(interval, 2)
        elif outcome == 'easy':
            reps += 1
            interval = int(interval * (ease + 0.15))
            ease = min(ease + 0.05, 3.0)
        else:
            raise ValueError("Invalid outcome; must be again|hard|good|easy")

        # Update card with safe bounds
        SAFE_MAX_DAYS = 36500  # ~100 years to avoid platform/date overflows
        card.reps = reps
        card.ease = ease
        card.interval_days = max(1, min(interval, SAFE_MAX_DAYS))
        card.last_outcome = outcome
        try:
            card.next_review_at = datetime.now() + timedelta(days=card.interval_days)
        except Exception:
            # Fallback to a reasonable future date if platform raises due to range issues
            card.next_review_at = datetime.now() + timedelta(days=1)

        self.db.commit()

        return {
            'problem_id': problem_id,
            'created': created,
            'next_review_at': card.next_review_at.isoformat() if card.next_review_at else None,
            'interval_days': card.interval_days,
            'ease': card.ease,
            'reps': card.reps,
            'lapses': card.lapses,
        }

    def get_stats(self) -> Dict[str, Any]:
        total_cards = self.db.query(ReviewCard).count()
        due_now = self.db.query(ReviewCard).filter(
            (ReviewCard.next_review_at == None) | (ReviewCard.next_review_at <= datetime.now())
        ).count()
        total_reviews = self.db.query(ReviewHistory).count()
        return {
            'total_cards': total_cards,
            'due_now': due_now,
            'total_reviews': total_reviews,
        }

    def log_retrieval(self, problem_id: str, retrieval_type: str, success_rate: float, retrieval_strength: float) -> Dict[str, Any]:
        entry = RetrievalPractice(
            problem_id=problem_id,
            retrieval_type=retrieval_type,
            success_rate=success_rate,
            retrieval_strength=retrieval_strength,
        )
        self.db.add(entry)
        self.db.commit()
        return {
            'id': entry.id,
            'problem_id': entry.problem_id,
            'retrieval_type': entry.retrieval_type,
            'success_rate': entry.success_rate,
            'retrieval_strength': entry.retrieval_strength,
            'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
        }

    def metrics(self, days: int = 7) -> Dict[str, Any]:
        """Compute review metrics for the last N days and weekly aggregates.

        Returns a structure with per-day counts and a week summary.
        """
        now = datetime.now()
        start = now - timedelta(days=max(1, days))

        # Per-day counts
        counts: Dict[str, int] = {}
        q = self.db.query(ReviewHistory).filter(ReviewHistory.timestamp >= start)
        for h in q.all():
            day = (h.timestamp.date().isoformat() if h.timestamp else now.date().isoformat())
            counts[day] = counts.get(day, 0) + 1

        # Fill missing days with 0 up to 'days'
        daily = []
        for i in range(days, -1, -1):
            d = (now - timedelta(days=i)).date().isoformat()
            daily.append({"date": d, "reviews": counts.get(d, 0)})

        total = sum(c["reviews"] for c in daily)
        avg_per_day = total / (len(daily) or 1)

        # Weekly aggregates (last 4 weeks)
        week_counts: Dict[str, int] = {}
        for h in self.db.query(ReviewHistory).all():
            if not h.timestamp:
                continue
            year, week, _ = h.timestamp.isocalendar()
            key = f"{year}-W{week:02d}"
            week_counts[key] = week_counts.get(key, 0) + 1

        # Sort weeks and take last 4
        weekly = [
            {"week": wk, "reviews": cnt}
            for wk, cnt in sorted(week_counts.items())[-4:]
        ]

        return {
            "daily": daily,
            "weekly": weekly,
            # Use explicit key with the requested days value for clarity
            f"total_last_{days}": total,
            "avg_per_day": round(avg_per_day, 2),
        }
