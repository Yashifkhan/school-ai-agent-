
from app.agent.state import AgentState


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
        raise ValueError(
            "Classifier returned no sources."
        )

    invalid_sources = set(sources) - AVAILABLE_SOURCES

    if invalid_sources:
        raise ValueError(
            f"Invalid sources: {invalid_sources}"
        )

    # 5. Return selected nodes
    return sources
