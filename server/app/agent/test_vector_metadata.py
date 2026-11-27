import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.agent.response_node import response_node
from app.agent.source_nodes import vector_db_node


class VectorMetadataTests(unittest.TestCase):
    def test_vector_node_does_not_pass_ids_or_scores_to_agent_state(self):
        search_results = [{
            "id": "private-vector-id",
            "content": "School transport routes are managed in settings.",
            "source_document": "Transport guide",
            "page": "4",
            "score": 0.91,
        }]

        with patch(
            "app.agent.source_nodes.asyncio.to_thread",
            new=AsyncMock(return_value=search_results),
        ):
            result = asyncio.run(vector_db_node({
                "query": "How do I manage student transport?",
            }))

        vector_result = result["source_results"][0]
        self.assertEqual(
            vector_result,
            {
                "source": "vector_db",
                "status": "success",
                "content": "School transport routes are managed in settings.",
                "source_document": "Transport guide",
                "page": "4",
            },
        )

    def test_response_prompt_strips_vector_ids_and_scores(self):
        model = Mock()
        model.invoke.return_value = Mock(
            content="Manage the routes from the transport settings.",
        )
        state = {
            "query": "How do I manage student transport?",
            "source_results": [{
                "source": "vector_db",
                "status": "success",
                "content": "School transport routes are managed in settings.",
                "source_document": "Transport guide",
                "page": "4",
                "chunk_id": "private-vector-id",
                "score": 0.91,
            }],
        }

        with patch("app.agent.response_node.get_chat_model", return_value=model):
            result = response_node(state)

        messages = model.invoke.call_args.args[0]
        prompt = "\n".join(message[1] for message in messages)
        self.assertNotIn("private-vector-id", prompt)
        self.assertNotIn('"score"', prompt)
        self.assertEqual(
            result["final_answer"],
            "Manage the routes from the transport settings.",
        )


if __name__ == "__main__":
    unittest.main()
