
import os

from typing import Literal

from dotenv import load_dotenv
from tavily import AsyncTavilyClient

from app.schemas.search import (
    WebSearchResult,
    WebSearchResponse
)


load_dotenv()


SearchDepth = Literal[
    "ultra-fast",
    "fast",
    "basic",
    "advanced"
]

SearchTopic = Literal[
    "general",
    "news",
    "finance"
]


async def search_web(
    query: str,
    max_results: int = 5,
    search_depth: SearchDepth = "fast",
    topic: SearchTopic = "general",
) -> WebSearchResponse:

    # 1. Validate query
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if len(query) > 400:
        raise ValueError(
            "Search query must be 400 characters or fewer."
        )

    if not 1 <= max_results <= 10:
        raise ValueError(
            "max_results must be between 1 and 10."
        )

    # 2. Get API key
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing from .env"
        )

    # 3. Initialize async Tavily client
    try:

        async with AsyncTavilyClient(
            api_key=api_key
        ) as client:

            # 4. Perform web search
            raw_response = await client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                topic=topic,

                # Gemini will generate the final answer later
                include_answer=False,

                # Only retrieve relevant text snippets
                include_raw_content=False,
            )

        # 5. Extract search results
        results = []

        for item in raw_response.get("results", []):

            results.append(
                WebSearchResult(
                    title=item.get("title", "Untitled"),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score"),
                )
            )

        # 6. Return validated response
        return WebSearchResponse(
            query=query,
            results=results,
            response_time=raw_response.get("response_time"),
            request_id=raw_response.get("request_id"),
        )

    except Exception as error:

        raise RuntimeError(
            f"Tavily web search failed: {error}"
        ) from error
