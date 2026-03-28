from __future__ import annotations


def build_matchup_rating(opponent_strength: int, ballpark_factor: int, home_away: str) -> str:
    """Convert raw matchup inputs into a simple text rating."""
    score = 100 - opponent_strength
    score += 5 if home_away == "Home" else 0
    score += 3 if ballpark_factor <= 98 else -3

    if score >= 58:
        return "Great"
    if score >= 50:
        return "Good"
    if score >= 43:
        return "Neutral"
    return "Risky"


def build_streamer_score(opponent_strength: int, ballpark_factor: int, projected_starts: int) -> int:
    """Create a simple 0-100 streamer score."""
    matchup_component = max(0, 100 - opponent_strength)
    park_component = max(0, 110 - ballpark_factor)
    two_start_bonus = 12 if projected_starts >= 2 else 0

    raw_score = (matchup_component * 0.55) + (park_component * 0.25) + 20 + two_start_bonus
    return max(0, min(100, round(raw_score)))
