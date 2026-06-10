import pandas as pd
import streamlit as st

from components.layout import page_header
from services.openai_service import get_api_key, get_secret
from services.rag_service import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    RERANK_MODEL,
    answer_with_context,
    build_vector_store,
    load_documents,
    rerank_candidates,
    retrieve_candidates,
    split_documents,
)


def _initialize_state() -> None:
    defaults = {
        "rag_chunks": [],
        "rag_vector_store": None,
        "rag_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _chunk_table() -> pd.DataFrame:
    rows = []
    for chunk in st.session_state.rag_chunks:
        rows.append(
            {
                "chunk_id": chunk.metadata.get("chunk_id"),
                "source": chunk.metadata.get("source"),
                "page": chunk.metadata.get("page", "-"),
                "start_index": chunk.metadata.get("start_index", "-"),
                "characters": len(chunk.page_content),
                "preview": chunk.page_content[:160].replace("\n", " "),
            }
        )
    return pd.DataFrame(rows)


def _ranking_table(documents: list, score_key: str) -> pd.DataFrame:
    rows = []
    for rank, document in enumerate(documents, start=1):
        row = {
            "rank": rank,
            "chunk_id": document.metadata.get("chunk_id"),
            "source": document.metadata.get("source"),
            "page": document.metadata.get("page", "-"),
            "score": document.metadata.get(score_key),
            "preview": document.page_content[:140].replace("\n", " "),
        }
        if score_key == "retrieval_score":
            row["distance"] = document.metadata.get("retrieval_distance")
        rows.append(row)
    return pd.DataFrame(rows)


def _render_chunk_inspector() -> None:
    chunks = st.session_state.rag_chunks
    if not chunks:
        st.info("문서를 인덱싱하면 분할된 청크가 여기에 표시됩니다.")
        return

    st.dataframe(_chunk_table(), width="stretch", hide_index=True)
    selected_id = st.selectbox(
        "전체 내용을 확인할 청크",
        options=[chunk.metadata["chunk_id"] for chunk in chunks],
        format_func=lambda value: f"Chunk {value}",
    )
    selected = chunks[selected_id]

    metadata, content = st.columns([1, 3])
    with metadata:
        st.json(selected.metadata)
    with content:
        st.text_area(
            "Chunk content",
            value=selected.page_content,
            height=300,
            disabled=True,
        )


def _render_result() -> None:
    result = st.session_state.rag_result
    if not result:
        return

    st.subheader("RAG 답변")
    st.markdown(result["answer"])

    retrieval_tab, rerank_tab, context_tab = st.tabs(
        ["Vector retrieval", "Cohere rerank", "LLM context"]
    )
    with retrieval_tab:
        st.dataframe(
            _ranking_table(result["candidates"], "retrieval_score"),
            width="stretch",
            hide_index=True,
        )
    with rerank_tab:
        if result["used_reranker"]:
            st.dataframe(
                _ranking_table(result["final_documents"], "relevance_score"),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("Cohere API 키가 없어 벡터 검색 순위를 그대로 사용했습니다.")
    with context_tab:
        st.code(result["context"], language="text", wrap_lines=True)


def render() -> None:
    page_header(
        "RAG PIPELINE",
        "Inspect chunking, retrieval, reranking, and LLM context",
        "Upload documents, create a Chroma vector index, compare retrieval "
        "with Cohere reranking, and inspect exactly what reaches the LLM.",
    )
    _initialize_state()

    openai_key = get_api_key()
    cohere_key = get_secret("COHERE_API_KEY")

    status_columns = st.columns(4)
    status_columns[0].metric("Chunk size", CHUNK_SIZE, border=True)
    status_columns[1].metric("Overlap", CHUNK_OVERLAP, border=True)
    status_columns[2].metric("Embedding", EMBEDDING_MODEL, border=True)
    status_columns[3].metric("Reranker", RERANK_MODEL, border=True)

    if not openai_key:
        st.error("`OPENAI_API_KEY`가 필요합니다.", icon=":material/key:")
    if not cohere_key:
        st.warning(
            "`COHERE_API_KEY`가 없어서 reranker는 선택적으로 건너뜁니다.",
            icon=":material/key:",
        )

    input_tab, chunks_tab, query_tab = st.tabs(
        ["1. Documents", "2. Chunk inspector", "3. Retrieve and answer"]
    )

    with input_tab:
        uploaded_files = st.file_uploader(
            "PDF, TXT, Markdown 파일",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )
        pasted_text = st.text_area(
            "또는 텍스트 직접 입력",
            height=180,
            placeholder="RAG로 검색할 문서를 붙여 넣으세요.",
        )

        if st.button(
            "문서 청킹 및 인덱싱",
            type="primary",
            icon=":material/database:",
            disabled=not openai_key,
        ):
            if not uploaded_files and not pasted_text.strip():
                st.warning("파일을 업로드하거나 텍스트를 입력하세요.")
            else:
                try:
                    with st.status("RAG 인덱스를 생성하고 있습니다...") as status:
                        status.write("문서 텍스트 추출")
                        files = [
                            (uploaded.name, uploaded.getvalue())
                            for uploaded in uploaded_files
                        ]
                        documents = load_documents(files, pasted_text)

                        status.write(
                            f"{CHUNK_SIZE}/{CHUNK_OVERLAP} 기준으로 청킹"
                        )
                        chunks = split_documents(documents)

                        status.write("OpenAI Embedding 및 Chroma 인덱스 생성")
                        vector_store = build_vector_store(chunks, openai_key)

                        st.session_state.rag_chunks = chunks
                        st.session_state.rag_vector_store = vector_store
                        st.session_state.rag_result = None
                        status.update(
                            label=f"{len(chunks)}개 청크 인덱싱 완료",
                            state="complete",
                        )
                except Exception as error:
                    st.error(f"인덱싱 실패: {error}")

    with chunks_tab:
        _render_chunk_inspector()

    with query_tab:
        vector_store = st.session_state.rag_vector_store
        if vector_store is None:
            st.info("먼저 Documents 탭에서 문서를 인덱싱하세요.")
        else:
            query = st.text_input(
                "질문",
                placeholder="업로드한 문서에 관해 질문하세요.",
            )
            controls = st.columns(3)
            candidate_count = controls[0].slider(
                "Retriever candidates",
                5,
                20,
                10,
            )
            final_count = controls[1].slider(
                "Final context chunks",
                min_value=1,
                max_value=min(8, candidate_count),
                value=min(4, candidate_count),
            )
            use_reranker = controls[2].toggle(
                "Use Cohere reranker",
                value=bool(cohere_key),
                disabled=not cohere_key,
            )

            if st.button(
                "검색, Rerank, 답변 생성",
                type="primary",
                icon=":material/search:",
                disabled=not query.strip(),
            ):
                try:
                    with st.status("RAG 파이프라인 실행 중...") as status:
                        status.write("Chroma 유사도 검색")
                        candidates = retrieve_candidates(
                            vector_store,
                            query,
                            candidate_count,
                        )

                        if use_reranker and cohere_key:
                            status.write("Cohere API reranking")
                            final_documents = rerank_candidates(
                                query,
                                candidates,
                                cohere_key,
                                final_count,
                            )
                        else:
                            final_documents = candidates[:final_count]

                        status.write("최종 컨텍스트를 GPT에 전달")
                        answer, context = answer_with_context(
                            query,
                            final_documents,
                        )
                        st.session_state.rag_result = {
                            "answer": answer,
                            "candidates": candidates,
                            "final_documents": final_documents,
                            "context": context,
                            "used_reranker": bool(
                                use_reranker and cohere_key
                            ),
                        }
                        status.update(label="RAG 답변 완료", state="complete")
                except Exception as error:
                    st.error(f"RAG 실행 실패: {error}")

        _render_result()
