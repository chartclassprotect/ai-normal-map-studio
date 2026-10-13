"""Image writer driver.

Remaps [-1, 1] normals to [0, 255] and writes a PNG/TIFF with the
configured suffix. Optionally stamps job metadata as PNG text chunks.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, PngImagePlugin

from ai_normal_map_studio.utils.job_context import JobContext


class ImageWriterDriver:
    def __init__(self, cfg: dict) -> None:
        self.fmt = cfg["output"]["format"]
        self.suffix = cfg["output"]["suffix"]
        self.write_meta = cfg["output"]["write_metadata"]

    def __call__(self, job: JobContext) -> JobContext:
        n = job.normal
        if n is None:
            raise RuntimeError("writer: no normal on job")

        rgb = ((n + 1.0) * 0.5 * 255.0).clip(0, 255).astype(np.uint8)
        im = Image.fromarray(rgb, mode="RGB")

        out = job.output_dir / f"{job.input_path.stem}{self.suffix}.{self.fmt}"
        out.parent.mkdir(parents=True, exist_ok=True)

        if self.write_meta and self.fmt == "png":
            meta = PngImagePlugin.PngInfo()
            for k, v in job.meta.items():
                meta.add_text(f"nmstudio.{k}", str(v))
            im.save(out, pnginfo=meta)
        else:
            im.save(out)

        job.output_path = out
        return job