
import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "school-manual"
)

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing.")

if not PINECONE_INDEX_NAME:
    raise ValueError("PINECONE_INDEX_NAME is missing.")


# Pinecone connection
pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX_NAME)


# Vector search

def search_school_documents(
    query: str,
    top_k: int = 4
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    response = index.search(
        namespace=PINECONE_NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {
                "text": query.strip()
            }
        }
    )

    print("\n========== RAW PINECONE RESPONSE ==========")
    print(response)

    results = []

    for hit in response.result.hits:

        print("\n========== RAW HIT ==========")
        print(hit)

        fields = hit.fields or {}

        result = {
            "id": str(hit.id),
            "content": str(fields.get("text", "")),
            "source_document": str(
                fields.get("source", "Unknown document")
            ),
            "page": fields.get("page", ""),
            "score": hit.score
        }

        results.append(result)

    return results
