import streamlit as st

from components.layout import apply_global_styles, render_sidebar
from views import chat, dashboard, data_explorer, playground


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
    ],
    "Examples": [
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
