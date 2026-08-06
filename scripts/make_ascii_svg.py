#!/usr/bin/env python3
"""Render a locally generated animated ASCII portrait SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
RAMP = " .`:-=+*cs#%@"


def image_to_ascii(path: Path, width: int, height: int) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prepared image: {path}")

    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    pixels = np.asarray(img, dtype=np.float32)
    levels = np.clip((255.0 - pixels) / 255.0 * (len(RAMP) - 1), 0, len(RAMP) - 1)
    chars = np.array(list(RAMP))[levels.astype(np.int16)]
    return ["".join(row.tolist()).rstrip() for row in chars]


def render_svg(lines: list[str], output: Path) -> None:
    char_w = 7
    line_h = 11
    pad_x = 20
    pad_y = 26
    width_chars = max(len(line) for line in lines)
    width = pad_x * 2 + width_chars * char_w
    height = pad_y * 2 + len(lines) * line_h
    duration = 5.8
    per_line = duration / len(lines)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Animated ASCII portrait of Rakshann</title>",
        "<desc id=\"desc\">A terminal styled ASCII portrait that types once from top to bottom.</desc>",
        "<style><![CDATA[",
        "svg{background:#050807;border-radius:14px}",
        ".ascii{font-family:'SFMono-Regular','Consolas','Liberation Mono',monospace;font-size:10px;fill:#7CFF9B;white-space:pre}",
        ".cursor{fill:#7CFF9B}",
        "]]></style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="#050807"/>',
        f'<rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="10" fill="none" stroke="#153b24"/>',
        "<defs>",
    ]

    cursor_values: list[str] = []
    cursor_times: list[str] = []
    for row, line in enumerate(lines):
        y = pad_y + row * line_h
        delay = row * per_line
        row_duration = max(0.05, per_line * 0.88)
        line_width = len(line) * char_w
        parts.append(f'<clipPath id="row-{row}"><rect x="{pad_x}" y="{y - line_h}" width="0" height="{line_h + 2}">')
        parts.append(f'<animate attributeName="width" from="0" to="{line_width}" begin="{delay:.3f}s" dur="{row_duration:.3f}s" fill="freeze" calcMode="linear"/>')
        parts.append("</rect></clipPath>")
        cursor_values.extend([f"{pad_x},{y - 9}", f"{pad_x + line_width},{y - 9}"])
        cursor_times.extend([f"{delay / duration:.4f}", f"{min(1, (delay + row_duration) / duration):.4f}"])

    cursor_times.append("1")
    cursor_values.append(f"{pad_x + width_chars * char_w},{pad_y + (len(lines) - 1) * line_h - 9}")
    parts.append("</defs>")

    for row, line in enumerate(lines):
        y = pad_y + row * line_h
        escaped = html.escape(line)
        parts.append(f'<text class="ascii" x="{pad_x}" y="{y}" clip-path="url(#row-{row})">{escaped}</text>')

    parts.extend(
        [
            f'<rect class="cursor" width="6" height="11" x="{pad_x}" y="{pad_y - 9}" opacity="0">',
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.92;0.94;1" begin="0s" dur="{duration + 0.8:.2f}s" fill="freeze"/>',
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(cursor_values)}" keyTimes="{";".join(cursor_times)}" begin="0s" dur="{duration:.2f}s" fill="freeze"/>',
            '<animate attributeName="fill-opacity" values="1;0;1;0;1;0;1" begin="0s" dur="1.1s" repeatCount="5" fill="freeze"/>',
            "</rect>",
            "</svg>",
        ]
    )
    output.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate rakshann-ascii.svg from source-prepped.png.")
    parser.add_argument("--input", type=Path, default=ROOT / "source-prepped.png")
    parser.add_argument("--output", type=Path, default=ROOT / "rakshann-ascii.svg")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=53)
    args = parser.parse_args()

    render_svg(image_to_ascii(args.input, args.width, args.height), args.output)


if __name__ == "__main__":
    main()
