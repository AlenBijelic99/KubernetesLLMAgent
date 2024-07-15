import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_openai import ChatOpenAI

from app.monitoring_agent.tools.tool_binder import extract_tool_metadata


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    system_message_text = (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants struggle with the question, you can all decide to stop,"
        " do it by prefix your response with UNSUCCESSFUL and give a summary of the progress made so far."
        " If you successfully answer the question and no diagnostic is needed, do it by prefix your response with"
        " FINISHED."
    )

    if tools:
        system_message_text += " You have access to the following tools: {tool_names}."

    system_message_text += " {system_message}"

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message_text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)

    if tools:
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    if tools:
        if isinstance(llm, ChatOpenAI):
            prompt_with_llm = prompt | llm.bind_tools(tools)
        elif isinstance(llm, OllamaFunctions):
            binded_tools = [extract_tool_metadata(tool) for tool in tools]
            print("binded_tools: ", binded_tools)
            prompt_with_llm = prompt | llm.bind_tools(tools=tools)
        else:
            raise Exception("Unsupported LLM model")
    else:
        prompt_with_llm = prompt | llm

    return prompt_with_llm
