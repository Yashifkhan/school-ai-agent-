
from typing import Annotated, TypedDict,Any
import operator

from app.schemas.routing import QueryClassification


class AgentState(TypedDict):

    query: str

    classification: QueryClassification | None

    source_results: Annotated[
        list[dict[str, Any]],
        operator.add
    ]