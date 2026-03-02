"""
SFT Data Collector
Automatically collects high-quality Q&A pairs from DevOps-MAS interactions
for supervised fine-tuning of domain-specific models.
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SFTSample:
    """A single SFT training sample."""
    id: str
    instruction: str
    input: str  # additional context
    output: str  # expected response
    system_prompt: str = ""
    category: str = "general"  # log_analysis | metrics | visual | knowledge | retrieval
    quality_score: float = 0.0  # 0-1, used for filtering
    source: str = "devops_interaction"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class SFTDataCollector:
    """
    Collects and manages SFT training data from DevOps-MAS interactions.

    Data sources:
    - User queries + high-confidence agent responses
    - Resolved case summaries
    - Manual annotations
    - RAG-enhanced Q&A pairs
    """

    def __init__(self, data_dir: str = "data/sft"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.samples: List[SFTSample] = []
        self._load_existing()
        logger.info(f"SFTDataCollector initialized with {len(self.samples)} samples")

    def collect_from_interaction(
        self,
        query: str,
        response: str,
        confidence: float,
        agent_name: str,
        context: Optional[str] = None,
        min_confidence: float = 0.7,
    ) -> Optional[SFTSample]:
        """Auto-collect from agent interactions when confidence is high enough."""
        if confidence < min_confidence:
            return None
        if len(response.strip()) < 20:
            return None

        category_map = {
            "log_analysis_agent": "log_analysis",
            "metrics_analysis_agent": "metrics",
            "visual_analysis_agent": "visual",
            "knowledge_agent": "knowledge",
            "retriever_agent": "retrieval",
            "search_agent": "search",
            "comprehensive_agent": "comprehensive",
        }

        sample = SFTSample(
            id=hashlib.md5(f"{query}{response[:100]}".encode()).hexdigest()[:10],
            instruction=query,
            input=context or "",
            output=response,
            system_prompt="You are DevOps-MAS, an intelligent DevOps assistant.",
            category=category_map.get(agent_name, "general"),
            quality_score=confidence,
            source="auto_collect",
            metadata={"agent_name": agent_name, "confidence": confidence},
        )
        self.samples.append(sample)
        self._save_sample(sample)
        return sample

    def collect_from_case(
        self,
        title: str,
        problem: str,
        root_cause: str,
        solution: str,
        tags: List[str],
    ) -> SFTSample:
        """Create SFT sample from a resolved case."""
        instruction = f"Analyze and solve this DevOps issue: {title}"
        context = f"Problem description: {problem}\nTags: {', '.join(tags)}"
        output = (
            f"## Root Cause Analysis\n{root_cause}\n\n"
            f"## Solution\n{solution}"
        )

        sample = SFTSample(
            id=hashlib.md5(f"case_{title}".encode()).hexdigest()[:10],
            instruction=instruction,
            input=context,
            output=output,
            system_prompt="You are DevOps-MAS, an expert in diagnosing and resolving DevOps issues.",
            category="case_resolution",
            quality_score=0.9,
            source="resolved_case",
            metadata={"tags": tags},
        )
        self.samples.append(sample)
        self._save_sample(sample)
        return sample

    def add_manual_sample(
        self,
        instruction: str,
        output: str,
        input_context: str = "",
        category: str = "manual",
    ) -> SFTSample:
        """Add a manually curated sample."""
        sample = SFTSample(
            id=hashlib.md5(f"manual_{instruction}".encode()).hexdigest()[:10],
            instruction=instruction,
            input=input_context,
            output=output,
            system_prompt="You are DevOps-MAS, an intelligent DevOps assistant.",
            category=category,
            quality_score=1.0,
            source="manual",
        )
        self.samples.append(sample)
        self._save_sample(sample)
        return sample

    def export_alpaca_format(self, min_quality: float = 0.5) -> List[Dict[str, str]]:
        """Export in Alpaca format for fine-tuning."""
        filtered = [s for s in self.samples if s.quality_score >= min_quality]
        return [
            {
                "instruction": s.instruction,
                "input": s.input,
                "output": s.output,
            }
            for s in filtered
        ]

    def export_sharegpt_format(self, min_quality: float = 0.5) -> List[Dict[str, Any]]:
        """Export in ShareGPT format (multi-turn conversations)."""
        filtered = [s for s in self.samples if s.quality_score >= min_quality]
        result = []
        for s in filtered:
            conversations = []
            if s.system_prompt:
                conversations.append({"from": "system", "value": s.system_prompt})
            user_msg = s.instruction
            if s.input:
                user_msg += f"\n\nContext:\n{s.input}"
            conversations.append({"from": "human", "value": user_msg})
            conversations.append({"from": "gpt", "value": s.output})
            result.append({"conversations": conversations, "id": s.id})
        return result

    def export_to_file(self, format: str = "alpaca", output_path: Optional[str] = None) -> str:
        """Export dataset to JSON file."""
        if format == "alpaca":
            data = self.export_alpaca_format()
        elif format == "sharegpt":
            data = self.export_sharegpt_format()
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_path is None:
            output_path = str(self.data_dir / f"sft_dataset_{format}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(data)} samples to {output_path} in {format} format")
        return output_path

    def get_stats(self) -> Dict[str, Any]:
        from collections import Counter
        cats = Counter(s.category for s in self.samples)
        sources = Counter(s.source for s in self.samples)
        scores = [s.quality_score for s in self.samples]
        return {
            "total_samples": len(self.samples),
            "by_category": dict(cats),
            "by_source": dict(sources),
            "avg_quality_score": sum(scores) / len(scores) if scores else 0,
            "high_quality_count": sum(1 for s in scores if s >= 0.8),
        }

    def _save_sample(self, sample: SFTSample):
        path = self.data_dir / f"{sample.id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(sample), f, ensure_ascii=False, indent=2)

    def _load_existing(self):
        for path in self.data_dir.glob("*.json"):
            if path.name.startswith("sft_dataset"):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "instruction" in data:
                    self.samples.append(SFTSample(**data))
            except Exception as e:
                logger.debug(f"Skipping {path}: {e}")
