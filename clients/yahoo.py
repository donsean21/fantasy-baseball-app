from __future__ import annotations

from pathlib import Path

from services.config import YahooAuthConfig


class YahooIntegrationError(RuntimeError):
    """Raised when Yahoo auth or league access fails."""


def _build_oauth_client(config: YahooAuthConfig):
    from yahoo_oauth import OAuth2

    if config.consumer_key and config.consumer_secret and config.refresh_token:
        return OAuth2(
            config.consumer_key,
            config.consumer_secret,
            callback_uri=config.callback_uri,
            access_token=config.access_token or "__refresh_from_token__",
            refresh_token=config.refresh_token,
            token_type=config.token_type or "bearer",
            token_time=config.token_time if config.token_time is not None else 0,
            store_file=False,
        )

    if config.oauth_file:
        oauth_path = Path(config.oauth_file)
        if not oauth_path.exists():
            raise YahooIntegrationError(
                f"Yahoo OAuth file was not found at '{oauth_path}'."
            )

        return OAuth2(None, None, from_file=str(oauth_path))

    raise YahooIntegrationError(
        "Yahoo auth is not configured. Add a local OAuth file or set: "
        "YAHOO_CONSUMER_KEY, YAHOO_CONSUMER_SECRET, YAHOO_REFRESH_TOKEN, "
        "and YAHOO_CALLBACK_URI."
    )


def fetch_free_agent_pitchers(
    league_key: str,
    auth_config: YahooAuthConfig,
) -> list[dict[str, object]]:
    """
    Fetch free-agent starting pitchers from a Yahoo fantasy baseball league.

    Supports either a local yahoo_oauth JSON file or secrets/env-based credentials.
    """
    try:
        import yahoo_fantasy_api as yfa
    except ImportError as exc:
        raise YahooIntegrationError(
            "Yahoo dependencies are not installed. Install requirements.txt first."
        ) from exc

    try:
        oauth = _build_oauth_client(auth_config)
        game = yfa.Game(oauth, "mlb")
        league = game.to_league(league_key)
        free_agents = league.free_agents("SP")
    except Exception as exc:  # pragma: no cover - third-party library surface
        raise YahooIntegrationError(
            "Unable to load Yahoo free agents. Check your league key and Yahoo OAuth settings."
        ) from exc

    pitchers: list[dict[str, object]] = []
    for player in free_agents:
        pitchers.append(
            {
                "pitcher name": player.get("name", ""),
                "yahoo player id": player.get("player_id"),
                "eligible positions": ", ".join(player.get("eligible_positions", [])),
            }
        )

    return pitchers
