from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st


DEFAULT_LOCAL_OAUTH_PATH = Path("secrets") / "yahoo_oauth.json"


@dataclass(frozen=True)
class YahooAuthConfig:
    league_key: str | None = None
    callback_uri: str = "oob"
    oauth_file: str | None = None
    consumer_key: str | None = None
    consumer_secret: str | None = None
    refresh_token: str | None = None
    access_token: str | None = None
    token_type: str | None = None
    token_time: float | None = None
    source_label: str = "not configured"

    @property
    def is_configured(self) -> bool:
        if self.oauth_file and Path(self.oauth_file).exists():
            return True

        return bool(self.consumer_key and self.consumer_secret and self.refresh_token)


def _get_streamlit_secret(flat_key: str, nested_key: str) -> tuple[Any | None, str | None]:
    try:
        if flat_key in st.secrets:
            return st.secrets[flat_key], "Streamlit secrets"

        if "yahoo" in st.secrets and nested_key in st.secrets["yahoo"]:
            return st.secrets["yahoo"][nested_key], "Streamlit secrets"
    except Exception:
        return None, None

    return None, None


def _get_config_value(
    env_keys: list[str],
    secret_flat_key: str,
    secret_nested_key: str,
) -> tuple[Any | None, str | None]:
    for env_key in env_keys:
        env_value = os.getenv(env_key)
        if env_value not in (None, ""):
            return env_value, "environment variables"

    return _get_streamlit_secret(secret_flat_key, secret_nested_key)


def _normalize_string(value: Any | None) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _normalize_float(value: Any | None) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_yahoo_auth_config(local_oauth_path: str | None = None) -> YahooAuthConfig:
    oauth_file = _normalize_string(local_oauth_path)
    if not oauth_file:
        oauth_file_value, _ = _get_config_value(
            ["YAHOO_OAUTH_FILE", "YAHOO_OAUTH_PATH"],
            "YAHOO_OAUTH_FILE",
            "oauth_file",
        )
        oauth_file = _normalize_string(oauth_file_value)

    if not oauth_file and DEFAULT_LOCAL_OAUTH_PATH.exists():
        oauth_file = str(DEFAULT_LOCAL_OAUTH_PATH)

    league_key, league_key_source = _get_config_value(
        ["YAHOO_LEAGUE_KEY"],
        "YAHOO_LEAGUE_KEY",
        "league_key",
    )
    callback_uri, callback_uri_source = _get_config_value(
        ["YAHOO_CALLBACK_URI", "YAHOO_REDIRECT_URI"],
        "YAHOO_CALLBACK_URI",
        "callback_uri",
    )
    consumer_key, consumer_key_source = _get_config_value(
        ["YAHOO_CONSUMER_KEY", "YAHOO_CLIENT_ID"],
        "YAHOO_CONSUMER_KEY",
        "consumer_key",
    )
    consumer_secret, consumer_secret_source = _get_config_value(
        ["YAHOO_CONSUMER_SECRET", "YAHOO_CLIENT_SECRET"],
        "YAHOO_CONSUMER_SECRET",
        "consumer_secret",
    )
    refresh_token, refresh_token_source = _get_config_value(
        ["YAHOO_REFRESH_TOKEN"],
        "YAHOO_REFRESH_TOKEN",
        "refresh_token",
    )
    access_token, access_token_source = _get_config_value(
        ["YAHOO_ACCESS_TOKEN"],
        "YAHOO_ACCESS_TOKEN",
        "access_token",
    )
    token_type, token_type_source = _get_config_value(
        ["YAHOO_TOKEN_TYPE"],
        "YAHOO_TOKEN_TYPE",
        "token_type",
    )
    token_time, token_time_source = _get_config_value(
        ["YAHOO_TOKEN_TIME"],
        "YAHOO_TOKEN_TIME",
        "token_time",
    )

    sources = {
        source
        for source in [
            league_key_source,
            callback_uri_source,
            consumer_key_source,
            consumer_secret_source,
            refresh_token_source,
            access_token_source,
            token_type_source,
            token_time_source,
        ]
        if source
    }

    if oauth_file and Path(oauth_file).exists() and not sources:
        source_label = "local OAuth file"
    elif sources:
        source_label = " / ".join(sorted(sources))
    elif oauth_file:
        source_label = "local OAuth file"
    else:
        source_label = "not configured"

    return YahooAuthConfig(
        league_key=_normalize_string(league_key),
        callback_uri=_normalize_string(callback_uri) or "oob",
        oauth_file=oauth_file,
        consumer_key=_normalize_string(consumer_key),
        consumer_secret=_normalize_string(consumer_secret),
        refresh_token=_normalize_string(refresh_token),
        access_token=_normalize_string(access_token),
        token_type=_normalize_string(token_type),
        token_time=_normalize_float(token_time),
        source_label=source_label,
    )
