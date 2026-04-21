import plotly.express as px
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

st.title("Dashboard")
st.caption("Дэшборд поверх истории текущего пользователя")

sample_size = st.slider("Dashboard sample size", min_value=10, max_value=100, value=50)


@st.fragment(run_every=5)
def render_dashboard() -> None:
    try:
        items = cached_history(
            st.session_state.api_url,
            st.session_state.user_id,
            st.session_state.api_key,
            sample_size,
        )
    except BackendAPIError as exc:
        st.error(str(exc))
        st.stop()

    frame = history_to_dataframe(items)
    if frame.empty:
        st.info("Not enough data for visualization.")
        return None

    frame = frame.sort_values("created_at")

    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    metrics_col1.metric("Chats loaded", len(frame))
    metrics_col2.metric("Streamed", int(frame["streamed"].sum()))
    metrics_col3.metric("AVG Temperature", f"{frame['streamed'].mean():.0f}")
    metrics_col4.metric("AVG Prompt length", f"{frame['prompt_length'].mean():.0f}")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        temperature_chart = px.histogram(
            frame,
            x="temperature",
            nbins=10,
            title="Temperature distribution",
            color_discrete_sequence=["#a83232"],
        )
        st.plotly_chart(temperature_chart, use_container_width=True)


render_dashboard()
