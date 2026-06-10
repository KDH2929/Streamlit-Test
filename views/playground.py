from datetime import date

import streamlit as st

from components.layout import HERO_IMAGE, page_header


@st.dialog("Saved profile")
def show_profile_dialog(name: str, role: str) -> None:
    st.write(f"**Name:** {name or 'Anonymous'}")
    st.write(f"**Role:** {role}")
    st.success("The form values were handled successfully.")


def render() -> None:
    page_header(
        "COMPONENT LAB",
        "Try common Streamlit building blocks",
        "A practical collection of inputs, layouts, containers, media, "
        "status elements, and execution patterns.",
    )

    input_tab, layout_tab, status_tab = st.tabs(
        ["Inputs and form", "Layout and media", "Status and flow"]
    )

    with input_tab:
        with st.form("profile_form"):
            left, right = st.columns(2)
            name = left.text_input("Name", placeholder="Your name")
            role = right.selectbox(
                "Role",
                ["Developer", "Data analyst", "Designer", "Student"],
            )
            interests = st.multiselect(
                "Interests",
                ["AI", "Data", "Web", "Automation", "Visualization"],
                default=["AI"],
            )
            experience = st.slider("Experience (years)", 0, 20, 2)
            available_date = st.date_input("Available from", value=date.today())
            introduction = st.text_area(
                "Introduction",
                placeholder="Tell us what you are building.",
            )
            notifications = st.toggle("Receive project notifications", value=True)
            submitted = st.form_submit_button(
                "Save profile",
                icon=":material/save:",
            )

        if submitted:
            st.session_state.profile = {
                "name": name,
                "role": role,
                "interests": interests,
                "experience": experience,
                "available_date": str(available_date),
                "introduction": introduction,
                "notifications": notifications,
            }
            show_profile_dialog(name, role)

        if "profile" in st.session_state:
            with st.expander("Session State preview"):
                st.json(st.session_state.profile)

    with layout_tab:
        left, center, right = st.columns([1, 2, 1], gap="large")
        left.info("Narrow column")
        center.success("Wide center column")
        right.warning("Narrow column")

        with st.container(border=True):
            st.subheader("Media container")
            if HERO_IMAGE.exists():
                st.image(str(HERO_IMAGE), width="stretch")
            st.caption("Images, audio, and video can live inside containers.")

        with st.expander("Why containers matter"):
            st.write(
                "Containers group related elements. Columns place groups "
                "side by side, while tabs and expanders reveal content on demand."
            )

    with status_tab:
        speed = st.segmented_control(
            "Simulation speed",
            ["Fast", "Normal", "Detailed"],
            default="Normal",
        )
        st.write(f"Selected mode: **{speed}**")

        if st.button("Run sample task", icon=":material/play_arrow:"):
            progress = st.progress(0, text="Starting...")
            for value in range(0, 101, 20):
                progress.progress(value, text=f"Progress: {value}%")
            st.toast("Sample task completed", icon=":material/check:")
            st.balloons()

        message_type = st.radio(
            "Status example",
            ["Info", "Success", "Warning", "Error"],
            horizontal=True,
        )
        status_functions = {
            "Info": st.info,
            "Success": st.success,
            "Warning": st.warning,
            "Error": st.error,
        }
        status_functions[message_type](
            f"This is a {message_type.lower()} message."
        )
