from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool


def create_agent(
    llm: BaseChatModel, tools: list[BaseTool], system_message: str
) -> Runnable[Any, Any]:
    """
    Create an agent with the given LLM and tools.
    """
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
        prompt = prompt.partial(tool_names=", ".join(tool.name for tool in tools))
        return prompt | llm.bind_tools(tools)
    return prompt | llm
