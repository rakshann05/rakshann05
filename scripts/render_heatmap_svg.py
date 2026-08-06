#!/usr/bin/env python3
"""Render a local GitHub-style contribution heatmap SVG."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def load_data(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def calendar_days(data: dict[str, Any]) -> list[dict[str, Any]]:
    daily = data.get("daily", [])
    by_date = {dt.date.fromisoformat(day["date"]): day for day in daily}
    if by_date:
        end = max(by_date)
    else:
        end = dt.date.today()
    start = end - dt.timedelta(days=(53 * 7) - 1)
    return [
        by_date.get(start + dt.timedelta(days=i), {"date": (start + dt.timedelta(days=i)).isoformat(), "count": 0, "level": 0})
        for i in range(53 * 7)
    ]


def render(data: dict[str, Any], output: Path) -> None:
    days = calendar_days(data)
    cell = 11
    gap = 4
    left = 28
    top = 70
    grid_w = 53 * cell + 52 * gap
    grid_h = 7 * cell + 6 * gap
    width = left * 2 + grid_w
    height = 214

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Rakshann contribution heatmap</title>',
        '<desc id="desc">A locally generated GitHub-style contribution heatmap with total, current streak, and longest streak.</desc>',
        "<style><![CDATA[",
        ".mono{font-family:'SFMono-Regular','Consolas','Liberation Mono',monospace}",
        ".title{fill:#e6edf3;font-size:17px;font-weight:700}",
        ".metric{fill:#7ee787;font-size:13px}",
        ".muted{fill:#8b949e;font-size:11px}",
        ".cell{shape-rendering:geometricPrecision}",
        "]]></style>",
        f'<rect width="{width}" height="{height}" rx="16" fill="#0d1117"/>',
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="16" fill="none" stroke="#30363d"/>',
        '<text class="mono title" x="28" y="33">rakshann@github:~$ ./contributions.sh</text>',
        f'<text class="mono metric" x="28" y="55">{data.get("total_contributions", 0)} total contributions</text>',
        f'<text class="mono metric" x="248" y="55">current streak: {data.get("current_streak", 0)} days</text>',
        f'<text class="mono metric" x="442" y="55">longest streak: {data.get("longest_streak", 0)} days</text>',
    ]

    for index, day in enumerate(days):
        col = index // 7
        row = index % 7
        x = left + col * (cell + gap)
        y = top + row * (cell + gap)
        level = max(0, min(int(day.get("level", 0)), 5))
        count = int(day.get("count", 0))
        label = html.escape(f'{day["date"]}: {count} contribution{"s" if count != 1 else ""}')
        delay = (col + row) * 0.018
        parts.append(f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{PALETTE[level]}" opacity="0">')
        parts.append(f"<title>{label}</title>")
        parts.append(f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.28s" fill="freeze"/>')
        parts.append("</rect>")

    legend_y = top + grid_h + 31
    parts.append(f'<text class="mono muted" x="{left}" y="{legend_y}">Less</text>')
    legend_x = left + 38
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{legend_x + i * 17}" y="{legend_y - 10}" width="11" height="11" rx="3" fill="{color}"/>')
    parts.append(f'<text class="mono muted" x="{legend_x + 112}" y="{legend_y}">More</text>')

    best = data.get("best_day", {})
    best_text = f'best day: {best.get("date", "n/a")} / {best.get("count", 0)}'
    parts.append(f'<text class="mono muted" x="{width - 220}" y="{legend_y}">{html.escape(best_text)}</text>')
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render contrib-heatmap.svg from contribution JSON.")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "contributions.json")
    parser.add_argument("--output", type=Path, default=ROOT / "contrib-heatmap.svg")
    args = parser.parse_args()

    render(load_data(args.input), args.output)


if __name__ == "__main__":
    main()
