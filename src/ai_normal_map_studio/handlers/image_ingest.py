"""Standard raster ingest via Pillow + numpy.

Reads PNG/JPG/BMP/TIFF, converts to float32 in [0, 1], and stores the
array on the job context under `job.height`. If the source is RGB, it is
luminance-converted unless `auto_grayscale` is disabled.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from ai_normal_map_studio.utils.job_context import JobContext


class ImageIngestHandler:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg

    def __call__(self, job: JobContext) -> JobContext:
        max_res = self.cfg["ingest"]["max_resolution"]
        auto_gray = self.cfg["ingest"]["auto_grayscale"]

        with Image.open(job.input_path) as im:
            im.load()
            if max(im.size) > max_res:
                raise ValueError(
                    f"image {im.size} exceeds max_resolution {max_res}"
                )
            arr = np.asarray(im).astype(np.float32) / 255.0

        if arr.ndim == 3 and arr.shape[2] == 4:
            arr = arr[..., :3]
        if arr.ndim == 3 and auto_gray:
            arr = arr @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

        job.height = arr
        job.meta["source_format"] = job.input_path.suffix.lstrip(".").lower()
        job.meta["source_size"] = arr.shape
        return job