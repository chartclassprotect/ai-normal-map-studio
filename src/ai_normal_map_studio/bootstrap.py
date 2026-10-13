"""Bootstrap: assemble the pipeline from config.

The pipeline is a linear chain of stages. Each stage is a callable that
consumes a JobContext and returns a JobContext. Order is fixed:

    ingest -> normalize -> infer -> postprocess -> write
"""
from __future__ import annotations

from pathlib import Path

from ai_normal_map_studio.handlers.registry import build_ingest_handler
from ai_normal_map_studio.processors.normalize import NormalizeProcessor
from ai_normal_map_studio.processors.inference import InferenceProcessor
from ai_normal_map_studio.processors.postprocess import PostprocessProcessor
from ai_normal_map_studio.drivers.image_writer import ImageWriterDriver
from ai_normal_map_studio.utils.config_loader import load_pipeline_config
from ai_normal_map_studio.utils.job_context import JobContext, Pipeline


class _Pipeline(Pipeline):
    def __init__(self, stages: list) -> None:
        self._stages = stages

    def run(self, job: JobContext) -> JobContext:
        ctx = job
        for stage in self._stages:
            ctx = stage(ctx)
        return ctx


def build_pipeline(config_path: Path) -> Pipeline:
    cfg = load_pipeline_config(config_path)

    stages = [
        build_ingest_handler(cfg),
        NormalizeProcessor(cfg),
        InferenceProcessor(cfg),
        PostprocessProcessor(cfg),
        ImageWriterDriver(cfg),
    ]
    return _Pipeline(stages)