import streamlit as st

from components.layout import apply_global_styles, render_sidebar
from views import (
    chat,
    dashboard,
    data_explorer,
    layout_lab,
    playground,
    rag_lab,
    visualization_lab,
)


st.set_page_config(
    page_title="Streamlit Studio",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
render_sidebar()

pages = {
    "Workspace": [
        st.Page(
            dashboard.render,
            title="Dashboard",
            icon=":material/dashboard:",
            url_path="dashboard",
            default=True,
        ),
        st.Page(
            data_explorer.render,
            title="Data Explorer",
            icon=":material/monitoring:",
            url_path="data",
        ),
        st.Page(
            chat.render,
            title="AI Chat",
            icon=":material/chat:",
            url_path="chat",
        ),
        st.Page(
            rag_lab.render,
            title="RAG Lab",
            icon=":material/manage_search:",
            url_path="rag",
        ),
    ],
    "Examples": [
        st.Page(
            visualization_lab.render,
            title="Visualization Lab",
            icon=":material/insert_chart:",
            url_path="visualization",
        ),
        st.Page(
            layout_lab.render,
            title="Layout Lab",
            icon=":material/view_quilt:",
            url_path="layout",
        ),
        st.Page(
            playground.render,
            title="UI Playground",
            icon=":material/widgets:",
            url_path="playground",
        ),
    ],
}

navigation = st.navigation(pages, position="sidebar", expanded=True)
navigation.run()
