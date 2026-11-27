


import logging
import time

from app.schemas.routing import QueryClassification
from app.agent.state import AgentState
from app.services.ai_models import get_chat_model

logger = logging.getLogger(__name__)


# 3. Classifier prompt
CLASSIFIER_PROMPT = """
You are a query classifier for a School SaaS AI Agent.

Available sources:

1. llm_knowledge: General knowledge and explanations.
2. vector_db: Internal school software documentation.
3. web_search: Latest external information.
4. school_db: Real-time school records.

Select one or multiple sources when necessary. Always select at least one
source unless clarification is genuinely required. Route greetings, thanks,
and general conversational messages to llm_knowledge. Ask for clarification
when required information is missing. Do not answer the user's question.

Return one JSON object with these fields: intent (string), sources (array of
"llm_knowledge", "vector_db", "web_search", or "school_db"),
needs_clarification (boolean), clarification_question (string or null), and
reason (string). Return structured classification only.
"""


# 1. Classifier
def classify_query(
    query: str,
    provider: str = "gemini",
    model: str | None = None,
) -> QueryClassification:

    messages = [
        ("system", CLASSIFIER_PROMPT),
        ("human", f"Classify this user query:\n{query}")
    ]

    llm = get_chat_model(provider, model)
    method = "json_schema" if provider == "gemini" else "json_mode"
    structured_llm = llm.with_structured_output(
        QueryClassification,
        method=method,
    )

    started_at = time.perf_counter()
    try:
        result = structured_llm.invoke(messages)
    finally:
        logger.info(
            "Query classification call took %.2fs",
            time.perf_counter() - started_at,
        )

    return result


# 2. LangGraph classifier node
def classify_query_node(state: AgentState):

    query = state["query"]

    classification = classify_query(
        query,
        state.get("provider", "gemini"),
        state.get("model"),
    )

    return {
        "classification": classification
    }