import logging
import time

from app.services.ai_models import get_chat_model

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are the general knowledge assistant for a School SaaS platform.

Your responsibility is to answer general knowledge questions.

Instructions:

1. Give clear and accurate explanations.
2. Use simple language that users can understand.
3. Explain concepts with practical examples when useful.
4. Structure longer answers with headings and bullet points.
5. Never invent school-specific records or information.
6. Never claim that you accessed the school's database.
7. Do not pretend to know the latest information.
8. If a question requires live external information,
   it should be handled by the web search source.
9. If a question requires internal school documentation,
   it should be handled by the vector database source.

Answer the user's question directly.
"""


# Reusable general knowledge function
def answer_general_question(
    query: str,
    provider: str = "gemini",
    model: str | None = None,
) -> str:

    if not query or not query.strip():
        raise ValueError("User query cannot be empty.")

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", query)
    ]

    llm = get_chat_model(provider, model)
    started_at = time.perf_counter()
    try:
        response = llm.invoke(messages)
    finally:
        logger.info(
            "General-knowledge generation call took %.2fs",
            time.perf_counter() - started_at,
        )

    # Extract generated text
    content = response.content

    if isinstance(content, str):
        answer = content.strip()

    elif isinstance(content, list):
        answer = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ).strip()

    else:
        answer = ""

    if not answer:
        raise RuntimeError("The selected model returned an empty answer.")

    return answer