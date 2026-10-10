import streamlit as st


out = st.components.v2.component(
    "promptguard.promptguard",
    js="index-*.js",
    css="index-*.css",
    html='<div class="react-root"></div>',
)


def promptguard(
    name,
    items=None,
    detection_result=None,
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

    component_value = out(
        key=key,

        default={
            "num_clicks": 0,
            "selected_item": None,
        },

        data={
            "name": name,
            "items": items or [],
            "detection_result": detection_result,
        },

        width="stretch",
        height="stretch",

        on_num_clicks_change=lambda: None,
        on_selected_item_change=lambda: None,
        on_item_clicked_change=on_item_clicked,
        on_prompt_submitted_change=on_prompt_submitted,
    )

    return component_value