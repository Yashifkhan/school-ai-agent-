
from app.agent.state import AgentState
from app.tools.llm_knowledge import answer_general_question
from app.tools.web_search import search_web
import asyncio
import logging

from app.agent.state import AgentState
from app.tools.vector_search import search_school_documents


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

async def vector_db_node(state: AgentState):

    query = state["query"]

    try:

        # Run synchronous Pinecone search without
        # blocking the asynchronous LangGraph node.
        results = await asyncio.to_thread(
            search_school_documents,
            query,
            4
        )

        if not results:

            return {
                "source_results": [
                    {
                        "source": "vector_db",
                        "status": "no_results",
                        "query": query,
                        "message": "No relevant documents found."
                    }
                ]
            }

        # Store each retrieved document chunk
        # in the existing AgentState structure.
        formatted_results = []

        for result in results:

            formatted_results.append({
                "source": "vector_db",
                "status": "success",
                "query": query,
                "chunk_id": result["id"],
                "content": result["content"],
                "source_document": result["source_document"],
                "page": result["page"],
                "score": result["score"]
            })

        return {
            "source_results": formatted_results
        }

    except Exception:

        logging.exception("Vector database search failed.")

        return {
            "source_results": [
                {
                    "source": "vector_db",
                    "status": "error",
                    "message": "Vector search failed. Check server logs."
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
