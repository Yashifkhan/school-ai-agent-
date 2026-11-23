
from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState

from app.agent.nodes import classify_query_node

from app.agent.routing import route_after_classification


from app.agent.source_nodes import (
    llm_knowledge_node,
    vector_db_node,
    web_search_node,
    school_db_node,
    clarification_node,
)

# Create graph
builder = StateGraph(AgentState)

# Register classifier node
builder.add_node(
    "classify_query",
    classify_query_node
)


# Register source nodes
builder.add_node("llm_knowledge", llm_knowledge_node)
builder.add_node("vector_db", vector_db_node)
builder.add_node("web_search", web_search_node)
builder.add_node("school_db", school_db_node)
builder.add_node("clarification", clarification_node)


# Starting point
builder.add_edge(START, "classify_query")


# Conditional routing
builder.add_conditional_edges(
    "classify_query",
    route_after_classification,
    {
        "llm_knowledge": "llm_knowledge",
        "vector_db": "vector_db",
        "web_search": "web_search",
        "school_db": "school_db",
        "clarification": "clarification",
    }
)


# Connect source nodes to END
builder.add_edge("llm_knowledge", END)
builder.add_edge("vector_db", END)
builder.add_edge("web_search", END)
builder.add_edge("school_db", END)
builder.add_edge("clarification", END)


# Compile graph
agent_graph = builder.compile()
