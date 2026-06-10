import altair as alt
import streamlit as st

from components.layout import HERO_IMAGE, feature_card, page_header
from services.data_service import load_default_data
from services.openai_service import DEFAULT_MODEL, get_api_key


def render() -> None:
    page_header(
        "STREAMLIT STUDIO",
        "One app, several useful tools",
        "Explore data, test an AI assistant, and learn Streamlit components "
        "inside a small project that is easy to extend.",
    )

    hero, summary = st.columns([1.7, 1], gap="large")
    with hero:
        if HERO_IMAGE.exists():
            st.image(
                str(HERO_IMAGE),
                caption="A calm starting point for the workspace",
                width="stretch",
            )
    with summary:
        st.subheader("Project status")
        st.success("Application is ready", icon=":material/check_circle:")
        st.write(f"**AI model:** `{DEFAULT_MODEL}`")
        st.write(
            "**API key:** "
            + ("Configured" if get_api_key() else "Not configured")
        )
        st.write("**Dataset:** Iris sample")

    data = load_default_data()
    numeric_columns = data.select_dtypes("number").columns

    st.subheader("Dataset at a glance")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Rows", f"{len(data):,}")
    metric_columns[1].metric("Columns", len(data.columns))
    metric_columns[2].metric("Species", data["Species"].nunique())
    metric_columns[3].metric(
        "Avg. petal length",
        f"{data['PetalLengthCm'].mean():.2f} cm",
    )

    chart = (
        alt.Chart(data)
        .mark_circle(size=80, opacity=0.75)
        .encode(
            x=alt.X("SepalLengthCm:Q", title="Sepal length (cm)"),
            y=alt.Y("PetalLengthCm:Q", title="Petal length (cm)"),
            color=alt.Color("Species:N", title="Species"),
            tooltip=["Species", *numeric_columns.tolist()],
        )
        .interactive()
    )
    st.altair_chart(chart, width="stretch")

    st.subheader("What is included")
    cards = st.columns(3, gap="medium")
    with cards[0]:
        feature_card(
            "Interactive data",
            "Upload CSV files, filter rows, inspect statistics, edit cells, "
            "draw charts, and download results.",
        )
    with cards[1]:
        feature_card(
            "Persistent AI chat",
            "Keep messages across reruns with Session State and call the "
            "OpenAI Responses API.",
        )
    with cards[2]:
        feature_card(
            "Component examples",
            "Try forms, tabs, dialogs, inputs, progress indicators, and "
            "responsive column layouts.",
        )
