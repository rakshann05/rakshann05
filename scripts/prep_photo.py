#!/usr/bin/env python3
"""Prepare source-photo.jpg for ASCII rendering."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove


ROOT = Path(__file__).resolve().parents[1]


def prepare_photo(source: Path, output: Path, size: int) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing source photo: {source}")

    original = Image.open(source).convert("RGBA")
    isolated = remove(original)

    white = Image.new("RGBA", isolated.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, isolated).convert("RGB")
    composited.thumbnail((size, size), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (size, size), "white")
    x = (size - composited.width) // 2
    y = (size - composited.height) // 2
    canvas.paste(composited, (x, y))

    gray = ImageOps.grayscale(canvas)
    arr = np.array(gray)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    Image.fromarray(enhanced, mode="L").save(output)
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove background and enhance source-photo.jpg.")
    parser.add_argument("--source", type=Path, default=ROOT / "source-photo.jpg")
    parser.add_argument("--output", type=Path, default=ROOT / "source-prepped.png")
    parser.add_argument("--size", type=int, default=720)
    args = parser.parse_args()

    prepare_photo(args.source, args.output, args.size)


if __name__ == "__main__":
    main()
