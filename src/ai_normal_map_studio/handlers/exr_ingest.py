"""OpenEXR ingest.

EXR files carry HDR height data that clips badly in 8-bit. We read the
first channel and rescale to [0, 1] using the file's own data window.
"""
from __future__ import annotations

import numpy as np

from ai_normal_map_studio.utils.job_context import JobContext


class ExrIngestHandler:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg

    def __call__(self, job: JobContext) -> JobContext:
        try:
            import OpenEXR  # type: ignore
            import Imath  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "OpenEXR python bindings required for .exr ingest"
            ) from exc

        f = OpenEXR.InputFile(str(job.input_path))
        header = f.header()
        dw = header["dataWindow"]
        w = dw.max.x - dw.min.x + 1
        h = dw.max.y - dw.min.y + 1
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        raw = f.channel(header["channels"].keys().__iter__().__next__(), pt)
        arr = np.frombuffer(raw, dtype=np.float32).reshape(h, w)

        lo, hi = float(arr.min()), float(arr.max())
        if hi - lo > 1e-6:
            arr = (arr - lo) / (hi - lo)

        job.height = arr.astype(np.float32)
        job.meta["source_format"] = "exr"
        job.meta["source_size"] = arr.shape
        return job