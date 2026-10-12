from pathlib import Path
import streamlit as st

BUILD_DIR = Path(__file__).parent / "frontend" / "build"

js_files = list(BUILD_DIR.glob("index-*.js"))
css_files = list(BUILD_DIR.glob("index-*.css"))

if len(js_files) != 1:
    raise FileNotFoundError(
        f"Expected one JavaScript bundle in {BUILD_DIR}, found {len(js_files)}"
    )

if len(css_files) != 1:
    raise FileNotFoundError(
        f"Expected one CSS bundle in {BUILD_DIR}, found {len(css_files)}"
    )

js_code = js_files[0].read_text(encoding="utf-8")
css_code = css_files[0].read_text(encoding="utf-8")

out = st.components.v2.component(
    "promptguard.promptguard",
    js=js_code,
    css=css_code,
    html='<div class="react-root"></div>',
)

def promptguard(
    name,
    items=None,
    detection_result=None,
    detection_response_id=None,
    key=None,
    on_item_clicked=lambda: None,
    on_prompt_submitted=lambda: None,
):
    """
    Create a new instance of the PromptGuard component.

    Parameters
    ----------
    name : str
        Component name.

    items : list[str] | None
        Optional list of items.

    detection_result : dict | None
        Latest result returned by the PromptGuard ML model.

    key : str | None
        Optional unique key for the component.

    on_item_clicked : callable
        Callback for item-click events.

    on_prompt_submitted : callable
        Callback triggered when a prompt is submitted.
    """

    return out(
        key=key,

        default={
            "num_clicks": 0,
            "selected_item": None,
        },

        data={
            "name": name,
            "items": items or [],
            "detection_result": detection_result,
            "detection_response_id": detection_response_id,
        },

        width="stretch",
        height="stretch",

        on_num_clicks_change=lambda: None,
        on_selected_item_change=lambda: None,
        on_item_clicked_change=on_item_clicked,
        on_prompt_submitted_change=on_prompt_submitted,
    )

  