import functools
from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from app.monitoring_agent.agent import create_agent
from app.monitoring_agent.llm import get_llm
from app.monitoring_agent.prompts import tasks_config
from app.monitoring_agent.state import AgentState
from app.monitoring_agent.tools.kubernetes_tool import (
    get_nodes_resources,
    get_pod_logs,
    get_pod_names,
    get_pod_resources,
    get_pod_yaml,
)
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query


def parse_config(config: dict[str, Any]) -> str:
    """
    Helper function to parse the task configuration into a system message.
    """
    return (
        f"role: {config['role']}, goal: {config['goal']}, "
        f"backstory: {config['backstory']}, description: {config['description']}, "
        f"expected_output: {config['expected_output']}, examples: {config['examples']}"
    )


def agent_node(state: AgentState, agent: Runnable, name: str) -> dict[str, Any]:
    """
    Helper function to create a node for a given agent.
    """
    result = agent.invoke(state)
    # Tag the message with the node name so the workflow (and the frontend)
    # knows which agent produced it.
    if isinstance(result, AIMessage):
        result = result.model_copy(update={"name": name})
    return {
        "messages": [result],
        # Since we have a strict workflow, we can track the sender so we know
        # who to pass to next.
        "sender": name,
    }


# Tools available for each agent node. Tool execution itself happens in the
# shared "call_tool" ToolNode of the graph.
NODE_TOOLS: dict[str, list[BaseTool]] = {
    "metric_analyser": [
        get_pod_names,
        execute_prometheus_query,
        get_pod_resources,
        get_nodes_resources,
    ],
    "diagnostic": [
        execute_prometheus_query,
        get_pod_logs,
        get_pod_yaml,
        get_pod_resources,
    ],
    "solution": [],
    "incident_reporter": [],
}

_NODE_TASKS = {
    "metric_analyser": "analyse_metric_task",
    "diagnostic": "diagnose_issue_task",
    "solution": "provide_solution_task",
    "incident_reporter": "report_incident_task",
}


def make_agent_node(name: str) -> Callable[[AgentState], dict[str, Any]]:
    """
    Build the graph node for the given agent name.

    Agents are created lazily (at graph construction time) instead of at
    import time, so importing this module does not require LLM credentials.
    """
    tools = NODE_TOOLS[name]
    agent = create_agent(
        get_llm(),
        tools,
        system_message=parse_config(tasks_config[_NODE_TASKS[name]]),
    )
    return functools.partial(agent_node, agent=agent, name=name)
