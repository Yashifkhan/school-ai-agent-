
from typing import Literal
from pydantic import BaseModel, Field, model_validator


# Allowed knowledge sources
SourceType = Literal[
    "llm_knowledge",
    "vector_db",
    "web_search",
    "school_db",
]


class QueryClassification(BaseModel):
    """Structured output from the query classifier."""

    intent: str = Field(
        description="The main intention behind the user's query."
    )

    sources: list[SourceType] = Field(
        description=(
            "One or more knowledge sources required "
            "to answer the user's query."
        )
    )

    needs_clarification: bool = Field(
        description="Whether more information is required."
    )

    clarification_question: str | None = Field(
        default=None,
        description="Question to ask when clarification is needed."
    )

    reason: str = Field(
        description="Short explanation for the selected routes."
    )

    @model_validator(mode="after")
    def validate_clarification(self):
        if self.needs_clarification and not self.clarification_question:
            raise ValueError(
                "A clarification question is required."
            )

        if not self.needs_clarification and self.clarification_question:
            raise ValueError(
                "Clarification question must be None."
            )

        return self
