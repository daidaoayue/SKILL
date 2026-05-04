"""Classify a file path into one of the buckets defined by project.toml."""
from __future__ import annotations
from typing import Mapping

BUCKETS = (
    "code", "experiment_data", "paper", "reading",
    "theory", "figures", "checkpoint_signal", "uncategorized",
)


class BucketClassifier:
    def __init__(self, config: Mapping[str, Mapping]) -> None:
        # config[bucket_name] = {"roots": [...], "exts": [...]}
        self._cfg = config

    @staticmethod
    def _matches_root(rel: str, root: str) -> bool:
        rel = rel.replace("\\", "/")
        if "**" in root:
            # "**/ppt_figures" — any depth, exact dir name match
            tail = root.replace("**/", "").rstrip("/")
            parts = rel.split("/")
            if tail in parts:
                return True
            # Allow nested cases like "Forecasting/sub/ppt_figures/x.png"
            for i in range(len(parts)):
                if "/".join(parts[:i+1]).endswith("/" + tail) or parts[i] == tail:
                    return True
            return False
        # Plain prefix match: "Forecasting/output" matches "Forecasting/output/x.json"
        return rel == root or rel.startswith(root.rstrip("/") + "/")

    def classify(self, rel_path: str) -> str:
        rel = rel_path.replace("\\", "/")
        ext = "." + rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        # Order matters: more-specific buckets before more-general ones.
        # checkpoint_signal & experiment_data live UNDER code roots, so check them first.
        order = ("checkpoint_signal", "experiment_data", "figures", "theory",
                 "paper", "reading", "code")
        for name in order:
            cfg = self._cfg.get(name)
            if not cfg:
                continue
            roots = cfg.get("roots", [])
            exts = [e.lower() for e in cfg.get("exts", [])]
            if exts and ext not in exts:
                continue
            for r in roots:
                if self._matches_root(rel, r):
                    return name
        return "uncategorized"
