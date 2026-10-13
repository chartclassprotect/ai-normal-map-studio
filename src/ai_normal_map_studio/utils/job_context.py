"""Job context and pipeline protocol.

A JobContext travels through every stage. Stages mutate it in place and
return it. Fields:
    input_path   : source file
    output_dir   : where the writer drops the result
    height       : ingested float32 array (HxW or HxWx3)
    tensor       : normalized tensor ready for inference
    normal       : model output in [-1, 1], HWC
    output_path  : final written path
    meta         : free-form dict for stage bookkeeping
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

import numpy as np


@dataclass
class JobContext:
    input_path: Path
    output_dir: Path
    model_override: Optional[str] = None
    flip_green: bool = False

    height: Optional[np.ndarray] = None
    tensor: Optional[np.ndarray] = None
    normal: Optional[np.ndarray] = None
    output_path: Optional[Path] = None
    meta: dict[str, Any] = field(default_factory=dict)


class Pipeline(Protocol):
    def run(self, job: JobContext) -> JobContext: ...