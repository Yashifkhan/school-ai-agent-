import asyncio
import os
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.agent.response_node import response_node
from app.main import ChatRequest, chat
from app.services.ai_models import (
    AIProviderNotConfigured,
    InvalidAISelection,
    get_model_catalog,
    resolve_ai_selection,
)


class AIModelSelectionTests(unittest.TestCase):
    def test_catalog_reports_configured_providers_and_defaults(self):
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "",
            "GROQ_API_KEY": "configured",
            "GROQ_MODEL": "openai/gpt-oss-120b",
        }):
            catalog = get_model_catalog()

        self.assertEqual(catalog["default_provider"], "groq")
        self.assertEqual(catalog["default_model"], "openai/gpt-oss-120b")
        providers = {provider["id"]: provider for provider in catalog["providers"]}
        self.assertFalse(providers["gemini"]["configured"])
        self.assertTrue(providers["groq"]["configured"])

    def test_resolve_rejects_models_outside_provider_allowlist(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "configured"}):
            with self.assertRaises(InvalidAISelection):
                resolve_ai_selection("groq", "unlisted-model")

    def test_catalog_lists_requested_groq_models(self):
        requested_models = {
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-safeguard-20b",
            "meta-llama/llama-prompt-guard-2-86m",
            "whisper-large-v3-turbo",
        }

        with patch.dict(os.environ, {"GROQ_API_KEY": "configured"}):
            catalog = get_model_catalog()

        groq = next(item for item in catalog["providers"] if item["id"] == "groq")
        model_options = {item["id"]: item for item in groq["models"]}
        self.assertTrue(requested_models.issubset(model_options))
        self.assertFalse(
            model_options["meta-llama/llama-prompt-guard-2-86m"]["selectable"]
        )
        self.assertFalse(model_options["whisper-large-v3-turbo"]["selectable"])
        self.assertEqual(
            resolve_ai_selection("groq", "openai/gpt-oss-20b"),
            ("groq", "openai/gpt-oss-20b"),
        )

    def test_catalog_lists_requested_gemini_models(self):
        requested_models = {
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.1-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
        }

        with patch.dict(os.environ, {"GEMINI_API_KEY": "configured"}):
            catalog = get_model_catalog()

        gemini = next(
            item for item in catalog["providers"] if item["id"] == "gemini"
        )
        model_ids = {item["id"] for item in gemini["models"]}
        self.assertEqual(model_ids, requested_models)
        self.assertEqual(
            resolve_ai_selection("gemini", "gemini-3.7-flash"),
            ("gemini", "gemini-3.7-flash"),
        )

    def test_chat_selection_rejects_specialized_groq_models(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "configured"}):
            with self.assertRaises(InvalidAISelection):
                resolve_ai_selection(
                    "groq",
                    "meta-llama/llama-prompt-guard-2-86m",
                )
            with self.assertRaises(InvalidAISelection):
                resolve_ai_selection("groq", "whisper-large-v3-turbo")

    def test_resolve_rejects_unconfigured_provider(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaises(AIProviderNotConfigured):
                resolve_ai_selection("gemini", "gemini-3.5-flash-lite")

    def test_chat_passes_validated_selection_to_agent(self):
        run_agent = AsyncMock(return_value="Hello!")
        request = ChatRequest(
            query="Hi",
            provider="groq",
            model="openai/gpt-oss-120b",
        )

        with (
            patch("app.main.resolve_ai_selection", return_value=(
                "groq",
                "openai/gpt-oss-120b",
            )),
            patch("app.main.run_agent", run_agent),
        ):
            response = asyncio.run(chat(request))

        self.assertEqual(response.answer, "Hello!")
        run_agent.assert_awaited_once_with("Hi", "groq", "openai/gpt-oss-120b")

    def test_response_generation_errors_are_not_returned_as_success(self):
        model = Mock()
        model.invoke.side_effect = RuntimeError("provider call failed")
        state = {
            "query": "How do I add a student?",
            "provider": "groq",
            "model": "openai/gpt-oss-120b",
            "source_results": [{
                "source": "vector_db",
                "status": "success",
                "content": "Student registration instructions.",
            }],
        }

        with patch("app.agent.response_node.get_chat_model", return_value=model):
            with self.assertRaisesRegex(RuntimeError, "provider call failed"):
                response_node(state)


if __name__ == "__main__":
    unittest.main()
