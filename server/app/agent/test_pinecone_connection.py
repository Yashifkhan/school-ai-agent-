
from app.tools.vector_search import search_school_documents


def test_vector_search():

    query = "How do I register a new student in our school software?"

    results = search_school_documents(
        query=query,
        top_k=4
    )

    print("\n========== VECTOR SEARCH RESULTS ==========")

    print("Query:", query)
    print("Total Results:", len(results))

    for index, result in enumerate(results, start=1):

        print(f"\n========== RESULT {index} ==========")

        print("Chunk ID:", result["id"])
        print("Source:", result["source_document"])
        print("Page:", result["page"])
        print("Score:", result["score"])

        print("\nContent:")
        print(result["content"])


if __name__ == "__main__":
    test_vector_search()
