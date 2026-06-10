import streamlit as st

from components.layout import page_header
from services.openai_service import DEFAULT_MODEL, create_response, get_api_key


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "안녕하세요. 이 앱의 AI 도우미입니다. 데이터 분석, Python, "
        "Streamlit에 관해 무엇이든 물어보세요."
    ),
}


def _initialize_chat() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [WELCOME_MESSAGE]


def render() -> None:
    page_header(
        "AI ASSISTANT",
        "A small chat interface with memory",
        f"Messages persist during this browser session. Model: {DEFAULT_MODEL}",
    )
    _initialize_chat()

    settings, action = st.columns([3, 1])
    with settings:
        system_prompt = st.text_input(
            "Assistant instruction",
            value="Answer clearly and concisely. Use Korean unless asked otherwise.",
        )
    with action:
        st.write("")
        st.write("")
        if st.button(
            "Clear chat",
            icon=":material/delete:",
            width="stretch",
        ):
            st.session_state.chat_messages = [WELCOME_MESSAGE]
            st.rerun()

    if not get_api_key():
        st.warning(
            "`OPENAI_API_KEY` is missing. Add it to `.env` or "
            "`.streamlit/secrets.toml` to enable replies.",
            icon=":material/key:",
        )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메시지를 입력하세요"):
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        api_messages = [
            {"role": "developer", "content": system_prompt},
            *st.session_state.chat_messages[1:],
        ]

        with st.chat_message("assistant"):
            try:
                with st.spinner("답변을 생성하고 있습니다..."):
                    answer = create_response(api_messages)
                st.markdown(answer)
            except Exception as error:
                answer = f"요청을 처리하지 못했습니다: {error}"
                st.error(answer)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer}
        )
