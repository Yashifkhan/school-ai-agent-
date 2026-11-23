
from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):

    title: str

    url: str

    content: str

    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )


class WebSearchResponse(BaseModel):

    query: str

    results: list[WebSearchResult]

    response_time: float | None = None

    request_id: str | None = None
