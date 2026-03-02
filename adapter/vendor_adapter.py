from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import json

from .base_adapter import BaseAdapter, AdapterConfig


class VendorKBConfig(AdapterConfig):
    vendor_name: str = Field(..., description="Vendor name, e.g., Huawei, Alibaba Cloud")
    kb_root: str = Field(default="data/vendor_kb", description="Root directory for vendor KB")
    fine_tune_output: str = Field(default="data/fine_tune", description="Output directory for fine-tuned artifacts")


class VendorKnowledgeAdapter(BaseAdapter):
    """
    Adapter to integrate a vendor-specific documentation corpus for retrieval and fine-tuning workflows.
    Minimal responsibilities:
      - Normalize vendor docs into a simple JSONL dataset format
      - Provide manifest for RAG ingestion
      - Provide dataset splits for supervised fine-tuning jobs
    """

    def __init__(self, config: VendorKBConfig):
        super().__init__(config)
        self._manifest: Dict[str, Any] = {}

    async def connect(self):
        os.makedirs(self.config.kb_root, exist_ok=True)
        os.makedirs(self.config.fine_tune_output, exist_ok=True)

    async def handle_incoming(self, data: dict) -> Dict[str, Any]:
        action = data.get("action")
        if action == "index_manifest":
            return await self._build_manifest()
        if action == "prepare_finetune":
            return await self._prepare_finetune_dataset(data.get("split_ratio", 0.9))
        if action == "add_doc":
            return await self._add_doc(data.get("title"), data.get("content"), data.get("metadata", {}))
        return {"error": f"Unknown action: {action}"}

    async def send_response(self, response: dict):
        # No-op: push-based messaging not required for local adapter
        return None

    async def _add_doc(self, title: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        if not title or not content:
            return {"success": False, "error": "title and content required"}
        item = {"title": title, "content": content, "metadata": metadata}
        ds_path = os.path.join(self.config.kb_root, f"{self.config.vendor_name}_raw.jsonl")
        os.makedirs(os.path.dirname(ds_path), exist_ok=True)
        with open(ds_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return {"success": True, "path": ds_path}

    async def _build_manifest(self) -> Dict[str, Any]:
        ds_path = os.path.join(self.config.kb_root, f"{self.config.vendor_name}_raw.jsonl")
        manifest = {
            "vendor": self.config.vendor_name,
            "dataset_path": ds_path,
            "format": "jsonl",
            "fields": {"title": "str", "content": "str", "metadata": "object"},
        }
        self._manifest = manifest
        return {"success": True, "manifest": manifest}

    async def _prepare_finetune_dataset(self, split_ratio: float = 0.9) -> Dict[str, Any]:
        ds_path = os.path.join(self.config.kb_root, f"{self.config.vendor_name}_raw.jsonl")
        if not os.path.exists(ds_path):
            return {"success": False, "error": f"dataset not found: {ds_path}"}

        items: List[Dict[str, Any]] = []
        with open(ds_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    items.append(obj)
                except Exception:
                    continue
        n = len(items)
        if n == 0:
            return {"success": False, "error": "empty dataset"}
        split = max(1, int(n * split_ratio))
        train, eval_ = items[:split], items[split:]

        def _fmt(ex: Dict[str, Any]) -> Dict[str, Any]:
            # Supervised fine-tuning prompt style; adjust downstream as needed
            return {
                "instruction": ex["title"],
                "input": ex.get("metadata", {}),
                "output": ex["content"],
            }

        out_dir = os.path.join(self.config.fine_tune_output, self.config.vendor_name)
        os.makedirs(out_dir, exist_ok=True)
        train_path = os.path.join(out_dir, "train.jsonl")
        eval_path = os.path.join(out_dir, "eval.jsonl")
        with open(train_path, "w", encoding="utf-8") as f:
            for ex in train:
                f.write(json.dumps(_fmt(ex), ensure_ascii=False) + "\n")
        with open(eval_path, "w", encoding="utf-8") as f:
            for ex in eval_:
                f.write(json.dumps(_fmt(ex), ensure_ascii=False) + "\n")

        return {"success": True, "train": train_path, "eval": eval_path, "counts": {"train": len(train), "eval": len(eval_)}}


