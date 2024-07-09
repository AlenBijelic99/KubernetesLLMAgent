# Either agent can decide to end
from typing import Literal


def router(state) -> Literal["call_tool", "__end__", "continue"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if "UNSUCCESSFUL" or "FINISHED" in last_message.content:
        return "__end__"
    return "continue"
