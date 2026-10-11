import streamlit as st

from promptguard import promptguard
from ml.src.predict import predict_prompt

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
        width: 100% !important;
        overflow: hidden !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        height: 100vh !important;
        width: 100% !important;
        overflow: hidden !important;
    }

    [data-testid="stMainBlockContainer"] {
        height: 100vh !important;
        width: 100% !important;
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

if "detection_result" not in st.session_state:
    st.session_state.detection_result = None

result = promptguard(
    "PromptGuard",
    key="promptguard",
    detection_result=st.session_state.detection_result,
    on_prompt_submitted=lambda: None,
)

prompt = result.prompt_submitted

if prompt:
    print(f"Python received prompt: {prompt}")

    try:
        prediction = predict_prompt(prompt)

        print(f"ML result: {prediction}")

        st.session_state.detection_result = prediction

        st.rerun()

    except Exception as exc:
        print(f"ML error: {exc}")

        st.session_state.detection_result = {
            "prediction": "ERROR",
            "target": None,
            "decision_score": None,
            "error": str(exc),
        }

        st.rerun()