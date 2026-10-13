"""Detail booster.

Second-stage refinement: runs the detail_booster_v2 model over an
already-generated normal map to sharpen micro-surface detail without
re-tiling the base inference.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ai_normal_map_studio.services.onnx_runtime import OnnxRuntimeService


class DetailBooster:
    def __init__(self, cfg: dict) -> None:
        cfg = dict(cfg)
        cfg["infer"] = dict(cfg["infer"], model_name="detail_booster_v2")
        self.service = OnnxRuntimeService(cfg)

    def boost(self, normal: np.ndarray, strength: float = 0.5) -> np.ndarray:
        base = normal
        refined = self.service.run(normal)
        out = base * (1.0 - strength) + refined * strength
        return out.astype(np.float32)