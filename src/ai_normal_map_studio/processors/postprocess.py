"""Postprocess processor.

Flips the green channel for DirectX convention, applies strength, and
optionally smooths the tile seams one more time. Output stays in [-1, 1]
until the writer remaps to 8-bit.
"""
from __future__ import annotations

import numpy as np

from ai_normal_map_studio.utils.job_context import JobContext


class PostprocessProcessor:
    def __init__(self, cfg: dict) -> None:
        self.flip_green = cfg["postprocess"]["flip_green_channel"]
        self.strength = cfg["postprocess"]["strength"]
        self.smooth = cfg["postprocess"]["smooth_edges"]
        self.radius = cfg["postprocess"]["edge_radius"]

    def __call__(self, job: JobContext) -> JobContext:
        n = job.normal
        if n is None:
            raise RuntimeError("postprocess: no normal on job")

        if self.flip_green:
            n = n.copy()
            n[..., 1] *= -1.0

        if self.strength != 1.0:
            xy = n[..., :2] * self.strength
            z = np.sqrt(np.clip(1.0 - (xy ** 2).sum(axis=-1), 1e-6, 1.0))
            n = np.stack([xy[..., 0], xy[..., 1], z], axis=-1)

        if self.smooth and self.radius > 0:
            n = _box_blur(n, self.radius)

        job.normal = np.clip(n, -1.0, 1.0)
        return job


def _box_blur(arr: np.ndarray, radius: int) -> np.ndarray:
    k = 2 * radius + 1
    out = np.zeros_like(arr)
    for c in range(arr.shape[2]):
        ch = arr[..., c]
        padded = np.pad(ch, radius, mode="reflect")
        acc = np.zeros_like(ch)
        for dy in range(k):
            for dx in range(k):
                acc += padded[dy:dy + ch.shape[0], dx:dx + ch.shape[1]]
        out[..., c] = acc / (k * k)
    return out