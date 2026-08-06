#!/usr/bin/env python3
"""Fetch public GitHub contributions without GraphQL or tokens."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
USERNAME = "rakshann05"
CONTRIB_URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(text: str | None) -> int:
    if not text:
        return 0
    lowered = text.lower()
    if "no contributions" in lowered:
        return 0
    match = re.search(r"([\d,]+)\s+contribution", lowered)
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "rakshann05-profile-local-generator/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def parse_contributions(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    days: list[dict[str, Any]] = []
    tooltips = {tip.get("for"): tip.get_text(" ", strip=True) for tip in soup.select("tool-tip[for]")}

    for cell in soup.select("[data-date]"):
        date = cell.get("data-date")
        if not date:
            continue
        count = parse_count(
            cell.get("data-tooltip-text")
            or cell.get("aria-label")
            or tooltips.get(cell.get("id"))
        )
        level_text = cell.get("data-level") or cell.get("data-intensity") or "0"
        try:
            level = int(level_text)
        except ValueError:
            level = 0
        days.append({"date": date, "count": count, "level": max(0, min(level, 4))})

    deduped = {day["date"]: day for day in days}
    return [deduped[date] for date in sorted(deduped)]


def streaks(days: list[dict[str, Any]]) -> tuple[int, int]:
    by_date = {dt.date.fromisoformat(day["date"]): day["count"] for day in days}
    if not by_date:
        return 0, 0

    longest = 0
    running = 0
    cursor = min(by_date)
    end = max(by_date)
    while cursor <= end:
        if by_date.get(cursor, 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
        cursor += dt.timedelta(days=1)

    current = 0
    cursor = end
    while cursor >= min(by_date) and by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= dt.timedelta(days=1)
    return current, longest


def build_payload(days: list[dict[str, Any]]) -> dict[str, Any]:
    monthly: dict[str, int] = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]

    total = sum(day["count"] for day in days)
    current, longest = streaks(days)
    best_day = max(days, key=lambda day: day["count"], default={"date": None, "count": 0, "level": 0})

    return {
        "username": USERNAME,
        "source": CONTRIB_URL,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "year_total": total,
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "daily": days,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub contribution calendar HTML and store JSON.")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "contributions.json")
    args = parser.parse_args()

    html = fetch_html(CONTRIB_URL)
    days = parse_contributions(html)
    if not days:
        raise RuntimeError("No contribution cells were found in GitHub's public contribution HTML.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_payload(days), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
