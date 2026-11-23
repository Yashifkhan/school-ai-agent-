
from app.agent.state import AgentState
from app.tools.llm_knowledge import answer_general_question
from app.tools.web_search import search_web


def llm_knowledge_node(state: AgentState):

    # 1. Get original user query
    query = state["query"]

    # 2. Generate general knowledge answer
    answer = answer_general_question(query)

    # 3. Return result to LangGraph state
    return {
        "source_results": [
            {
                "source": "llm_knowledge",
                "status": "completed",
                "content": answer
            }
        ]
    }

def vector_db_node(state: AgentState):

    return {
        "source_results": [
            {
                "source": "vector_db",
                "status": "route_reached"
            }
        ]
    }



async def web_search_node(state: AgentState):

    # 1. Get user query
    query = state["query"]

    # 2. Call actual Tavily search function
    response = await search_web(
        query=query,
        max_results=5,
        search_depth="fast",
        topic="general",
    )

    # 3. Return structured results to AgentState
    return {
        "source_results": [
            {
                "source": "web_search",
                "status": "completed",
                "content": response.model_dump(),
            }
        ]
    }


def school_db_node(state: AgentState):

    return {
        "source_results": [
            {
                "source": "school_db",
                "status": "route_reached"
            }
        ]
    }


def clarification_node(state: AgentState):

    classification = state.get("classification")

    question = (
        classification.clarification_question
        if classification
        else None
    )

    return {
        "source_results": [
            {
                "source": "clarification",
                "status": "required",
                "question": question or "Please provide more information."
            }
        ]
    }
