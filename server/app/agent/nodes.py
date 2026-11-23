


# Imports
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.routing import QueryClassification
from app.agent.state import AgentState

import os

load_dotenv()


# 1. Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


# 2. Structured output
structured_llm = llm.with_structured_output(
    QueryClassification,
    method="json_schema",
)


# 3. Classifier prompt
CLASSIFIER_PROMPT = """
You are a query classifier for a School SaaS AI Agent.

Available sources:

1. llm_knowledge: General knowledge and explanations.
2. vector_db: Internal school software documentation.
3. web_search: Latest external information.
4. school_db: Real-time school records.

Select one or multiple sources when necessary.
Ask for clarification when required information is missing.
Do not answer the user's question.
Return structured classification only.
"""


# 4. Original Gemini classifier
def classify_query(query: str) -> QueryClassification:

    messages = [
        ("system", CLASSIFIER_PROMPT),
        ("human", f"Classify this user query:\n{query}")
    ]

    result = structured_llm.invoke(messages)

    return result


# 5. LangGraph classifier node
def classify_query_node(state: AgentState):

    query = state["query"]

    classification = classify_query(query)

    return {
        "classification": classification
    }