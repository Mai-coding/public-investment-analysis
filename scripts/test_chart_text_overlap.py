#!/usr/bin/env python3
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chart_text_overlap import assert_no_text_overlap, find_text_overlaps


def main() -> int:
    fig, ax = plt.subplots(figsize=(4, 3))
    a = ax.text(0.5, 0.5, "Alpha")
    b = ax.text(0.5, 0.5, "Beta")
    assert find_text_overlaps(fig, [a, b]), "expected overlap not detected"
    try:
        assert_no_text_overlap(fig, [a, b])
    except RuntimeError:
        pass
    else:
        raise AssertionError("overlap gate did not fail")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4, 3))
    a = ax.text(0.1, 0.2, "Alpha")
    b = ax.text(0.8, 0.8, "Beta")
    assert_no_text_overlap(fig, [a, b])
    plt.close(fig)
    print("CHART TEXT OVERLAP TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
