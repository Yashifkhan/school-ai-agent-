
from app.agent.state import AgentState
from app.tools.llm_knowledge import answer_general_question
from app.tools.web_search import search_web
import asyncio
import logging

from app.agent.state import AgentState
from app.tools.vector_search import search_school_documents



from app.tools.school_db import (
    search_students,
    search_employees,
    get_student_attendance,
    get_student_fees,
    get_student_fee_payments,
    get_student_transport_details,
)

from app.tools.school_data import get_collection


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



def find_record_in_query(
    query: str,
    collection_name: str,
    tenant_id: str,
    branch_id: str | None = None
) -> dict | None:
    """
    Identify a student or employee from the user's query.
    """

    records = get_collection(collection_name)

    query_lower = query.lower()

    matches = []

    for record in records:

        if record.get("tenant_id") != tenant_id:
            continue

        if branch_id and record.get("branch_id") != branch_id:
            continue

        full_name = str(record.get("full_name", "")).lower()
        first_name = str(record.get("first_name", "")).lower()
        record_id = str(
            record.get("student_id")
            or record.get("employee_id")
            or ""
        ).lower()

        if (
            (full_name and full_name in query_lower)
            or (first_name and first_name in query_lower)
            or (record_id and record_id in query_lower)
        ):
            matches.append(record)

    if len(matches) == 1:
        return matches[0]

    return None


def school_db_node(state: AgentState):

    query = state["query"]
    tenant_id = state.get("tenant_id")
    branch_id = state.get("branch_id")

    # Tenant context must come from the backend.
    if not tenant_id:
        return {
            "source_results": [{
                "source": "school_db",
                "status": "error",
                "message": "Missing authenticated tenant context."
            }]
        }

    try:

        query_lower = query.lower()

        # Identify requested database operation
        if any(word in query_lower for word in [
            "payment", "payments", "receipt", "transaction"
        ]):
            action = "fee_payments"

        elif any(word in query_lower for word in [
            "attendance", "absent", "present", "late"
        ]):
            action = "attendance"

        elif any(word in query_lower for word in [
            "transport", "bus", "driver", "route"
        ]):
            action = "transport"

        elif any(word in query_lower for word in [
            "fee", "fees", "balance", "dues", "outstanding"
        ]):
            action = "fees"

        elif any(word in query_lower for word in [
            "employee", "teacher", "staff"
        ]):
            action = "employee_search"

        else:
            action = "student_search"

        # Employee search
        if action == "employee_search":

            employee = find_record_in_query(
                query,
                "employees",
                tenant_id,
                branch_id
            )

            if not employee:
                return {
                    "source_results": [{
                        "source": "school_db",
                        "status": "no_results",
                        "message": "No matching employee found."
                    }]
                }

            results = [employee]

            return {
                "source_results": [{
                    "source": "school_db",
                    "status": "success",
                    "action": action,
                    "data": results
                }]
            }

        # Identify student for student-related operations
        student = find_record_in_query(
            query,
            "students",
            tenant_id,
            branch_id
        )

        if not student:

            return {
                "source_results": [{
                    "source": "school_db",
                    "status": "no_results",
                    "message": (
                        "Student not found or the query matches "
                        "multiple students. Please provide a full name "
                        "or student ID."
                    )
                }]
            }

        student_id = student["student_id"]

        # Execute the requested operation
        if action == "attendance":

            data = get_student_attendance(
                student_id,
                tenant_id,
                branch_id
            )

        elif action == "fees":

            data = get_student_fees(
                student_id,
                tenant_id,
                branch_id
            )

        elif action == "fee_payments":

            data = get_student_fee_payments(
                student_id,
                tenant_id,
                branch_id
            )

        elif action == "transport":

            data = get_student_transport_details(
                student_id,
                tenant_id,
                branch_id
            )

        else:

            data = [student]

        return {
            "source_results": [{
                "source": "school_db",
                "status": "success" if data else "no_results",
                "action": action,
                "student_id": student_id,
                "student_name": student["full_name"],
                "data": data
            }]
        }

    except Exception:

        logging.exception("School database search failed.")

        return {
            "source_results": [{
                "source": "school_db",
                "status": "error",
                "message": "School database operation failed."
            }]
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
