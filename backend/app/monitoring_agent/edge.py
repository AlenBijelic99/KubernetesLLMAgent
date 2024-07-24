# Either agent can decide to end
from typing import Literal


def router(state) -> Literal["call_tool", "__end__", "continue"]:
    """
    The router function that decides which node to go to next based on the current state.

    Note: Sometime the LLM uses keywords that indicates we should continue with a keyword to end the conversation. That
    is why we check for those keywords.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    elif "DIAGNOSTIC NEEDED" in last_message.content or "GENERATE SOLUTIONS" in last_message.content:
        return "continue"
    if "UNSUCCESSFUL" in last_message.content or "FINISHED" in last_message.content:
        return "__end__"
    return "continue"
