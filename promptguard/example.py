import json
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
    html, body, #root {
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMainBlockContainer"] {
        height: 100vh !important;
        width: 100% !important;
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    footer {
        display: none !important;
    }
</style>
""")

if "detection_result" not in st.session_state:
    st.session_state.detection_result = None

if "detection_response_id" not in st.session_state:
    st.session_state.detection_response_id = None

if "last_processed_request_id" not in st.session_state:
    st.session_state.last_processed_request_id = None

print("OUTGOING RESULT:", st.session_state.detection_result)
print("OUTGOING RESPONSE ID:", st.session_state.detection_response_id)

component_result = promptguard(
    "PromptGuard",
    key="promptguard",
    detection_result=st.session_state.detection_result,
    detection_response_id=st.session_state.detection_response_id,
    on_prompt_submitted=lambda: None,
)

raw_request = component_result.prompt_submitted

print("COMPONENT REQUEST:", repr(raw_request))

if raw_request:
    try:
        request = json.loads(raw_request)

        request_id = request["request_id"]
        prompt = request["prompt"]

        print("REQUEST ID:", request_id)
        print("PROMPT:", prompt)

        if request_id != st.session_state.last_processed_request_id:
            st.session_state.last_processed_request_id = request_id

            print(f"Python received prompt: {prompt}")

            try:
                prediction = predict_prompt(prompt)
                print(f"ML result: {prediction}")

            except Exception as exc:
                print(f"ML error: {exc}")

                prediction = {
                    "prediction": "ERROR",
                    "target": None,
                    "decision_score": None,
                    "error": str(exc),
                }

            st.session_state.detection_result = prediction
            st.session_state.detection_response_id = request_id


            print("ML PREDICTION:", prediction)
            print(
                "RESPONSE ID:",
                st.session_state.detection_response_id
            )

            st.rerun()

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Invalid prompt request received: {exc}")