import streamlit as st
from promptguard import promptguard

st.set_page_config(
    page_title="PromptGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.html("""
<style>
    html,
    body,
    #root {
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
    }

    [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        height: 100vh !important;
        overflow: hidden !important;
    }

    [data-testid="stMainBlockContainer"] {
        height: 100vh !important;
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    footer {
        display: none !important;
    }
</style>
""")

promptguard(
    "PromptGuard",
    key="promptguard",
)