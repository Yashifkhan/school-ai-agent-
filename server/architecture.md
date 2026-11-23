1. Main architecture
You have four knowledge sources:
1. LLM Knowledge: General knowledge and reasoning.
2. Vector Database: Internal school software documentation using RAG.
3. Web Search: Latest information from the internet.
4. School Database: Real-time student, attendance, fee, and other records.
Your classifier decides which of these sources are needed.
1. User Query

User sends a message through the school SaaS chat


2. Query Classifier

Understand intent, required sources, entities and ambiguity


3. Route Selection

Select one or more routes
LLM Knowledge


Vector DB / RAG


Web Search


School Database





4. Result Aggregator

Collect, validate and combine tool results


5. Response Generator

Generate an answer grounded in available evidence


6. Final Response to User


One important distinction: the four sources are not necessarily four independent autonomous agents. They can be specialized tools or workflows controlled by one LangGraph orchestrator.


*******************************
2. Step 1 – Query Classifier
This is the most important part of your architecture.

The classifier receives the user's message and decides:
- What does the user want?
- Which source can answer the question?
- Does the query need one source or multiple sources?
- Is clarification necessary?
- Is the user asking for an action or simply information?
For example:

User query:

"How can I add a new student to my school software?"

The classifier identifies:
{
  "intent": "software_help",
  "sources": ["vector_db"],
  "action": "answer",
  "needs_clarification": false
}


Another example:

User query:

"Show me Rahul's attendance for this month."

Classifier:
{
  "intent": "attendance_query",
  "sources": ["school_db"],
  "action": "retrieve_records",
  "needs_clarification": false
}


Another:

User query:

"What is the latest CBSE examination guideline, and how should I configure it in our school software?"

Classifier:
{
  "intent": "combined_query",
  "sources": ["web_search", "vector_db"],
  "action": "answer",
  "needs_clarification": false
}


Notice something important: the classifier can select multiple sources.
What should the classifier return?
I recommend a structured Pydantic schema.
from typing import Literalfrom pydantic import BaseModel, Fieldclass QueryRoute(BaseModel):    intent: str    sources: list[        Literal[            "llm_knowledge",            "vector_db",            "web_search",            "school_db"        ]    ] = Field(default_factory=list)    needs_clarification: bool = False    clarification_question: str | None = None    reason: str



This schema is the starting point. Later, you can add validated action types, required entities, and routing confidence.

My recommendation: Use an LLM with structured output for classification instead of relying only on keyword matching.

But never let the classifier decide authorization. Your backend must independently enforce permissions.


***************************************
3. Step 2 – Route Selection
After classification, LangGraph decides which nodes to execute.

Suppose the classifier returns:
{    "intent": "combined_query",    "sources": ["web_search", "vector_db"]}



Your graph should execute both selected routes.

The routing function should not execute tools itself. It should decide which graph nodes need to run.
Example routing function
def route_query(state):    sources = state["route"]["sources"]    selected_routes = []    if "llm_knowledge" in sources:        selected_routes.append("llm_knowledge")    if "vector_db" in sources:        selected_routes.append("vector_db")    if "web_search" in sources:        selected_routes.append("web_search")    if "school_db" in sources:        selected_routes.append("school_db")    return selected_routes



This is conceptual routing logic. In LangGraph, you can implement multiple outgoing edges using add_conditional_edges and a list-returning routing function, or use a dispatch node that creates parallel branches.



