from typing import Literal

from app.monitoring_agent.state import AgentState


def router(state: AgentState) -> Literal["call_tool", "__end__", "continue"]:
    """
    Decides which node to go to next based on the current state.

    The agents are instructed to end their reports with control keywords
    (DIAGNOSTIC NEEDED, GENERATE SOLUTIONS, UNSUCCESSFUL, FINISHED), which
    are used here to route the workflow.
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "call_tool"
    content = str(last_message.content)
    if "DIAGNOSTIC NEEDED" in content or "GENERATE SOLUTIONS" in content:
        return "continue"
    if "UNSUCCESSFUL" in content or "FINISHED" in content:
        return "__end__"
    return "continue"
