from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from clients.mlb import MlbApiError, fetch_probable_starters
from data.reference import BALLPARK_FACTOR, OPPONENT_STRENGTH


def get_probable_starters(days: int = 7) -> tuple[list[dict[str, Any]], str | None]:
    """Return probable starters enriched with simple matchup inputs."""
    start = date.today()
    end = start + timedelta(days=days - 1)

    try:
        raw_starters = fetch_probable_starters(start_date=start, end_date=end)
        source_note = None
    except MlbApiError as exc:
        raw_starters = []
        source_note = str(exc)

    projected_counts = Counter(starter["pitcher_name"] for starter in raw_starters)
    starters: list[dict[str, Any]] = []

    for starter in raw_starters:
        park_team = starter["park_team"]
        opponent = starter["opponent"]
        starters.append(
            {
                **starter,
                "projected_starts": projected_counts[starter["pitcher_name"]],
                "opponent_strength": OPPONENT_STRENGTH.get(opponent, 50),
                "ballpark_factor": BALLPARK_FACTOR.get(park_team, 100),
            }
        )

    return starters, source_note
