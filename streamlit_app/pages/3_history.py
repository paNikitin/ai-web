import streamlit as st
from api import (
    BackendAPIError,
    cached_history,
    cached_session_history,
    cached_sessions,
    clear_api_caches,
)
from utils import (
    format_session_label,
    history_to_dataframe,
    messages_from_history,
    require_auth,
)

require_auth()

st.title("History")
st.caption("История чатов, сохраненных в PostgreSQL.")

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
session_filter_options = [None, *session_by_id]

if st.session_state.active_session_id not in session_by_id:
    first_session = sessions[0]
    st.session_state.active_session_id = first_session["id"]
    st.session_state.active_session_title = first_session.get("title")
    st.session_state.loaded_session_id = None


controls_col, filter_col, refresh_col = st.columns([2, 2, 1])


with filter_col:
    selected_session_id = st.selectbox(
        "Session filter",
        options=session_filter_options,
        format_func=lambda session_id: (
            "All sessions"
            if session_id is None
            else format_session_label(session_by_id[session_id])
        ),
    )

with controls_col:
    limit = st.session_state.history_limit
    st.caption(f"РHistory limit from sider: `{limit}`")

with refresh_col:
    if st.button("Refresh", use_container_width=True):
        clear_api_caches()


try:
    if selected_session_id is None:
        print(f"LIMIT: {limit}")
        history_items = cached_history(
            st.session_state.api_url,
            st.session_state.user_id,
            st.session_state.api_key,
            limit,
        )
    else:
        history_items = cached_session_history(
            base_url=st.session_state.api_url,
            user_id=st.session_state.user_id,
            api_key=st.session_state.api_key,
            session_id=selected_session_id,
        )
except BackendAPIError as exc:
    st.error(str(exc))
    st.stop()

if selected_session_id is not None:
    session_title = session_by_id[selected_session_id]["title"]
    st.caption(f"Showing full history for session: `{session_title}`")


if not history_items:
    st.info("History is empty.")

history_dataframe = history_to_dataframe(history_items)

display_columns = [
    "id",
    "session_id",
    "user_id",
    "created_at",
    "temperature",
    "max_tokens",
    "streamed",
]

display_frame = history_dataframe[display_columns]

st.dataframe(display_frame, use_container_width=True)

csv_data = history_dataframe.to_csv(index=False)

st.download_button(
    label="Download CSV.",
    data=csv_data,
    file_name="chat_history.csv",
)

for item in history_items:
    session = session_by_id.get(item["session_id"])
    session_label = session["title"] if session else f"Session {item['session_id']}"

    label = f"{item['created_at']} . {session_label} . {'stream' if item['streamed'] else 'chat'}"

    with st.expander(label):
        meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
        with meta_col1:
            st.metric("Session", f"{item['session_id']}")
        with meta_col2:
            st.metric("Temperature", f"{item['temperature']:.2f}")
        with meta_col3:
            st.metric("Max tokens", f"{item['max_tokens']}")
        with meta_col4:
            st.metric("Mode", f"{'stream' if item['streamed'] else 'chat'}")

    st.markdown("**Prompt**")
    st.write(item["user_prompt"])
    st.markdown("**Answer**")
    st.write(item["assistant_prompt"])

    if st.button("Open session in chat", key=f"open-session-{item['id']}"):
        session_id = item["session_id"]
        try:
            print(f"selected_session_id: {selected_session_id}")
            session_items = cached_session_history(
                base_url=st.session_state.api_url,
                user_id=st.session_state.user_id,
                api_key=st.session_state.api_key,
                session_id=session_id,
            )
        except BackendAPIError as exc:
            st.error(str(exc))
        else:
            session = session_by_id.get(session_id)

            st.session_state.active_session_id = session_id
            st.session_state.active_session_title = (
                session["title"] if session else f"Session {session_id}"
            )
            st.session_state.loaded_session_id = session_id
            st.session_state.messages = messages_from_history(session_items)
            st.switch_page("pages/2_chat.py")
