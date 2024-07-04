from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " The workflow concists of multiple steps, each assistant will perform a specific task. "
                " The steps are metric analysis, diagnostic, solution, and incident report. "
                " The metric analysis assistant will analyze the metrics to identify the issue. "
                " The diagnostic assistant will diagnose the issue based on the analysis. "
                " The solution assistant will provide a solution to the issue. "
                " The incident report assistant will report the incident. "
                " If you or any of the other assistants struggle with your given task, you can all decide to stop,"
                " do it by prefix your response with FINAL ANSWER so the team knows to stop."
                " Only use it if the team is stuck and can't make progress. "
                " Discovering an issue is not a reason to stop. "
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    # TODO: Need a find a solution to bind tool in Ollama way. Here bind_tools is defined in langchain for ChatGPT
    return prompt | llm.bind_tools(tools)