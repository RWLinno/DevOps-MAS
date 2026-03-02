"""
DevOps-MAS Case Tracker
Full lifecycle management for DevOps incidents:
  creation -> investigation -> diagnosis -> resolution -> postmortem
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CaseStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    DIAGNOSED = "diagnosed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, Enum):
    P0 = "P0"  # Critical / Service Down
    P1 = "P1"  # Major Impact
    P2 = "P2"  # Minor Impact
    P3 = "P3"  # Low Priority


@dataclass
class CaseEvent:
    timestamp: float
    event_type: str  # "created" | "message" | "agent_action" | "diagnosis" | "resolution" | "note"
    content: str
    agent_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentCase:
    case_id: str
    title: str
    description: str
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.P2
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    events: List[CaseEvent] = field(default_factory=list)
    related_logs: List[str] = field(default_factory=list)
    related_images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def resolution_time_min(self) -> Optional[float]:
        if self.resolved_at and self.created_at:
            return (self.resolved_at - self.created_at) / 60.0
        return None

    def add_event(
        self,
        event_type: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.events.append(
            CaseEvent(
                timestamp=time.time(),
                event_type=event_type,
                content=content,
                agent_name=agent_name,
                metadata=metadata or {},
            )
        )
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["priority"] = self.priority.value
        return d


class CaseTracker:
    """Manages the lifecycle of oncall cases."""

    def __init__(self, storage_dir: str = "data/cases"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cases: Dict[str, IncidentCase] = {}
        self._load_cases()
        logger.info(f"CaseTracker initialized with {len(self.cases)} cases")

    def create_case(
        self,
        title: str,
        description: str,
        priority: str = "P2",
        tags: Optional[List[str]] = None,
    ) -> IncidentCase:
        case_id = f"OC-{hashlib.md5(f'{time.time()}{title}'.encode()).hexdigest()[:6].upper()}"
        case = IncidentCase(
            case_id=case_id,
            title=title,
            description=description,
            priority=CasePriority(priority),
            tags=tags or [],
        )
        case.add_event("created", f"Case created: {title}")
        self.cases[case_id] = case
        self._save_case(case)
        logger.info(f"Case created: {case_id} - {title}")
        return case

    def update_status(self, case_id: str, status: CaseStatus, note: str = ""):
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        old_status = case.status
        case.status = status
        case.updated_at = time.time()
        if status == CaseStatus.RESOLVED:
            case.resolved_at = time.time()
        case.add_event(
            "status_change",
            f"Status changed: {old_status.value} -> {status.value}. {note}",
        )
        self._save_case(case)

    def add_diagnosis(self, case_id: str, root_cause: str, agent_name: Optional[str] = None):
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        case.root_cause = root_cause
        case.status = CaseStatus.DIAGNOSED
        case.add_event("diagnosis", f"Root cause identified: {root_cause}", agent_name=agent_name)
        self._save_case(case)

    def add_solution(self, case_id: str, solution: str, agent_name: Optional[str] = None):
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        case.solution = solution
        case.status = CaseStatus.RESOLVED
        case.resolved_at = time.time()
        case.add_event("resolution", f"Solution applied: {solution}", agent_name=agent_name)
        self._save_case(case)

    def add_message(self, case_id: str, content: str, agent_name: Optional[str] = None):
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        case.add_event("message", content, agent_name=agent_name)
        self._save_case(case)

    def add_log_reference(self, case_id: str, log_path: str):
        case = self.cases.get(case_id)
        if case:
            case.related_logs.append(log_path)
            self._save_case(case)

    def add_image_reference(self, case_id: str, image_path: str):
        case = self.cases.get(case_id)
        if case:
            case.related_images.append(image_path)
            self._save_case(case)

    def get_case(self, case_id: str) -> Optional[IncidentCase]:
        return self.cases.get(case_id)

    def list_cases(
        self,
        status: Optional[CaseStatus] = None,
        priority: Optional[CasePriority] = None,
        limit: int = 50,
    ) -> List[IncidentCase]:
        cases = list(self.cases.values())
        if status:
            cases = [c for c in cases if c.status == status]
        if priority:
            cases = [c for c in cases if c.priority == priority]
        cases.sort(key=lambda c: c.updated_at, reverse=True)
        return cases[:limit]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.cases)
        if total == 0:
            return {"total": 0}

        by_status = {}
        by_priority = {}
        resolved_times = []
        for c in self.cases.values():
            by_status[c.status.value] = by_status.get(c.status.value, 0) + 1
            by_priority[c.priority.value] = by_priority.get(c.priority.value, 0) + 1
            if c.resolution_time_min is not None:
                resolved_times.append(c.resolution_time_min)

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "avg_resolution_time_min": (
                sum(resolved_times) / len(resolved_times) if resolved_times else None
            ),
            "resolved_count": len(resolved_times),
        }

    def _save_case(self, case: IncidentCase):
        path = self.storage_dir / f"{case.case_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(case.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_cases(self):
        for path in self.storage_dir.glob("OC-*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["status"] = CaseStatus(data["status"])
                data["priority"] = CasePriority(data["priority"])
                data["events"] = [CaseEvent(**e) for e in data.get("events", [])]
                self.cases[data["case_id"]] = IncidentCase(**data)
            except Exception as e:
                logger.warning(f"Failed to load case {path}: {e}")
