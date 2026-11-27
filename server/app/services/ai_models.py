import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

ProviderId = Literal["gemini", "groq"]

PROVIDER_OPTIONS = {
    "gemini": {
        "name": "Google Gemini",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "models": [
            {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash"},
            {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash"},
            {"id": "gemini-3.1-flash-lite", "name": "Gemini 3.1 Flash Lite"},
            {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
            {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite"},
        ],
    },
    "groq": {
        "name": "Groq",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "models": [
            {"id": "allam-2-7b", "name": "Allam 2 7B"},
            {"id": "openai/gpt-oss-20b", "name": "OpenAI GPT OSS 20B"},
            {"id": "openai/gpt-oss-120b", "name": "OpenAI GPT OSS 120B"},
            {
                "id": "openai/gpt-oss-safeguard-20b",
                "name": "OpenAI GPT OSS Safeguard 20B",
            },
            {
                "id": "meta-llama/llama-prompt-guard-2-86m",
                "name": "Llama Prompt Guard 2 86M",
                "selectable": False,
                "reason": "Safety classifier",
            },
            {
                "id": "whisper-large-v3-turbo",
                "name": "Whisper Large V3 Turbo",
                "selectable": False,
                "reason": "Audio transcription",
            },
        ],
    },
}


class InvalidAISelection(ValueError):
    pass


class AIProviderNotConfigured(RuntimeError):
    pass


def _default_model(provider: str) -> str:
    options = PROVIDER_OPTIONS[provider]["models"]
    configured_model = os.getenv(PROVIDER_OPTIONS[provider]["model_env"])

    if configured_model and any(
        option["id"] == configured_model
        and option.get("selectable", True)
        for option in options
    ):
        return configured_model

    return options[0]["id"]


def get_model_catalog() -> dict:
    configured_providers = [
        provider
        for provider, options in PROVIDER_OPTIONS.items()
        if os.getenv(options["key_env"])
    ]
    default_provider = (
        "gemini"
        if "gemini" in configured_providers
        else configured_providers[0]
        if configured_providers
        else "gemini"
    )

    providers = []
    for provider, options in PROVIDER_OPTIONS.items():
        providers.append({
            "id": provider,
            "name": options["name"],
            "configured": bool(os.getenv(options["key_env"])),
            "default_model": _default_model(provider),
            "models": options["models"],
        })

    return {
        "default_provider": default_provider,
        "default_model": _default_model(default_provider),
        "providers": providers,
    }


def resolve_ai_selection(
    provider: str | None,
    model: str | None,
) -> tuple[ProviderId, str]:
    selected_provider = provider or get_model_catalog()["default_provider"]

    if selected_provider not in PROVIDER_OPTIONS:
        raise InvalidAISelection("Choose a supported AI provider.")

    selected_model = model or _default_model(selected_provider)
    allowed_models = {
        option["id"]
        for option in PROVIDER_OPTIONS[selected_provider]["models"]
        if option.get("selectable", True)
    }
    if selected_model not in allowed_models:
        raise InvalidAISelection(
            "The selected model is not available for this provider."
        )

    key_env = PROVIDER_OPTIONS[selected_provider]["key_env"]
    if not os.getenv(key_env):
        raise AIProviderNotConfigured(
            f"{PROVIDER_OPTIONS[selected_provider]['name']} is not configured."
        )

    return selected_provider, selected_model


def get_chat_model(provider: str, model: str | None = None):
    selected_provider, selected_model = resolve_ai_selection(provider, model)
    return _get_chat_model(selected_provider, selected_model)


@lru_cache(maxsize=16)
def _get_chat_model(provider: ProviderId, model: str):
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.environ["GEMINI_API_KEY"],
            timeout=20,
            max_retries=1,
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        api_key=os.environ["GROQ_API_KEY"],
        timeout=20,
        max_retries=1,
    )
