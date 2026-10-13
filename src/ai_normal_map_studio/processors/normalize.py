"""Normalize processor.

Brings the ingested array into the shape and range the inference backend
expects. Handles:
    - height_to_normal : single channel, [0, 1]
    - diffuse_to_normal: 3 channels, [0, 1]
    - albedo_to_normal : 3 channels, [0, 1]
"""
from __future__ import annotations

import numpy as np

from ai_normal_map_studio.utils.job_context import JobContext


class NormalizeProcessor:
    def __init__(self, cfg: dict) -> None:
        self.mode = cfg["normalize"]["mode"]
        self.invert = cfg["normalize"]["invert_height"]
        self.scale = cfg["normalize"]["height_scale"]

    def __call__(self, job: JobContext) -> JobContext:
        arr = job.height
        if arr is None:
            raise RuntimeError("normalize: no height data on job")

        if self.mode == "height_to_normal":
            if arr.ndim != 2:
                raise ValueError("height_to_normal expects a single channel")
            if self.invert:
                arr = 1.0 - arr
            arr = np.clip(arr * self.scale, 0.0, 1.0)
        elif self.mode in ("diffuse_to_normal", "albedo_to_normal"):
            if arr.ndim != 3:
                raise ValueError(f"{self.mode} expects 3 channels")
        else:
            raise ValueError(f"unknown normalize mode: {self.mode}")

        job.tensor = arr.astype(np.float32)
        job.meta["normalize_mode"] = self.mode
        return job