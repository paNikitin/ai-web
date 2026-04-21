from typing import Any

import pandas as pd
import streamlit as st


def mask_token(token: str | None) -> str:
    if not token:
        return "not set"
    if len(token) <= 10:
        return token
    return f"{token[:4]}..{token[-4:]}"


def require_auth() -> None:
    if not st.session_state.auth or not st.session_state.api_key:
        st.warning("Log in first / Create user")
        st.stop()


def history_item_to_messages(item: dict[str, Any]) -> list[dict[str, Any]]:
    messages = [
        {"role": message["role"], "content": message["message"]}
        for message in item.get("messages", [])
    ]
    assistant_prompt = item.get("assistant_prompt")
    if assistant_prompt:
        messages.append({"role": "assistant", "content": assistant_prompt})
    return messages


def push_history_to_chat(item: dict[str, Any]) -> None:
    st.session_state.messages = history_item_to_messages(item)


def format_session_label(session: dict[str, Any]) -> str:
    title = session.get("title") or "New chat"
    created_at = session.get("created_at", "")
    return f"{title} | {created_at}"


def messages_from_history(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not items:
        return []
    lates_item = items[-1]
    return history_item_to_messages(lates_item)


def history_to_dataframe(items: list[dict[str, Any]]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(
            columns=[
                "id",
                "session_id",
                "user_id",
                "created_at",
                "user_prompt",
                "assistant_prompt",
                "temperature",
                "max_tokens",
                "streamed",
            ]
        )

    frame = pd.DataFrame(items)
    frame["created_at"] = pd.to_datetime(frame["created_at"])
    frame["prompt_length"] = frame["user_prompt"].str.len()
    frame["response_length"] = frame["assistant_prompt"].str.len()
    return frame
