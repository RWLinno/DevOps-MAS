"""
Case Analyzer & Visualization
Provides analytics, trend analysis, and report generation for oncall cases.
"""

import json
import logging
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .tracker import CaseTracker, CaseStatus, IncidentCase

logger = logging.getLogger(__name__)


@dataclass
class CaseReport:
    summary: str
    total_cases: int
    resolved_cases: int
    avg_resolution_time_min: Optional[float]
    top_tags: List[tuple]
    priority_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    timeline: List[Dict[str, Any]]
    recommendations: List[str]


class CaseAnalyzer:
    """Analyze oncall cases and generate insights."""

    def __init__(self, tracker: CaseTracker):
        self.tracker = tracker

    def generate_report(self) -> CaseReport:
        cases = list(self.tracker.cases.values())
        if not cases:
            return CaseReport(
                summary="No cases recorded yet.",
                total_cases=0,
                resolved_cases=0,
                avg_resolution_time_min=None,
                top_tags=[],
                priority_distribution={},
                status_distribution={},
                timeline=[],
                recommendations=[],
            )

        resolved = [c for c in cases if c.status in (CaseStatus.RESOLVED, CaseStatus.CLOSED)]
        resolution_times = [c.resolution_time_min for c in resolved if c.resolution_time_min]

        all_tags = []
        for c in cases:
            all_tags.extend(c.tags)
        tag_counts = Counter(all_tags).most_common(10)

        priority_dist = Counter(c.priority.value for c in cases)
        status_dist = Counter(c.status.value for c in cases)

        timeline = self._build_timeline(cases)
        recommendations = self._generate_recommendations(cases, tag_counts, resolution_times)

        avg_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
        summary = (
            f"Total {len(cases)} cases, {len(resolved)} resolved. "
            f"Average resolution time: {avg_time:.1f} min. " if avg_time else
            f"Total {len(cases)} cases, {len(resolved)} resolved. "
        )
        if tag_counts:
            summary += f"Most common issues: {', '.join(t[0] for t in tag_counts[:3])}."

        return CaseReport(
            summary=summary,
            total_cases=len(cases),
            resolved_cases=len(resolved),
            avg_resolution_time_min=avg_time,
            top_tags=tag_counts,
            priority_distribution=dict(priority_dist),
            status_distribution=dict(status_dist),
            timeline=timeline,
            recommendations=recommendations,
        )

    def get_case_timeline(self, case_id: str) -> List[Dict[str, Any]]:
        """Get detailed timeline for a single case."""
        case = self.tracker.get_case(case_id)
        if not case:
            return []
        timeline = []
        for event in case.events:
            timeline.append({
                "timestamp": event.timestamp,
                "time_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp)),
                "type": event.event_type,
                "content": event.content,
                "agent": event.agent_name,
            })
        return timeline

    def get_visualization_data(self) -> Dict[str, Any]:
        """Generate data suitable for charts and dashboards."""
        cases = list(self.tracker.cases.values())
        if not cases:
            return {"empty": True}

        priority_data = Counter(c.priority.value for c in cases)
        status_data = Counter(c.status.value for c in cases)

        tag_data = Counter()
        for c in cases:
            tag_data.update(c.tags)

        daily_counts: Dict[str, int] = {}
        for c in cases:
            day = time.strftime("%Y-%m-%d", time.localtime(c.created_at))
            daily_counts[day] = daily_counts.get(day, 0) + 1

        resolution_by_priority: Dict[str, List[float]] = {}
        for c in cases:
            if c.resolution_time_min is not None:
                p = c.priority.value
                if p not in resolution_by_priority:
                    resolution_by_priority[p] = []
                resolution_by_priority[p].append(c.resolution_time_min)

        avg_resolution_by_priority = {
            p: sum(times) / len(times)
            for p, times in resolution_by_priority.items()
        }

        return {
            "priority_distribution": dict(priority_data),
            "status_distribution": dict(status_data),
            "top_tags": dict(tag_data.most_common(15)),
            "daily_case_count": daily_counts,
            "avg_resolution_by_priority": avg_resolution_by_priority,
            "total_cases": len(cases),
        }

    def _build_timeline(self, cases: List[IncidentCase]) -> List[Dict[str, Any]]:
        all_events = []
        for case in cases:
            for event in case.events:
                all_events.append({
                    "case_id": case.case_id,
                    "timestamp": event.timestamp,
                    "time_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp)),
                    "type": event.event_type,
                    "content": event.content[:100],
                    "priority": case.priority.value,
                })
        all_events.sort(key=lambda e: e["timestamp"], reverse=True)
        return all_events[:100]

    def _generate_recommendations(
        self,
        cases: List[IncidentCase],
        top_tags: List[tuple],
        resolution_times: List[float],
    ) -> List[str]:
        recommendations = []

        if top_tags:
            tag, count = top_tags[0]
            if count >= 3:
                recommendations.append(
                    f"Recurring issue detected: '{tag}' appeared in {count} cases. "
                    f"Consider creating a runbook or automated fix."
                )

        if resolution_times:
            avg = sum(resolution_times) / len(resolution_times)
            slow_cases = [t for t in resolution_times if t > avg * 2]
            if slow_cases:
                recommendations.append(
                    f"{len(slow_cases)} case(s) took >2x the average resolution time "
                    f"({avg:.0f} min). Review these for process improvements."
                )

        p0_cases = [c for c in cases if c.priority.value == "P0" and c.status == CaseStatus.OPEN]
        if p0_cases:
            recommendations.append(
                f"{len(p0_cases)} P0 (critical) case(s) are still open! Immediate attention required."
            )

        open_count = sum(1 for c in cases if c.status == CaseStatus.OPEN)
        if open_count > 5:
            recommendations.append(
                f"{open_count} cases are still open. Consider prioritizing resolution."
            )

        if not recommendations:
            recommendations.append("All systems nominal. No critical issues detected.")

        return recommendations
