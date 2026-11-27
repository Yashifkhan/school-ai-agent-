import asyncio
import unittest
from unittest.mock import Mock, patch

from app.agent.graph import agent_graph
from app.agent.routing import route_after_classification
from app.main import ChatRequest, chat
from app.schemas.routing import QueryClassification


def make_classification(
    sources: list[str],
    needs_clarification: bool = False,
    clarification_question: str | None = None,
) -> QueryClassification:
    return QueryClassification(
        intent="test",
        sources=sources,
        needs_clarification=needs_clarification,
        clarification_question=clarification_question,
        reason="test classification",
    )


class RoutingTests(unittest.TestCase):
    def test_empty_sources_without_clarification_routes_safely(self):
        state = {
            "classification": make_classification([]),
        }

        with self.assertLogs("app.agent.routing", level="WARNING"):
            route = route_after_classification(state)

        self.assertEqual(route, ["clarification"])

    def test_requested_clarification_routes_to_clarification_node(self):
        state = {
            "classification": make_classification(
                [],
                needs_clarification=True,
                clarification_question="Which student?",
            ),
        }

        self.assertEqual(route_after_classification(state), ["clarification"])

    def test_duplicate_sources_are_deduplicated(self):
        state = {
            "classification": make_classification([
                "llm_knowledge",
                "llm_knowledge",
                "web_search",
            ]),
        }

        self.assertEqual(
            route_after_classification(state),
            ["llm_knowledge", "web_search"],
        )

    def test_graph_returns_clarification_instead_of_failing_for_empty_sources(self):
        classification = make_classification([])
        classify = Mock(return_value=classification)

        with patch("app.agent.nodes.classify_query", classify):
            result = asyncio.run(agent_graph.ainvoke({
                "query": "Hi",
                "source_results": [],
                "provider": "groq",
                "model": "openai/gpt-oss-20b",
            }))

        classify.assert_called_once_with(
            "Hi",
            "groq",
            "openai/gpt-oss-20b",
        )
        self.assertEqual(
            result["final_answer"],
            "I couldn't determine which information source is needed. "
            "Could you rephrase your question or add a little more context?",
        )
        self.assertEqual(
            result["source_results"][0]["source"],
            "clarification",
        )

    def test_chat_endpoint_returns_answer_instead_of_503(self):
        classification = make_classification([])

        with (
            patch(
                "app.main.resolve_ai_selection",
                return_value=("groq", "openai/gpt-oss-20b"),
            ),
            patch("app.agent.nodes.classify_query", return_value=classification),
        ):
            response = asyncio.run(chat(ChatRequest(
                query="Hi",
                provider="groq",
                model="openai/gpt-oss-20b",
            )))

        self.assertIn("rephrase your question", response.answer)


if __name__ == "__main__":
    unittest.main()
