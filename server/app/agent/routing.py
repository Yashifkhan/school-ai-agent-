
import logging

from app.agent.state import AgentState

logger = logging.getLogger(__name__)


AVAILABLE_SOURCES = {
    "llm_knowledge",
    "vector_db",
    "web_search",
    "school_db",
}


def route_after_classification(
    state: AgentState
) -> list[str]:

    classification = state.get("classification")


    # 1. Validate classification
    if classification is None:

        raise ValueError("Classification is missing.")

    # 2. Check whether clarification is required
    if classification.needs_clarification:
        return ["clarification"]

    # 3. Get selected sources
    sources = list(dict.fromkeys(classification.sources))

    # 4. Validate selected sources
    if not sources:
        logger.warning(
            "Classifier returned no sources without requesting clarification; "
            "routing to clarification."
        )
        return ["clarification"]

    invalid_sources = set(sources) - AVAILABLE_SOURCES

    if invalid_sources:
        raise ValueError(
            f"Invalid sources: {invalid_sources}"
        )

    # 5. Return selected nodes
    return sources