from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ai-text: #163b40;
            --ai-muted: #4d676c;
            --ai-surface: rgba(255, 255, 255, 0.88);
            --ai-border: rgba(22, 59, 64, 0.14);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, #f7f4ed 0%, #eef4f1 42%, #ffffff 100%);
            color: var(--ai-text);
        }
        .stApp p,
        .stApp label,
        .stApp li,
        .stApp span,
        .stApp small,
        .stApp .stCaption,
        .stApp [data-testid="stMarkdownContainer"],
        .stApp [data-testid="stMarkdownContainer"] *,
        .stApp [data-testid="stSidebarNav"] *,
        .stApp [data-baseweb="tab-list"] *,
        .stApp [data-testid="stMetricLabel"] *,
        .stApp [data-testid="stExpander"] * {
            color: var(--ai-text);
        }
        h1, h2, h3 {
            color: var(--ai-text);
            letter-spacing: -0.02em;
        }
        .stApp [data-baseweb="input"] input,
        .stApp [data-baseweb="base-input"] input,
        .stApp textarea,
        .stApp [data-baseweb="select"] > div,
        .stApp [data-baseweb="base-input"] > div {
            color: var(--ai-text);
            background: rgba(255, 255, 255, 0.92);
        }
        .stApp [data-testid="stSidebarNav"] {
            background: transparent;
        }
        .stButton > button *,
        .stDownloadButton > button * {
            color: #ffffff !important;
        }
        .stButton > button, .stDownloadButton > button {
            background: #163b40;
            color: #ffffff;
            border: 1px solid #163b40;
            border-radius: 999px;
            padding: 0.45rem 1rem;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #28555c;
            border-color: #28555c;
            color: #ffffff;
        }
        .stApp [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.52);
            border-radius: 999px;
        }
        .stApp [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(22, 59, 64, 0.12);
        }
        div[data-testid="stMetricValue"] {
            color: #163b40;
        }
        div[data-testid="stChatMessage"] {
            border: 1px solid var(--ai-border);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.72);
        }
        section[data-testid="stSidebar"] {
            background: var(--ai-surface);
            backdrop-filter: blur(10px);
        }
        .stApp [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.72);
            border-radius: 16px;
        }
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
