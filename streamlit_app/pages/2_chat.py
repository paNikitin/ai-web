import streamlit as st
from api import (
    BackendAPIError,
    cached_session_history,
    cached_sessions,
    clear_api_caches,
    get_api,
)
from sqlalchemy.orm import create_session
from state import set_active_session
from utils import format_session_label, messages_from_history, require_auth

require_auth()


st.title("Chat")
st.caption("Диалог с LLM внутри выбранной сессии.")

api = get_api(st.session_state.api_url)

create_col, refresh_col = st.columns([4, 1])

with create_col:
    with st.form("create_session_form", clear_on_submit=True):
        session_title = st.text_input("New session title", placeholder="New chat")
        create_session = st.form_submit_button("Create session")

if create_session:
    try:
        with st.spinner("Creating chat session.."):
            session = api.create_session(
                user_id=st.session_state.user_id,
                api_key=st.session_state.api_key,
                title=session_title or "New chat",
            )

    except BackendAPIError as exc:
        st.error(str(exc))
    else:
        clear_api_caches()
        set_active_session(session)
        st.rerun()


with refresh_col:
    st.write("")
    if st.button("Refresh", use_container_width=True):
        clear_api_caches()
        st.rerun()

try:
    sessions = cached_sessions(
        st.session_state.api_url, st.session_state.user_id, st.session_state.api_key
    )
except BackendAPIError as exc:
    st.error(str(exc))
    st.stop()


if not sessions:
    st.info("Create chat session first.")
    st.stop()

session_by_id = {session["id"]: session for session in sessions}
session_ids = list(session_by_id)


if st.session_state.active_session_id not in session_by_id:
    first_session = sessions[0]
    st.session_state.active_session_id = first_session["id"]
    st.session_state.active_session_title = first_session.get("title")
    st.session_state.loaded_session_id = None


selected_session_id = st.selectbox(
    "Active session",
    options=session_ids,
    index=session_ids.index(st.session_state.active_session_id),
    format_func=lambda session_id: format_session_label(session_by_id[session_id]),
)

selected_session = session_by_id[selected_session_id]
if selected_session_id != st.session_state.active_session_id:
    st.session_state.active_session_id = selected_session_id
    st.session_state.active_session_title = selected_session.get("title")
    st.session_state.loaded_session_id = None


if st.session_state.loaded_session_id != selected_session_id:
    try:
        session_history = cached_session_history(
            base_url=st.session_state.api_url,
            user_id=st.session_state.user_id,
            api_key=st.session_state.api_key,
            session_id=selected_session_id,
        )
    except BackendAPIError as exc:
        st.error(str(exc))
        st.stop()

    st.session_state.messages = messages_from_history(session_history)
    st.session_state.active_session_title = selected_session.get("title")
    st.session_state.loaded_session_id = selected_session_id
    st.rerun()


st.caption(
    f"Active session: `{st.session_state.active_session_title}`"
    f"(id={st.session_state.active_session_id})"
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "Input your message", disabled=st.session_state.active_session_id is None
)

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            if st.session_state.streaming_enabled:
                placeholder = st.empty()
                full_response = ""
                for chunk in api.stream_chat(
                    api_key=st.session_state.api_key,
                    session_id=st.session_state.active_session_id,
                    messages=st.session_state.messages,
                    temperature=st.session_state.temperature,
                    max_tokens=st.session_state.max_tokens,
                ):
                    full_response += chunk
                    placeholder.markdown(full_response)
            else:
                with st.spinner("LLM is generating.."):
                    response = api.send_chat(
                        api_key=st.session_state.api_key,
                        session_id=st.session_state.active_session_id,
                        messages=st.session_state.messages,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens,
                    )
                full_response = response["response"]
                st.markdown(full_response)
    except BackendAPIError as exc:
        st.error(str(exc))

    else:
        assistant_message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(assistant_message)
        st.session_state.loaded_session_id = st.session_state.active_session_id
        clear_api_caches()
        st.rerun()
