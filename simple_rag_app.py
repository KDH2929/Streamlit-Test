import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

st.set_page_config(
    page_title="RAG 문서 질의응답",
    page_icon="📄",
    layout="wide",
)

st.title("📄 RAG 기반 문서 질의응답 시스템")

uploaded_file = st.file_uploader(
    "PDF 업로드",
    type=["pdf"],
)

if uploaded_file:
    pdf_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    retriever = vectordb.as_retriever(
        search_kwargs={"k": 3},
    )

    st.success(f"문서 로드 완료 ({len(chunks)}개 청크)")

    question = st.text_input(
        "질문을 입력하세요",
    )

    if question:
        docs = retriever.invoke(question)
        context = "\n\n".join(
            doc.page_content for doc in docs
        )

        prompt = f"""
당신은 문서 기반 QA 시스템입니다.
다음 문서를 참고하여 답변하세요.

문서:
{context}

질문:
{question}

답변:
"""

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )

        response = llm.invoke(prompt)

        st.subheader("답변")
        st.write(response.content)

        with st.expander("검색된 문서 보기"):
            for index, doc in enumerate(docs, start=1):
                st.markdown(f"### Chunk {index}")
                st.write(doc.page_content)
