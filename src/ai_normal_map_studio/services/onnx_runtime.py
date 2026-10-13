"""ONNX Runtime service.

Loads a model from config/models.yaml, holds the session, and exposes a
single `run(tensor) -> np.ndarray` entry point. Device selection is
`auto | cpu | cuda`; auto prefers CUDA when available.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import onnxruntime as ort
except ImportError:  # pragma: no cover
    ort = None  # type: ignore

from ai_normal_map_studio.utils.config_loader import load_model_registry


class OnnxRuntimeService:
    def __init__(self, cfg: dict) -> None:
        if ort is None:
            raise RuntimeError("onnxruntime is not installed")
        self.cfg = cfg
        registry = load_model_registry(Path("config/models.yaml"))
        model_name = cfg["infer"].get("model_name") or "nmgen_v4"
        spec = registry[model_name]
        self.spec = spec

        providers = self._providers(cfg["infer"]["device"])
        self.session = ort.InferenceSession(spec["path"], providers=providers)
        self.input_name = self.session.get_inputs()[0].name

    @staticmethod
    def _providers(device: str) -> list[str]:
        if device == "cpu":
            return ["CPUExecutionProvider"]
        if device == "cuda":
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        available = ort.get_available_providers()
        if "CUDAExecutionProvider" in available:
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def run(self, tensor: np.ndarray) -> np.ndarray:
        x = tensor
        if x.ndim == 2:
            x = x[None, None, ...]
        elif x.ndim == 3:
            x = x.transpose(2, 0, 1)[None, ...]
        x = x.astype(np.float32)

        out = self.session.run(None, {self.input_name: x})[0]
        out = out[0].transpose(1, 2, 0)  # NCHW -> HWC
        return out.astype(np.float32)