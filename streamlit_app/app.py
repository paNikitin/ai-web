from pathlib import Path

import streamlit as st
from api import BackendAPI, BackendAPIError, cached_health, clear_api_caches
from state import clear_chat, init_state, logout
from styles import inject_styles
from utils import mask_token

APP_DIR = Path(__file__).resolve().parent
PAGES_DIR = APP_DIR / "pages"


st.set_page_config(page_title="AI WEB DEMO", layout="wide")

init_state()
inject_styles()

with st.sidebar:
    st.title("AI WEB DEMO")
    st.title("Streamlit frontend")
    st.text_input("Backend URL", key="api_url")

    if st.session_state.api_url != st.session_state.last_api_url:
        clear_api_caches()
        st.session_state.last_api_url = st.session_state.api_url

    if st.button("Refresh API status", use_container_width=True):
        clear_api_caches()

    try:
        health = cached_health(st.session_state.api_url)
    except BackendAPIError as e:
        st.error(f"Backend is unavailable. `e`:{e}")
    else:
        if health.get("status") == "ok":
            st.success("Backend OK")
        else:
            st.warning(f"Backend status: {health.get('status', 'unknown')}")

        st.caption(
            f"DB: {health.get('database', 'unknown')} | "
            f"Model loaded: {health.get('model_loaded', 'unknown')}"
        )

    st.divider()
    st.subheader("LLM Runtime")
    st.toggle("Streaming", key="streaming_enabled")
    st.slider("Temperature", key="temperature", min_value=0.0, max_value=2.0, value=1.0)
    st.slider("Max tokens", key="max_tokens", min_value=10, max_value=2000, value=10)
    st.slider(
        "History limit", key="history_limit", min_value=10, max_value=50, value=10
    )

    st.divider()
    st.subheader("Session")
    if st.session_state.auth:
        st.caption(f"User: `{st.session_state.username}`")
        st.caption(f"ID: `{st.session_state.user_id}`")
        st.caption(f"API key: `{mask_token(st.session_state.api_key)}`")
        if st.session_state.active_session_id:
            st.caption(f"Chat session: `{st.session_state.active_session_title}`")
            st.caption(f"Session ID: `{st.session_state.active_session_id}`")
        if st.button("Clear local chat", use_container_width=True):
            clear_chat()
            st.rerun()
        if st.button("Logout", use_container_width=True):
            logout()
            clear_api_caches()
            st.rerun()
    else:
        st.info("Not authenticated")

pages = [
    st.Page(
        PAGES_DIR / "1_auth.py", title="Auth", default=True, icon=":material/badge:"
    ),
    st.Page(PAGES_DIR / "2_chat.py", title="Chat", icon=":material/forum:"),
    st.Page(
        PAGES_DIR / "3_history.py",
        title="History",
        icon=":material/history:",
    ),
    st.Page(
        PAGES_DIR / "4_dashboard.py",
        title="Dashboard",
        icon=":material/monitoring:",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
