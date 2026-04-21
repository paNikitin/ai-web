import os
from typing import Any

import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://api:8001")


def init_state() -> None:
    defaults: dict[str, Any] = {
        "auth": False,
        "api_url": DEFAULT_BACKEND_URL,
        "last_api_url": DEFAULT_BACKEND_URL,
        "user_id": None,
        "username": None,
        "api_key": None,
        "last_issued_token": None,
        "active_session_id": None,
        "active_session_title": None,
        "loaded_session_id": None,
        "messages": [],
        "streaming_enabled": True,
        "temperature": 0.8,
        "max_tokens": 100,
        "history_limit": 20,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    print(f"Sess state: `{st.session_state}`")
    print(f"Sess state streaming: `{st.session_state.streaming_enabled}`")


def set_authenticated_user(user: dict[str, Any], api_key: str) -> None:
    st.session_state.auth = True
    st.session_state.user_id = user["id"]
    st.session_state.api_key = api_key
    st.session_state.username = user.get("username")
    st.session_state.active_session_id = None
    st.session_state.active_session_title = None
    st.session_state.loaded_session_id = None
    st.session_state.messages = []


def set_active_session(session: dict[str, Any] | None) -> None:

    if session is None:
        st.session_state.active_session_id = None
        st.session_state.active_session_title = None
        st.session_state.loaded_session_id = None
        st.session_state.messages = []
        return None

    st.session_state.active_session_id = session["id"]
    st.session_state.active_session_title = session.get("title")
    st.session_state.loaded_session_id = session["id"]
    st.session_state.messages = []


def clear_chat() -> None:
    st.session_state.messages = []


def logout() -> None:
    keep_keys = {
        "api_url": st.session_state.api_url,
        "last_api_url": st.session_state.api_url,
        "streaming_enabled": st.session_state.streaming_enabled,
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
        "history_limit": st.session_state.history_limit,
    }

    st.session_state.clear()
    init_state()
    for k, v in keep_keys.items():
        st.session_state[k] = v
