from __future__ import annotations

import json
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


MLB_SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
MLB_API_TIMEOUT_SECONDS = 10


class MlbApiError(RuntimeError):
    """Raised when the MLB Stats API cannot be reached or parsed."""


def fetch_probable_starters(start_date: date, end_date: date) -> list[dict[str, Any]]:
    """Fetch probable starters from the public MLB Stats API schedule endpoint."""
    params = {
        "sportId": 1,
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "hydrate": "probablePitcher,team",
    }
    url = f"{MLB_SCHEDULE_URL}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=MLB_API_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise MlbApiError(f"Unable to fetch MLB probable starters: {exc}") from exc

    starters: list[dict[str, Any]] = []
    for schedule_date in payload.get("dates", []):
        game_date = schedule_date.get("date")
        for game in schedule_date.get("games", []):
            teams = game.get("teams", {})
            home_team = teams.get("home", {}).get("team", {})
            away_team = teams.get("away", {}).get("team", {})
            venue = game.get("venue", {})

            home_probable = teams.get("home", {}).get("probablePitcher")
            away_probable = teams.get("away", {}).get("probablePitcher")

            if home_probable:
                starters.append(
                    {
                        "pitcher_name": home_probable.get("fullName", "Unknown"),
                        "team": home_team.get("abbreviation", home_team.get("name", "UNK")),
                        "opponent": away_team.get("abbreviation", away_team.get("name", "UNK")),
                        "home_away": "Home",
                        "start_date": game_date,
                        "venue_name": venue.get("name", ""),
                        "park_team": home_team.get("abbreviation", home_team.get("name", "UNK")),
                    }
                )

            if away_probable:
                starters.append(
                    {
                        "pitcher_name": away_probable.get("fullName", "Unknown"),
                        "team": away_team.get("abbreviation", away_team.get("name", "UNK")),
                        "opponent": home_team.get("abbreviation", home_team.get("name", "UNK")),
                        "home_away": "Away",
                        "start_date": game_date,
                        "venue_name": venue.get("name", ""),
                        "park_team": home_team.get("abbreviation", home_team.get("name", "UNK")),
                    }
                )

    return starters
