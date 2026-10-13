"""Handler registry — maps file extensions to ingest handlers."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from ai_normal_map_studio.handlers.image_ingest import ImageIngestHandler
from ai_normal_map_studio.handlers.exr_ingest import ExrIngestHandler
from ai_normal_map_studio.utils.job_context import JobContext

_HANDLERS: dict[str, type] = {
    "png": ImageIngestHandler,
    "jpg": ImageIngestHandler,
    "jpeg": ImageIngestHandler,
    "bmp": ImageIngestHandler,
    "tif": ImageIngestHandler,
    "tiff": ImageIngestHandler,
    "exr": ExrIngestHandler,
}


def build_ingest_handler(cfg: dict) -> Callable[[JobContext], JobContext]:
    accepted = set(cfg["ingest"]["accepted_formats"])

    def _dispatch(job: JobContext) -> JobContext:
        ext = job.input_path.suffix.lower().lstrip(".")
        if ext not in accepted:
            raise ValueError(f"unsupported format: .{ext}")
        handler_cls = _HANDLERS.get(ext)
        if handler_cls is None:
            raise ValueError(f"no handler registered for .{ext}")
        return handler_cls(cfg)(job)

    return _dispatch


def supported_extensions() -> list[str]:
    return sorted(_HANDLERS.keys())