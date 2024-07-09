import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    system_message_text = (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants struggle with the question, you can all decide to stop,"
        " do it by prefix your response with UNSUCCESSFUL and give a summary of the progress made so far."
        " If you successfully answer the question, do it by prefix your response with FINISHED."
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
        # TODO: Need to find a solution to bind tool in Ollama way. Here bind_tools is defined in langchain for ChatGPT
        return prompt | llm.bind_tools(tools)
    else:
        return prompt | llm
