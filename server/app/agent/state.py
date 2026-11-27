
# from typing import Annotated, TypedDict,Any
# import operator

# from app.schemas.routing import QueryClassification


# class AgentState(TypedDict):

#     query: str

#     classification: QueryClassification | None

#     source_results: Annotated[
#         list[dict[str, Any]],
#         operator.add
#     ]







from typing import Annotated, TypedDict, Any, NotRequired
import operator

from app.schemas.routing import QueryClassification


class AgentState(TypedDict):

    query: str

    classification: NotRequired[QueryClassification | None]

    source_results: Annotated[
        list[dict[str, Any]],
        operator.add
    ]

    # Trusted context supplied by the backend
    tenant_id: NotRequired[str]

    # Optional branch restriction
    branch_id: NotRequired[str | None]
    provider: NotRequired[str]
    model: NotRequired[str]
    final_answer: NotRequired[str]
