"""Smoke test: run the pipeline on a synthetic height map, assert a
normal map comes out with plausible unit-length normals."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ai_normal_map_studio.bootstrap import build_pipeline
from ai_normal_map_studio.utils.job_context import JobContext


@pytest.fixture()
def synthetic_height(tmp_path: Path) -> Path:
    y, x = np.mgrid[0:256, 0:256].astype(np.float32)
    height = 0.5 + 0.5 * np.sin(x / 12.0) * np.cos(y / 12.0)
    im = Image.fromarray((height * 255).astype(np.uint8))
    out = tmp_path / "height.png"
    im.save(out)
    return out


def