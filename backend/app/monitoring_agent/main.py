import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from sqlmodel import Session

from app.core.config import settings
from app.crud import create_event, set_run_status
from app.monitoring_agent.agent_nodes import make_agent_node
from app.monitoring_agent.edge import router
from app.monitoring_agent.state import AgentState
from app.monitoring_agent.tools.kubernetes_tool import (
    get_nodes_resources,
    get_pod_logs,
    get_pod_names,
    get_pod_resources,
    get_pod_yaml,
)
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query
from app.websocket.websocket import ConnectionManager

TOOLS = [
    get_pod_names,
    execute_prometheus_query,
    get_pod_logs,
    get_nodes_resources,
    get_pod_yaml,
    get_pod_resources,
]


def event_to_json(event: Any) -> Any:
    """
    Recursively convert a graph event into JSON-serializable data,
    serializing LangChain messages along the way.
    """
    if isinstance(event, BaseMessage):
        return event.model_dump()
    if isinstance(event, dict):
        return {k: event_to_json(v) for k, v in event.items()}
    if isinstance(event, list):
        return [event_to_json(item) for item in event]
    return event


def generate_graph() -> Any:
    """
    Build and compile the monitoring workflow:
    metric_analyser -> diagnostic -> solution -> incident_reporter,
    with a shared tool node and keyword-based routing between steps.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("metric_analyser", make_agent_node("metric_analyser"))
    workflow.add_node("diagnostic", make_agent_node("diagnostic"))
    workflow.add_node("solution", make_agent_node("solution"))
    workflow.add_node("incident_reporter", make_agent_node("incident_reporter"))
    workflow.add_node("call_tool", ToolNode(TOOLS))

    workflow.add_conditional_edges(
        "metric_analyser",
        router,
        {
            "continue": "diagnostic",
            "call_tool": "call_tool",
            "__end__": "incident_reporter",
        },
    )

    workflow.add_conditional_edges(
        "diagnostic",
        router,
        {
            "continue": "solution",
            "call_tool": "call_tool",
            "__end__": "incident_reporter",
        },
    )
    workflow.add_conditional_edges(
        "solution",
        router,
        {"continue": "incident_reporter", "__end__": "incident_reporter"},
    )

    workflow.add_conditional_edges(
        "call_tool",
        lambda x: x["sender"],
        {
            "metric_analyser": "metric_analyser",
            "diagnostic": "diagnostic",
            "__end__": "incident_reporter",
        },
    )

    workflow.add_edge("incident_reporter", END)

    workflow.set_entry_point("metric_analyser")

    return workflow.compile()


async def run(
    web_socket_manager: ConnectionManager, session: Session, run_id: uuid.UUID
) -> None:
    """
    Execute the monitoring workflow, persisting every event of the run and
    broadcasting it to the connected websocket clients.
    """
    event: dict[str, Any] | None = None
    try:
        graph = generate_graph()

        namespaces = (
            settings.NAMESPACES
            if isinstance(settings.NAMESPACES, list)
            else [settings.NAMESPACES]
        )
        current_time_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        input_state = {
            "messages": [
                HumanMessage(
                    content=f"Check the metrics for all pods in the following namespaces {', '.join(namespaces)}, "
                    f"and if needed run a diagnostic and find solutions to any issue. Current time is {current_time_utc}"
                )
            ],
        }

        create_event(
            session=session,
            run_id=run_id,
            event_data=event_to_json({"metric_analyser": input_state}),
        )

        async for event in graph.astream(
            input_state,
            stream_mode="updates",
            config={"recursion_limit": 30},
        ):
            json_event = event_to_json(event)
            create_event(session=session, run_id=run_id, event_data=json_event)
            await web_socket_manager.send_json(json_event)

        set_run_status(session=session, run_id=run_id, status="finished")

    except Exception as e:
        logging.exception("Agent run %s failed", run_id)
        failed_event_info = {
            "type": "Error",
            "error": str(e),
            "event": event_to_json(event) if event is not None else None,
        }
        create_event(session=session, run_id=run_id, event_data=failed_event_info)
        set_run_status(session=session, run_id=run_id, status="failed")
        await web_socket_manager.send_json({"error": str(e)})
        raise
    finally:
        web_socket_manager.delete_current_run_json()
