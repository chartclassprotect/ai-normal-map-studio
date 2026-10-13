"""Height extractor.

Fallback path for diffuse inputs: derives a pseudo-height field from
luminance + local contrast before the normal model sees it. Cheap and
good enough for stylized assets.
"""
from __future__ import annotations

import numpy as np


def extract_height(diffuse: np.ndarray) -> np.ndarray:
    if diffuse.ndim != 3:
        raise ValueError("extract_height expects HWC input")
    lum = diffuse @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    gx = np.gradient(lum, axis=1)
    gy = np.gradient(lum, axis=0)
    contrast = np.sqrt(gx ** 2 + gy ** 2)
    height = lum * 0.7 + contrast * 0.3
    lo, hi = float(height.min()), float(height.max())
    if hi - lo > 1e-6:
        height = (height - lo) / (hi - lo)
    return height.astype(np.float32)