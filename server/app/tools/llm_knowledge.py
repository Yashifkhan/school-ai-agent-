import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# 1. Validate configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL is missing from .env")


# 2. Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
)


# 3. System instructions
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


# 4. Reusable LLM Knowledge function
def answer_general_question(query: str) -> str:

    if not query or not query.strip():
        raise ValueError("User query cannot be empty.")

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", query)
    ]

    # Generate answer
    response = llm.invoke(messages)

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
        raise RuntimeError("Gemini returned an empty response.")

    return answer