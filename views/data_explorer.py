import altair as alt
import pandas as pd
import streamlit as st

from components.layout import page_header
from services.data_service import (
    dataframe_to_csv,
    load_default_data,
    load_uploaded_csv,
)


def _get_data() -> tuple[pd.DataFrame, str]:
    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Leave this empty to use the bundled Iris dataset.",
    )
    if uploaded_file is None:
        return load_default_data(), "iris-filtered.csv"

    return load_uploaded_csv(uploaded_file.getvalue()), uploaded_file.name


def _filter_data(data: pd.DataFrame) -> pd.DataFrame:
    filtered = data.copy()
    categorical_columns = filtered.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()
    numeric_columns = filtered.select_dtypes("number").columns.tolist()

    with st.expander("Filters", expanded=True):
        left, right = st.columns(2)

        if categorical_columns:
            category_column = left.selectbox(
                "Category column",
                categorical_columns,
            )
            category_options = filtered[category_column].dropna().unique().tolist()
            selected_categories = left.multiselect(
                "Values",
                category_options,
                default=category_options,
            )
            filtered = filtered[filtered[category_column].isin(selected_categories)]
        else:
            left.info("No categorical columns found.")

        if numeric_columns:
            numeric_column = right.selectbox("Numeric column", numeric_columns)
            minimum = float(data[numeric_column].min())
            maximum = float(data[numeric_column].max())
            if minimum < maximum:
                selected_range = right.slider(
                    "Range",
                    min_value=minimum,
                    max_value=maximum,
                    value=(minimum, maximum),
                )
                filtered = filtered[
                    filtered[numeric_column].between(*selected_range)
                ]
            else:
                right.info("The selected column has a single value.")
        else:
            right.info("No numeric columns found.")

    return filtered


def _render_chart(data: pd.DataFrame) -> None:
    numeric_columns = data.select_dtypes("number").columns.tolist()
    categorical_columns = data.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if len(numeric_columns) < 2:
        st.info("At least two numeric columns are required for a scatter chart.")
        return

    controls = st.columns(3)
    x_column = controls[0].selectbox("X axis", numeric_columns, index=0)
    y_column = controls[1].selectbox(
        "Y axis",
        numeric_columns,
        index=min(1, len(numeric_columns) - 1),
    )
    color_column = controls[2].selectbox(
        "Color",
        ["None", *categorical_columns],
    )

    encoding = {
        "x": alt.X(f"{x_column}:Q", title=x_column),
        "y": alt.Y(f"{y_column}:Q", title=y_column),
        "tooltip": data.columns.tolist(),
    }
    if color_column != "None":
        encoding["color"] = alt.Color(f"{color_column}:N", title=color_column)

    chart = alt.Chart(data).mark_circle(size=75, opacity=0.7).encode(**encoding)
    st.altair_chart(chart.interactive(), width="stretch")


def render() -> None:
    page_header(
        "DATA TOOLS",
        "Explore a CSV without writing analysis code",
        "Upload, filter, edit, visualize, and export tabular data.",
    )

    try:
        data, filename = _get_data()
    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")
        return

    filtered = _filter_data(data)
    st.caption(f"Showing {len(filtered):,} of {len(data):,} rows")

    table_tab, chart_tab, stats_tab = st.tabs(
        ["Table", "Chart", "Statistics"]
    )

    with table_tab:
        edited_data = st.data_editor(
            filtered,
            width="stretch",
            hide_index=True,
            num_rows="dynamic",
        )
        st.download_button(
            "Download visible data",
            data=dataframe_to_csv(edited_data),
            file_name=filename,
            mime="text/csv",
            icon=":material/download:",
        )

    with chart_tab:
        _render_chart(filtered)

    with stats_tab:
        if filtered.empty:
            st.info("No rows match the current filters.")
        else:
            st.dataframe(
                filtered.describe(include="all").transpose(),
                width="stretch",
            )
