import os

from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_openai import ChatOpenAI


def get_llm():
    """
    Get the LLM model to use for the monitoring agent.
    """
    model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    if model.startswith("gpt"):
        return ChatOpenAI(model=model, temperature=0)
    elif model == "llama3":
        # EXPERIMENTAL OllamaFunctions
        # TODO: Currently does not work
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaFunctions(
            model=model,
            base_url=ollama_base_url,
            keep_alive=-1,
            temperature=0,
            max_new_tokens=512
        )
