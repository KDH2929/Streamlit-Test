from datetime import datetime

import streamlit as st

from components.layout import page_header


@st.fragment
def _fragment_counter() -> None:
    if "fragment_clicks" not in st.session_state:
        st.session_state.fragment_clicks = 0

    st.caption("This section reruns independently with `@st.fragment`.")
    if st.button("Fragment +1", icon=":material/add:", key="fragment_add"):
        st.session_state.fragment_clicks += 1
    st.metric("Fragment clicks", st.session_state.fragment_clicks, border=True)


def _render_column_builder() -> None:
    controls = st.columns(3)
    ratio = controls[0].selectbox(
        "Column ratio",
        ["1 : 1", "1 : 2", "1 : 2 : 1", "2 : 1 : 1"],
    )
    alignment = controls[1].selectbox(
        "Vertical alignment",
        ["top", "center", "bottom"],
    )
    show_border = controls[2].toggle("Show borders", value=True)

    ratio_map = {
        "1 : 1": [1, 1],
        "1 : 2": [1, 2],
        "1 : 2 : 1": [1, 2, 1],
        "2 : 1 : 1": [2, 1, 1],
    }
    columns = st.columns(
        ratio_map[ratio],
        gap="medium",
        vertical_alignment=alignment,
        border=show_border,
    )
    for index, column in enumerate(columns, start=1):
        with column:
            st.subheader(f"Column {index}")
            st.write("A responsive content block.")
            for _ in range(index - 1):
                st.write("Extra line for alignment testing.")


def _render_containers() -> None:
    st.subheader("Horizontal container")
    with st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="center",
        gap="medium",
    ):
        st.button("Primary action", type="primary", key="horizontal_primary")
        st.button("Secondary action", key="horizontal_secondary")
        st.link_button(
            "Streamlit docs",
            "https://docs.streamlit.io/develop/api-reference",
            icon=":material/open_in_new:",
        )

    st.space("medium")

    left, right = st.columns(2)
    with left:
        with st.container(border=True, height=220):
            st.subheader("Fixed-height container")
            st.write("This container scrolls when its content becomes taller.")
            for number in range(1, 7):
                st.write(f"Scrollable row {number}")

    with right:
        placeholder = st.empty()
        placeholder.info("`st.empty` creates a replaceable placeholder.")
        if st.button("Replace placeholder", key="replace_placeholder"):
            placeholder.success(f"Replaced at {datetime.now():%H:%M:%S}")


def _render_overlays() -> None:
    left, right = st.columns(2)
    with left:
        with st.popover(
            "Open settings",
            icon=":material/settings:",
            width="stretch",
        ):
            st.toggle("Compact mode", key="popover_compact")
            st.color_picker("Accent color", "#5B6CFF")
            st.select_slider(
                "Density",
                ["Comfortable", "Normal", "Compact"],
                value="Normal",
            )

    with right:
        tags = st.pills(
            "Feature tags",
            ["Layout", "Charts", "State", "Cache", "Chat"],
            selection_mode="multi",
            default=["Layout", "Charts"],
        )
        st.write("Selected:", ", ".join(tags) if tags else "None")

    rating = st.feedback("stars", key="layout_rating")
    if rating is not None:
        st.success(f"You selected {rating + 1} star(s).")


def render() -> None:
    page_header(
        "LAYOUT LAB",
        "Build and test responsive Streamlit layouts",
        "Experiment with column ratios, container alignment, overlays, "
        "placeholders, fragments, and a bottom-pinned action area.",
    )

    columns_tab, containers_tab, flow_tab = st.tabs(
        ["Columns", "Containers", "Flow and overlays"]
    )
    with columns_tab:
        _render_column_builder()
    with containers_tab:
        _render_containers()
    with flow_tab:
        _render_overlays()
        st.divider()
        _fragment_counter()

        if st.button("Run status demo", icon=":material/play_arrow:"):
            with st.status("Running test steps...", expanded=True) as status:
                st.write("Loading sample data")
                st.write("Rendering components")
                st.write("Checking state")
                status.update(
                    label="All test steps completed",
                    state="complete",
                )

    with st.bottom:
        with st.container(
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
        ):
            st.caption("Bottom-pinned container")
            st.button("Save test state", icon=":material/save:", key="bottom_save")
