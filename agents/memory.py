"""
Agent Memory System
Provides short-term (conversation), long-term (persistent), and episodic memory
for multi-agent collaboration in DevOps-MAS scenarios.
"""

import hashlib
import json
import logging
import os
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    id: str
    timestamp: float
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_name: Optional[str] = None
    session_id: Optional[str] = None
    case_id: Optional[str] = None
    embedding: Optional[List[float]] = None


@dataclass
class EpisodicMemory:
    """A resolved DevOps-MAS case stored as episodic memory."""
    case_id: str
    title: str
    problem_description: str
    root_cause: str
    solution: str
    steps: List[str]
    tags: List[str]
    resolution_time_min: float
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentMemory:
    """
    Unified memory system for DevOps-MAS.

    - short_term: sliding-window conversation buffer (last N turns)
    - long_term: persistent knowledge base (JSON file backed)
    - episodic: resolved case history for experience-based reasoning
    """

    def __init__(
        self,
        memory_dir: str = "data/memory",
        short_term_limit: int = 50,
        session_id: Optional[str] = None,
    ):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or hashlib.md5(
            str(time.time()).encode()
        ).hexdigest()[:12]

        self.short_term: deque[MemoryEntry] = deque(maxlen=short_term_limit)
        self.long_term: List[MemoryEntry] = []
        self.episodes: List[EpisodicMemory] = []

        self._load_persistent_memory()
        logger.info(
            f"AgentMemory initialized: session={self.session_id}, "
            f"episodes={len(self.episodes)}, long_term={len(self.long_term)}"
        )

    # ---- Short-term (conversation) ----

    def add_message(
        self,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        case_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            id=hashlib.md5(f"{time.time()}{content[:50]}".encode()).hexdigest()[:10],
            timestamp=time.time(),
            role=role,
            content=content,
            agent_name=agent_name,
            session_id=self.session_id,
            case_id=case_id,
            metadata=metadata or {},
        )
        self.short_term.append(entry)
        return entry

    def get_conversation_history(
        self, last_n: Optional[int] = None
    ) -> List[Dict[str, str]]:
        items = list(self.short_term)
        if last_n:
            items = items[-last_n:]
        return [{"role": e.role, "content": e.content} for e in items]

    def get_context_window(self, max_tokens_estimate: int = 4000) -> List[Dict[str, str]]:
        """Get as many recent messages as fit within an approximate token budget."""
        messages: List[Dict[str, str]] = []
        char_budget = max_tokens_estimate * 4
        total = 0
        for entry in reversed(list(self.short_term)):
            total += len(entry.content)
            if total > char_budget:
                break
            messages.insert(0, {"role": entry.role, "content": entry.content})
        return messages

    # ---- Long-term (persistent knowledge) ----

    def store_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        entry = MemoryEntry(
            id=hashlib.md5(content.encode()).hexdigest()[:10],
            timestamp=time.time(),
            role="system",
            content=content,
            metadata=metadata or {},
            session_id=self.session_id,
        )
        self.long_term.append(entry)
        self._save_persistent_memory()
        return entry

    def search_knowledge(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """Simple keyword-based search over long-term memory."""
        query_words = set(query.lower().split())
        scored: List[tuple] = []
        for entry in self.long_term:
            content_words = set(entry.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap / max(len(query_words), 1), entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]

    # ---- Episodic (resolved case history) ----

    def add_episode(self, episode: EpisodicMemory):
        self.episodes.append(episode)
        self._save_persistent_memory()
        logger.info(f"Episode stored: {episode.case_id} - {episode.title}")

    def search_episodes(self, query: str, top_k: int = 3) -> List[EpisodicMemory]:
        """Find similar past cases."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        scored: List[tuple] = []
        for ep in self.episodes:
            text = f"{ep.title} {ep.problem_description} {ep.root_cause} {' '.join(ep.tags)}"
            text_words = set(text.lower().split())
            overlap = len(query_words & text_words)
            tag_bonus = sum(1 for t in ep.tags if t.lower() in query_lower)
            score = overlap + tag_bonus * 2
            if score > 0:
                scored.append((score, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]

    def get_all_episodes(self) -> List[EpisodicMemory]:
        return list(self.episodes)

    # ---- Persistence ----

    def _save_persistent_memory(self):
        data = {
            "long_term": [asdict(e) for e in self.long_term],
            "episodes": [asdict(e) for e in self.episodes],
        }
        path = self.memory_dir / "persistent_memory.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_persistent_memory(self):
        path = self.memory_dir / "persistent_memory.json"
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.long_term = [
                MemoryEntry(**e) for e in data.get("long_term", [])
            ]
            self.episodes = [
                EpisodicMemory(**e) for e in data.get("episodes", [])
            ]
        except Exception as e:
            logger.warning(f"Failed to load persistent memory: {e}")

    def clear_session(self):
        self.short_term.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "short_term_messages": len(self.short_term),
            "long_term_entries": len(self.long_term),
            "episodic_cases": len(self.episodes),
        }
