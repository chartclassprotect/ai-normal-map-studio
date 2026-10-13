"""Tile iteration and seam blending for large inputs.

`iter_tiles` yields (y, x, h, w) windows with overlap. `blend_tiles`
runs the service on each window and feather-blends them back together
with a raised-cosine weight so seams aren't visible.
"""
from __future__ import annotations

from typing import Iterator

import numpy as np


def iter_tiles(
    shape: tuple[int, int],
    tile_size: int,
    overlap: int,
) -> Iterator[tuple[int, int, int, int]]:
    h, w = shape
    step = max(1, tile_size - overlap)
    for y in range(0, h, step):
        for x in range(0, w, step):
            y1 = min(y + tile_size, h)
            x1 = min(x + tile_size, w)
            yield y, x, y1 - y, x1 - x


def _feather(h: int, w: int) -> np.ndarray:
    fy = np.hanning(h).astype(np.float32)
    fx = np.hanning(w).astype(np.float32)
    weight = np.outer(fy, fx)
    weight = np.clip(weight, 1e-3, None)
    return weight


def blend_tiles(service, tensor: np.ndarray, tile_size: int, overlap: int,
                batch_size: int) -> np.ndarray:
    h, w = tensor.shape[:2]
    acc = np.zeros((h, w, 3), dtype=np.float32)
    wsum = np.zeros((h, w, 1), dtype=np.float32)

    for y, x, th, tw in iter_tiles((h, w), tile_size, overlap):
        patch = tensor[y:y + th, x:x + tw]
        out = service.run(patch)
        if out.shape[2] != 3:
            raise RuntimeError(f"unexpected model output channels: {out.shape[2]}")
        weight = _feather(th, tw)[..., None]
        acc[y:y + th, x:x + tw] += out * weight
        wsum[y:y + th, x:x + tw] += weight

    return (acc / np.clip(wsum, 1e-6, None)).astype(np.float32)