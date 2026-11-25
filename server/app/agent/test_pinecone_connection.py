
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from app.tools.vector_search import index, PINECONE_NAMESPACE

load_dotenv()


def split_text_into_chunks(
    text,
    chunk_size=1000,
    chunk_overlap=150
):
    """
    Split text while trying to preserve paragraph boundaries.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        # Handle paragraphs larger than the chunk size.
        if len(paragraph) > chunk_size:

            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            start = 0

            while start < len(paragraph):
                end = start + chunk_size
                chunks.append(paragraph[start:end])

                start += chunk_size - chunk_overlap

            continue

        candidate = (
            current_chunk + "\n" + paragraph
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate

        else:
            chunks.append(current_chunk)

            overlap_text = current_chunk[-chunk_overlap:]

            current_chunk = (
                overlap_text + "\n" + paragraph
            )

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def upload_new_pdf(pdf_path):
    """
    Extract text from the new PDF, create chunks,
    and upload records using Pinecone integrated embedding.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    print("\n========== READING PDF ==========")

    reader = PdfReader(str(pdf_path))

    if reader.is_encrypted:
        raise ValueError(
            "The PDF is encrypted. Provide an unlocked PDF."
        )

    records = []

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text() or ""

        if not page_text.strip():
            print(f"Skipping empty page: {page_number}")
            continue

        page_chunks = split_text_into_chunks(page_text)

        for chunk_number, chunk in enumerate(
            page_chunks,
            start=1
        ):

            record = {
                "_id": str(uuid.uuid4()),

                # This field must match the integrated
                # embedding field configured in Pinecone.
                "text": chunk,

                # Metadata
                "source": pdf_path.name,
                "page": page_number - 1,
                "page_label": str(page_number),
                "chunk_number": chunk_number,
                "document_type": "school_user_manual"
            }

            records.append(record)

    if not records:
        raise ValueError(
            "No extractable text found in the PDF."
        )

    print("\n========== CHUNK INFORMATION ==========")
    print("PDF:", pdf_path.name)
    print("Pages:", len(reader.pages))
    print("Total chunks:", len(records))

    # Preview before uploading.
    for number, record in enumerate(records, start=1):
        print(f"\nChunk {number}")
        print("Page:", record["page_label"])
        print("Characters:", len(record["text"]))
        print("Text:", record["text"][:200])

    print("\n========== UPLOADING TO PINECONE ==========")

    # Integrated embedding generates embeddings on Pinecone.
    response = index.upsert_records(
        namespace=PINECONE_NAMESPACE,
        records=records
    )

    print("\n========== UPLOAD SUBMITTED ==========")
    print("Records submitted:", len(records))
    print(response)

    print(
        "\nPinecone writes are asynchronous. "
        "Verify the records after indexing completes."
    )



from app.tools.vector_search import search_school_documents


TEST_QUERIES = [
    "How do I register a new student?",
    # "How do I collect student fees?",
    "How do I enable transport during student admission?",
    # "How do I create a transport route?",
    # "How do I remove a student from an existing route?",
    # "How do I open a student's 360 profile?"
]


def test_vector_search():

    for query in TEST_QUERIES:

        print("\n" + "=" * 80)
        print("QUERY:", query)
        print("=" * 80)

        try:

            results = search_school_documents(
                query=query,
                top_k=4
            )

            if not results:
                print("No results found.")
                continue

            for i, result in enumerate(results, start=1):

                print(f"\n--- RESULT {i} ---")
                print("ID:", result["id"])
                print("Score:", result["score"])
                print("Source:", result["source_document"])
                print("Page:", result["page"])
                print("Content:")
                print(result["content"])

        except Exception as error:
            print("ERROR:", error)


if __name__ == "__main__":
    test_vector_search()



# if __name__ == "__main__":
#     # upload_new_pdf("documents/student_management_transport_guide.pdf")
#     # First run the deletion function separately.
#     # Upload the new PDF only after verifying deletion.

#     pass
