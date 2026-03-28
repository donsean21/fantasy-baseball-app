from __future__ import annotations

import pandas as pd
import streamlit as st

from clients.yahoo import YahooIntegrationError, fetch_free_agent_pitchers
from services.config import DEFAULT_LOCAL_OAUTH_PATH, YahooAuthConfig, get_yahoo_auth_config
from services.probable_starters import get_probable_starters
from services.scoring import build_matchup_rating, build_streamer_score


st.set_page_config(page_title="Fantasy Baseball Pitcher Streamer", layout="wide")


@st.cache_data(ttl=60 * 30, show_spinner=False)
def load_streamer_table(days: int = 7) -> tuple[pd.DataFrame, str | None]:
    starters, source_note = get_probable_starters(days=days)
    rows = []

    for starter in starters:
        matchup_rating = build_matchup_rating(
            opponent_strength=starter["opponent_strength"],
            ballpark_factor=starter["ballpark_factor"],
            home_away=starter["home_away"],
        )
        streamer_score = build_streamer_score(
            opponent_strength=starter["opponent_strength"],
            ballpark_factor=starter["ballpark_factor"],
            projected_starts=starter["projected_starts"],
        )

        rows.append(
            {
                "pitcher name": starter["pitcher_name"],
                "team": starter["team"],
                "opponent": starter["opponent"],
                "home/away": starter["home_away"],
                "start date": starter["start_date"],
                "projected starts": starter["projected_starts"],
                "matchup rating": matchup_rating,
                "streamer score": streamer_score,
                "venue": starter["venue_name"],
            }
        )

    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return dataframe, source_note

    return (
        dataframe.sort_values(by=["streamer score", "start date"], ascending=[False, True]),
        source_note,
    )


@st.cache_data(ttl=60 * 15, show_spinner=False)
def load_yahoo_free_agents(league_key: str, auth_config: YahooAuthConfig) -> pd.DataFrame:
    free_agents = fetch_free_agent_pitchers(league_key=league_key, auth_config=auth_config)
    return pd.DataFrame(free_agents)


st.title("Yahoo Fantasy Baseball Pitcher Streamer")
st.caption("Live MLB probable starters, with optional Yahoo free-agent filtering for your league.")

with st.sidebar:
    st.header("Filters")
    days_ahead = st.slider("Days ahead", min_value=3, max_value=7, value=7)
    minimum_score = st.slider("Minimum streamer score", min_value=0, max_value=100, value=40)
    show_top_n = st.selectbox("Show top options", options=[5, 10, 15], index=1)
    st.divider()
    st.header("Yahoo League")
    enable_yahoo = st.checkbox("Filter to Yahoo free agents", value=False)
    local_oauth_path = st.text_input(
        "Local OAuth file path (optional)",
        value=str(DEFAULT_LOCAL_OAUTH_PATH) if DEFAULT_LOCAL_OAUTH_PATH.exists() else "",
        help="Used for local development only when Streamlit secrets or environment variables are not set.",
    )
    yahoo_auth_config = get_yahoo_auth_config(local_oauth_path=local_oauth_path)
    league_key = st.text_input(
        "League key",
        value=yahoo_auth_config.league_key or "",
        placeholder="456.l.12345",
    )
    st.caption(f"Yahoo auth source: {yahoo_auth_config.source_label}.")
    st.caption(f"Yahoo redirect URI: {yahoo_auth_config.callback_uri}")

dataframe, source_note = load_streamer_table(days=days_ahead)

if source_note:
    st.warning(source_note)

if dataframe.empty:
    st.error("No probable starters were returned for the selected window.")
    st.stop()

if enable_yahoo:
    if not league_key.strip():
        st.info("Enter your Yahoo league key to filter the table down to free-agent starters.")
    elif not yahoo_auth_config.is_configured:
        st.warning(
            "Yahoo auth is not configured. Use a local OAuth file for development or add Streamlit "
            "secrets/environment variables for deployment."
        )
    else:
        try:
            yahoo_free_agents = load_yahoo_free_agents(
                league_key=league_key.strip(),
                auth_config=yahoo_auth_config,
            )
            if yahoo_free_agents.empty:
                st.warning("Yahoo returned no free-agent starting pitchers for this league.")
            else:
                dataframe = dataframe.merge(yahoo_free_agents, on="pitcher name", how="inner")
        except YahooIntegrationError as exc:
            st.warning(str(exc))

filtered = dataframe[dataframe["streamer score"] >= minimum_score].head(show_top_n)

col1, col2, col3 = st.columns(3)
col1.metric("Probable Starters", len(dataframe))
col2.metric("Filtered Options", len(filtered))
col3.metric("Best Streamer Score", int(dataframe["streamer score"].max()) if not dataframe.empty else 0)

st.subheader("Recommended Free-Agent Pitchers")
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.subheader("How the score works")
st.write(
    """
    The streamer score rewards weaker opposing lineups, friendlier ballparks,
    and pitchers projected for two starts in the next week.
    """
)

st.info(
    "MLB starters come from the public MLB Stats API. Yahoo filtering is optional and supports either "
    "a local OAuth JSON file or Streamlit secrets/environment variables."
)
