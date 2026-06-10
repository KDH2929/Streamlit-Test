from io import BytesIO
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_cohere import CohereRerank
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from services.openai_service import create_response


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "text-embedding-3-small"
RERANK_MODEL = "rerank-v4.0-fast"


def _decode_text(file_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("지원되는 문자 인코딩으로 파일을 읽을 수 없습니다.")


def load_documents(
    files: list[tuple[str, bytes]],
    pasted_text: str = "",
) -> list[Document]:
    documents: list[Document] = []

    for filename, file_bytes in files:
        suffix = filename.rsplit(".", maxsplit=1)[-1].lower()

        if suffix == "pdf":
            reader = PdfReader(BytesIO(file_bytes))
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": filename,
                                "page": page_number,
                            },
                        )
                    )
        elif suffix in {"txt", "md"}:
            documents.append(
                Document(
                    page_content=_decode_text(file_bytes),
                    metadata={"source": filename},
                )
            )
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {filename}")

    if pasted_text.strip():
        documents.append(
            Document(
                page_content=pasted_text.strip(),
                metadata={"source": "직접 입력"},
            )
        )

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", "。", "? ", "! ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index
        chunk.metadata["char_count"] = len(chunk.page_content)

    return chunks


def build_vector_store(
    chunks: list[Document],
    openai_api_key: str,
) -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=openai_api_key,
    )
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=f"rag-test-{uuid4().hex}",
    )


def retrieve_candidates(
    vector_store: Chroma,
    query: str,
    candidate_count: int,
) -> list[Document]:
    results = vector_store.similarity_search_with_score(
        query,
        k=candidate_count,
    )
    candidates: list[Document] = []

    for rank, (document, distance) in enumerate(results, start=1):
        document.metadata["retrieval_rank"] = rank
        document.metadata["retrieval_distance"] = float(distance)
        document.metadata["retrieval_score"] = 1 / (1 + max(float(distance), 0))
        candidates.append(document)

    return candidates


def rerank_candidates(
    query: str,
    candidates: list[Document],
    cohere_api_key: str,
    top_n: int,
) -> list[Document]:
    reranker = CohereRerank(
        model=RERANK_MODEL,
        cohere_api_key=cohere_api_key,
        top_n=top_n,
    )
    reranked = reranker.compress_documents(candidates, query)

    for rank, document in enumerate(reranked, start=1):
        document.metadata["rerank_rank"] = rank

    return list(reranked)


def format_context(documents: list[Document]) -> str:
    sections = []
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown")
        page = document.metadata.get("page")
        chunk_id = document.metadata.get("chunk_id", "?")
        location = f"{source}, page {page}" if page else source
        sections.append(
            f"[Context {index} | {location} | chunk {chunk_id}]\n"
            f"{document.page_content}"
        )
    return "\n\n".join(sections)


def answer_with_context(
    query: str,
    documents: list[Document],
) -> tuple[str, str]:
    context = format_context(documents)
    messages = [
        {
            "role": "developer",
            "content": (
                "제공된 컨텍스트만 근거로 한국어로 답하세요. "
                "근거가 부족하면 모른다고 답하세요. "
                "답변의 문장 끝에 관련 컨텍스트 번호를 [Context N] 형태로 표시하세요."
            ),
        },
        {
            "role": "user",
            "content": f"질문:\n{query}\n\n컨텍스트:\n{context}",
        },
    ]
    return create_response(messages), context
