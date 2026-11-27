
import os
from functools import lru_cache

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "school-manual"
)


@lru_cache(maxsize=1)
def _get_index():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not api_key:
        raise ValueError("PINECONE_API_KEY is missing from .env")

    if not index_name:
        raise ValueError("PINECONE_INDEX_NAME is missing from .env")

    return Pinecone(api_key=api_key).Index(index_name)


def search_school_documents(
    query: str,
    top_k: int = 4
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    response = _get_index().search(
        namespace=PINECONE_NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {
                "text": query.strip()
            }
        }
    )

    results = []

    for hit in response.result.hits:

        # Extract fields from dictionary-like hit records.
        fields = hit.get("fields", {}) or {}

        result = {
            "id": str(hit.get("_id", "")),
            "content": str(fields.get("text", "")),
            "source_document": str(
                fields.get("source", "Unknown document")
            ),
            "page": fields.get(
                "page_label",
                fields.get("page", "")
            ),
            "score": hit.get("_score")
        }

        results.append(result)

    return results
