#!/usr/bin/env python3
"""Detect overlapping Matplotlib text artists at final rendered size.

Chart scripts should collect title/annotation/data-label Text artists and call
``assert_no_text_overlap`` immediately before saving. This is a detection gate,
not an automatic layout engine: when it fails, change lanes, offsets, wrapping,
figure size or split the chart.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TextOverlap:
    left: str
    right: str


def _label(artist) -> str:
    text = getattr(artist, "get_text", lambda: "")() or ""
    return " ".join(str(text).split())[:80] or "<blank>"


def find_text_overlaps(fig, artists: Iterable, pad_px: float = 3.0) -> list[TextOverlap]:
    """Return pairwise overlaps for visible, non-empty text artists."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes: list[tuple[object, object]] = []
    for artist in artists:
        if artist is None or not getattr(artist, "get_visible", lambda: True)():
            continue
        if not (getattr(artist, "get_text", lambda: "")() or "").strip():
            continue
        try:
            box = artist.get_window_extent(renderer=renderer).expanded(
                1 + pad_px / max(1.0, artist.get_window_extent(renderer=renderer).width),
                1 + pad_px / max(1.0, artist.get_window_extent(renderer=renderer).height),
            )
        except Exception:
            continue
        boxes.append((artist, box))

    overlaps: list[TextOverlap] = []
    for i, (a, box_a) in enumerate(boxes):
        for b, box_b in boxes[i + 1 :]:
            if box_a.overlaps(box_b):
                overlaps.append(TextOverlap(_label(a), _label(b)))
    return overlaps


def assert_no_text_overlap(fig, artists: Iterable, pad_px: float = 3.0) -> None:
    overlaps = find_text_overlaps(fig, artists, pad_px=pad_px)
    if overlaps:
        preview = "; ".join(f"{x.left!r} ↔ {x.right!r}" for x in overlaps[:12])
        extra = f" (+{len(overlaps)-12} more)" if len(overlaps) > 12 else ""
        raise RuntimeError(
            "Chart text-overlap gate failed at final render size: " + preview + extra
        )
