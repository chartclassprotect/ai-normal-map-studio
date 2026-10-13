"""Config loaders for pipeline.yaml and models.yaml."""
from __future__ import annotations

from pathlib import Path

import yaml


def load_pipeline_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_model_registry(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["models"]