import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

from components.layout import page_header
from services.data_service import load_default_data


SEOUL_LOCATIONS = pd.DataFrame(
    {
        "name": ["서울역", "광화문", "강남역", "잠실", "홍대입구"],
        "lat": [37.5547, 37.5759, 37.4979, 37.5133, 37.5572],
        "lon": [126.9706, 126.9768, 127.0276, 127.1002, 126.9245],
        "visitors": [80, 55, 100, 70, 90],
    }
)


def _chart_data() -> pd.DataFrame:
    data = load_default_data()
    return (
        data.groupby("Species", as_index=False)
        .agg(
            sepal_length=("SepalLengthCm", "mean"),
            sepal_width=("SepalWidthCm", "mean"),
            petal_length=("PetalLengthCm", "mean"),
            petal_width=("PetalWidthCm", "mean"),
        )
    )


def _render_native_charts(data: pd.DataFrame) -> None:
    chart_type = st.segmented_control(
        "Native chart API",
        ["Line", "Area", "Bar", "Scatter"],
        default="Line",
    )

    if chart_type == "Line":
        st.line_chart(
            data,
            x="Species",
            y=["sepal_length", "petal_length"],
            x_label="Species",
            y_label="Average length (cm)",
        )
    elif chart_type == "Area":
        st.area_chart(
            data,
            x="Species",
            y=["sepal_width", "petal_width"],
            stack=False,
        )
    elif chart_type == "Bar":
        st.bar_chart(
            data,
            x="Species",
            y=["sepal_length", "petal_length"],
            stack=False,
        )
    else:
        iris = load_default_data()
        st.scatter_chart(
            iris,
            x="SepalLengthCm",
            y="PetalLengthCm",
            color="Species",
            size="PetalWidthCm",
        )

    st.caption(
        "Native charts need very little code and are suitable for quick analysis."
    )


def _render_altair_chart() -> None:
    iris = load_default_data()
    chart = (
        alt.Chart(iris)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X("SepalLengthCm:Q", title="Sepal length"),
            y=alt.Y("PetalLengthCm:Q", title="Petal length"),
            color=alt.Color("Species:N", title="Species"),
            size=alt.Size("PetalWidthCm:Q", title="Petal width"),
            tooltip=[
                "Species",
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
        )
        .interactive()
    )
    st.altair_chart(chart, width="stretch")
    st.caption("Altair provides detailed encodings, tooltips, and interactions.")


def _render_maps() -> None:
    simple_tab, deck_tab = st.tabs(["st.map", "st.pydeck_chart"])

    with simple_tab:
        st.map(
            SEOUL_LOCATIONS,
            latitude="lat",
            longitude="lon",
            size="visitors",
            zoom=10,
            height=430,
        )

    with deck_tab:
        layer = pdk.Layer(
            "ColumnLayer",
            data=SEOUL_LOCATIONS,
            get_position=["lon", "lat"],
            get_elevation="visitors * 15",
            elevation_scale=8,
            radius=450,
            get_fill_color=[91, 108, 255, 180],
            pickable=True,
            auto_highlight=True,
        )
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=37.55,
                longitude=126.99,
                zoom=10,
                pitch=45,
            ),
            tooltip={"text": "{name}\n방문자 지수: {visitors}"},
        )
        st.pydeck_chart(deck, height=430)


def render() -> None:
    page_header(
        "CHART GALLERY",
        "Compare Streamlit visualization APIs",
        "Render the same sample data with native charts, Altair, maps, "
        "and deck.gl-based 3D layers.",
    )

    data = _chart_data()
    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Setosa petal",
        "1.46 cm",
        chart_data=[1.2, 1.4, 1.3, 1.5, 1.46],
        chart_type="line",
        border=True,
    )
    metric_columns[1].metric(
        "Versicolor petal",
        "4.26 cm",
        delta="2.80 cm",
        chart_data=[3.8, 4.0, 4.3, 4.1, 4.26],
        chart_type="area",
        border=True,
    )
    metric_columns[2].metric(
        "Virginica petal",
        "5.55 cm",
        delta="1.29 cm",
        chart_data=[4.9, 5.2, 5.4, 5.7, 5.55],
        chart_type="bar",
        border=True,
    )
    metric_columns[3].metric(
        "Samples",
        "150",
        delta="3 species",
        delta_color="off",
        border=True,
    )

    native_tab, altair_tab, map_tab = st.tabs(
        ["Native charts", "Altair", "Maps and 3D"]
    )
    with native_tab:
        _render_native_charts(data)
    with altair_tab:
        _render_altair_chart()
    with map_tab:
        _render_maps()
