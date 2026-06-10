import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_MODEL = "gpt-5-nano"


def get_api_key() -> str | None:
    load_dotenv()

    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except FileNotFoundError:
        secret_key = None

    return secret_key or os.getenv("OPENAI_API_KEY")


def create_response(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
) -> str:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(model=model, input=messages)
    return response.output_text
