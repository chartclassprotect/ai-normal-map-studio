"""Inference processor.

Wraps the ONNX runtime service and runs the model over the job tensor.
Tiles large inputs so VRAM stays bounded; overlaps tiles and blends on
the seams to avoid visible banding.
"""
from __future__ import annotations

import numpy as np

from ai_normal_map_studio.services.onnx_runtime import OnnxRuntimeService
from ai_normal_map_studio.utils.job_context import JobContext
from ai_normal_map_studio.utils.tiling import iter_tiles, blend_tiles


class InferenceProcessor:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.service = OnnxRuntimeService(cfg)

    def __call__(self, job: JobContext) -> JobContext:
        tensor = job.tensor
        if tensor is None:
            raise RuntimeError("inference: no tensor on job")

        tile = self.cfg["infer"]["tile_size"]
        overlap = self.cfg["infer"]["tile_overlap"]
        batch = self.cfg["infer"]["batch_size"]

        h, w = tensor.shape[:2]
        if h <= tile and w <= tile:
            out = self.service.run(tensor)
        else:
            out = blend_tiles(
                self.service,
                tensor,
                tile_size=tile,
                overlap=overlap,
                batch_size=batch,
            )

        job.normal = out
        job.meta["inference_tiles"] = max(1, (h // tile) * (w // tile))
        return job