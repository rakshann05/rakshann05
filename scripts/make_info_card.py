#!/usr/bin/env python3
"""Generate the animated terminal/neofetch info card."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"

ROWS = [
    ("Name", "Rakshann"),
    ("Role", "Computer Science Undergraduate"),
    ("College", "Amrita Vishwa Vidyapeetham"),
    ("Current Focus", "Backend Development"),
    ("Languages", "Java / Python / JavaScript / SQL"),
    ("Backend", "Spring Boot / Node / Flask"),
    ("Frontend", "React / Flutter"),
    ("Cloud", "AWS / Google Cloud"),
    ("Database", "PostgreSQL / MySQL"),
    ("Highlights", "NexusForge / DEWD Dashboard / OLabs Collab / Analyn"),
]


def render() -> None:
    width = 620
    height = 374
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Rakshann terminal information card</title>',
        '<desc id="desc">A terminal themed profile card with animated lines of personal and technical details.</desc>',
        "<style><![CDATA[",
        ".mono{font-family:'SFMono-Regular','Consolas','Liberation Mono',monospace}",
        ".prompt{fill:#69f0a0;font-size:16px;font-weight:700}",
        ".label{fill:#39d353;font-size:14px;font-weight:700}",
        ".value{fill:#d7ffe0;font-size:14px}",
        ".muted{fill:#7ee787;font-size:12px}",
        "]]></style>",
        '<rect width="620" height="374" rx="16" fill="#0d1117"/>',
        '<rect x="1" y="1" width="618" height="372" rx="16" fill="none" stroke="#30363d"/>',
        '<rect x="0" y="0" width="620" height="42" rx="16" fill="#161b22"/>',
        '<rect x="0" y="26" width="620" height="18" fill="#161b22"/>',
        '<circle cx="24" cy="21" r="6" fill="#ff5f56"/>',
        '<circle cx="46" cy="21" r="6" fill="#ffbd2e"/>',
        '<circle cx="68" cy="21" r="6" fill="#27c93f"/>',
        '<text class="mono muted" x="95" y="26">rakshann@github:~$ whoami</text>',
        '<text class="mono prompt" x="28" y="74">./neofetch --local-only</text>',
    ]

    y = 112
    for index, (label, value) in enumerate(ROWS):
        delay = 0.22 + index * 0.18
        escaped_label = html.escape(label.ljust(14))
        escaped_value = html.escape(value)
        parts.append(f'<g opacity="0" transform="translate(0 8)">')
        parts.append(f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.36s" fill="freeze"/>')
        parts.append(f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{delay:.2f}s" dur="0.36s" fill="freeze"/>')
        parts.append(f'<text class="mono label" x="36" y="{y}">{escaped_label}</text>')
        parts.append(f'<text class="mono value" x="178" y="{y}">: {escaped_value}</text>')
        parts.append("</g>")
        y += 25

    parts.extend(
        [
            '<rect x="34" y="336" width="552" height="1" fill="#238636" opacity="0.7"/>',
            '<text class="mono muted" x="36" y="358">zero third-party stats services / generated locally with Python</text>',
            "</svg>",
        ]
    )
    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    render()
