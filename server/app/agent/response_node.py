
import json
import logging
import time

from app.agent.state import AgentState
from app.services.ai_models import get_chat_model

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an AI assistant for a School Management SaaS platform.

Your task is to answer user questions using the provided source results.

STRICT RULES:

1. Use only the information available in the source results.
2. Never invent or assume information.
3. Never generate fake student or employee records.
4. Never invent attendance, fees, payments, or transport details.
5. If information is missing, clearly say it is unavailable.
6. If a source returns no records, explain that no matching records were found.
7. If a source has an error, clearly communicate that the information
   could not be retrieved. Never present an error as a successful result.
8. Answer the user's actual question.
9. Use simple, professional language.
10. Format financial amounts clearly.
11. Do not expose internal IDs unless explicitly requested.
12. Distinguish between missing data and failed data retrieval.
13. Treat vector IDs and relevance scores as internal metadata. Never
    reproduce raw source JSON or technical retrieval metadata.

Return only the final answer.
"""


def response_node(state: AgentState) -> dict:

    query = state.get("query", "")
    source_results = state.get("source_results", [])

    if not query.strip():
        return {
            "final_answer": "Please provide a valid question."
        }

    if not source_results:
        return {
            "final_answer": (
                "I couldn't find any information to answer your question."
            )
        }

    # Check source errors before generating an answer
    errors = [
        result for result in source_results
        if result.get("status") == "error"
    ]

    if errors:
        return {
            "final_answer": (
                "I couldn't retrieve the required information because "
                "one or more data sources encountered an error."
            )
        }

    if len(source_results) == 1:
        result = source_results[0]
        content = result.get("content")
        if (
            result.get("source") == "llm_knowledge"
            and result.get("status") == "completed"
            and isinstance(content, str)
            and content.strip()
        ):
            return {"final_answer": content.strip()}

    # Prepare source context
    prompt_source_results = [
        {
            key: value
            for key, value in result.items()
            if key not in {"chunk_id", "score"}
        }
        if result.get("source") == "vector_db"
        else result
        for result in source_results
    ]
    source_context = json.dumps(
        prompt_source_results,
        indent=2,
        ensure_ascii=False,
        default=str
    )

    user_prompt = f"""
USER QUESTION:
{query}

SOURCE RESULTS:
{source_context}

Generate an accurate answer using only the supplied source results.
"""

    started_at = time.perf_counter()
    try:
        llm = get_chat_model(
            state.get("provider", "gemini"),
            state.get("model"),
        )
        response = llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("human", user_prompt)
        ])
    finally:
        logger.info(
            "Final response generation call took %.2fs",
            time.perf_counter() - started_at,
        )

    content = response.content

    if isinstance(content, str):
        final_answer = content.strip()

    elif isinstance(content, list):
        final_answer = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict)
            and item.get("type") == "text"
        ).strip()

    else:
        final_answer = ""

    if not final_answer:
        raise ValueError("The selected model returned an empty response.")

    return {
        "final_answer": final_answer
    }
