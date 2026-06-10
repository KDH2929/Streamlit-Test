from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
HERO_IMAGE = ROOT_DIR / "sunrise.jpg"


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1180px;
            padding-top: 4.5rem;
            padding-bottom: 3rem;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-top: 5rem;
            }
        }
        [data-testid="stMetric"] {
            background: color-mix(in srgb, var(--primary-color) 8%, transparent);
            border: 1px solid color-mix(in srgb, var(--primary-color) 20%, transparent);
            border-radius: 1rem;
            padding: 1rem;
        }
        .app-kicker {
            color: var(--primary-color);
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .app-subtitle {
            color: color-mix(in srgb, currentColor 65%, transparent);
            font-size: 1.05rem;
            margin-top: -0.5rem;
            max-width: 720px;
        }
        .feature-card {
            border: 1px solid color-mix(in srgb, currentColor 14%, transparent);
            border-radius: 1rem;
            min-height: 150px;
            padding: 1.1rem;
        }
        .feature-card h3 {
            font-size: 1rem;
            margin: 0 0 0.45rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        if HERO_IMAGE.exists():
            st.logo(
                str(HERO_IMAGE),
                size="large",
                icon_image=":material/space_dashboard:",
            )
        st.caption("A compact data and AI workspace")

        with st.expander("About this app"):
            st.write(
                "Built with native Streamlit navigation, session state, "
                "cached data, interactive charts, file tools, and AI chat."
            )

        st.page_link(
            "https://docs.streamlit.io/develop/api-reference",
            label="Streamlit API reference",
            icon=":material/open_in_new:",
        )


def page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(f'<div class="app-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(
        f'<p class="app-subtitle">{description}</p>',
        unsafe_allow_html=True,
    )


def feature_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
