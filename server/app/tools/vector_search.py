
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Default namespace
PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "school-manual"
)

# ==========================================
# 2. VALIDATE ENVIRONMENT VARIABLES
# ==========================================

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing from .env")

if not PINECONE_INDEX_NAME:
    raise ValueError("PINECONE_INDEX_NAME is missing from .env")

# ==========================================
# 3. INITIALIZE PINECONE
# ==========================================

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX_NAME)


# ==========================================
# 4. SEARCH SCHOOL DOCUMENTS
# ==========================================

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
