import logging
import time
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.services.ai_models import (
    AIProviderNotConfigured,
    InvalidAISelection,
    get_model_catalog,
    resolve_ai_selection,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="School SaaS AI Agent API",
    description="API for the school management SaaS AI assistant.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)
    provider: Literal["gemini", "groq"] | None = None
    model: str | None = Field(default=None, min_length=1, max_length=100)


class ChatResponse(BaseModel):
    answer: str


async def run_agent(query: str, provider: str, model: str) -> str:
    from app.agent.graph import agent_graph

    started_at = time.perf_counter()
    try:
        result = await agent_graph.ainvoke({
            "query": query,
            "source_results": [],
            "provider": provider,
            "model": model,
        })
        print("test output in terminal ",result)
    finally:
        logger.info(
            "Agent graph execution took %.2fs",
            time.perf_counter() - started_at,
        )
    answer = result.get("final_answer")

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("The agent returned no final answer.")

    return answer


@app.get("/health", tags=["health"])
async def health() -> dict:
    catalog = get_model_catalog()
    selected_provider = next(
        item
        for item in catalog["providers"]
        if item["id"] == catalog["default_provider"]
    )

    return {
        "status": "ok",
        "ai_provider": selected_provider["name"],
        "ai_model": catalog["default_model"],
        "ai_configured": selected_provider["configured"],
        **catalog,
    }


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        provider, model = resolve_ai_selection(
            request.provider,
            request.model,
        )
    except InvalidAISelection as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except AIProviderNotConfigured as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    try:
        answer = await run_agent(request.query, provider, model)
    except Exception as error:
        logger.exception("AI agent request failed.")
        raise HTTPException(
            status_code=503,
            detail="The AI agent is temporarily unavailable.",
        ) from error

    return ChatResponse(answer=answer)
