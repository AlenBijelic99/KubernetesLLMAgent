from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import settings


def get_llm() -> BaseChatModel:
    """
    Get the LLM to use for the monitoring agent.

    gpt-* models are served by OpenAI; any other model name is assumed to be
    an Ollama model served at OLLAMA_BASE_URL (e.g. llama3.1, qwen3). Both
    support native tool calling through bind_tools.
    """
    model = settings.LLM_MODEL
    if model.startswith("gpt"):
        api_key = (
            SecretStr(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        )
        return ChatOpenAI(model=model, temperature=0, api_key=api_key)
    return ChatOllama(model=model, base_url=settings.OLLAMA_BASE_URL, temperature=0)
