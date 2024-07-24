import io
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict

from PIL import Image
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from app.api.deps import SessionDep
from app.crud import create_event, set_run_status
from app.monitoring_agent.agent_nodes import metric_analyser_node, diagnostic_node, solution_node, \
    incident_reporter_node
from app.monitoring_agent.edge import router
from app.monitoring_agent.state import AgentState
from app.monitoring_agent.tools.kubernetes_tool import get_pod_names, get_pod_logs, get_nodes_resources, get_pod_yaml, \
    get_pod_resources
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query

load_dotenv()

tools = [get_pod_names, execute_prometheus_query, get_pod_logs, get_nodes_resources, get_pod_yaml, get_pod_resources]
tool_node = ToolNode(tools)


def extract_message_info(message) -> Dict[str, Any]:
    if isinstance(message, HumanMessage):
        return {"type": "HumanMessage", "content": message.content}
    elif isinstance(message, AIMessage):
        tool_calls_info = [
            {
                "function_name": tool_call['function']['name'],
                "arguments": tool_call['function']['arguments']
            }
            for tool_call in message.additional_kwargs.get('tool_calls', [])
        ]
        return {
            "type": "AIMessage",
            "name": message.name,
            "content": message.content,
            "tool_calls": tool_calls_info
        }
    elif isinstance(message, ToolMessage):
        return {
            "type": "ToolMessage",
            "name": message.name,
            "content": message.content,
            "tool_call_id": message.tool_call_id
        }
    else:
        return {"type": "UnknownMessage"}


def event_to_json(event: Dict[str, Any]) -> Dict[str, Any]:
    def serialize_message(message):
        if isinstance(message, HumanMessage):
            return message.__dict__
        elif isinstance(message, AIMessage):
            return message.__dict__
        elif isinstance(message, ToolMessage):
            return message.__dict__
        return message

    def recursive_serialize(d):
        if isinstance(d, dict):
            return {k: recursive_serialize(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [recursive_serialize(item) for item in d]
        else:
            s = serialize_message(d)
            logging.error(f"Serialized: {s}")
            return serialize_message(d)

    return recursive_serialize(event)


def generate_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("metric_analyser", metric_analyser_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("solution", solution_node)
    workflow.add_node("incident_reporter", incident_reporter_node)
    workflow.add_node("call_tool", tool_node)

    workflow.add_conditional_edges(
        "metric_analyser",
        router,
        {"continue": "diagnostic", "call_tool": "call_tool", "__end__": "incident_reporter"},
    )

    workflow.add_conditional_edges(
        "diagnostic",
        router,
        {"continue": "solution", "call_tool": "call_tool", "__end__": "incident_reporter"},
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
            "__end__": "incident_reporter"
        },
    )

    workflow.add_edge("incident_reporter", END)

    workflow.set_entry_point("metric_analyser")

    graph = workflow.compile()

    return graph


def export_graph_image(graph):
    img_bytes = graph.get_graph(xray=1).draw_mermaid_png()
    image = Image.open(io.BytesIO(img_bytes))
    image.save("graph.png")
    image.show()


async def run(web_socket_manager, session: SessionDep, run_id: uuid.UUID):
    try:
        # Create the graph with full workflow
        graph = generate_graph()

        # Export the graph image
        export_graph_image(graph)

        namespaces = os.getenv("NAMESPACES", "default").split(',')

        current_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        input = {
            "messages": [
                HumanMessage(
                    content=f"Check the metrics for all pods in the following namespaces {', '.join(namespaces)}, "
                            f"and if needed run a diagnostic and find solutions to any issue. Current time is {current_time_utc}"
                )
            ],
        }

        create_event(session, run_id, event_to_json({"metric_analyser": input}))

        async for event in graph.astream(
                input,
                stream_mode="updates",
                config={"recursion_limit": 30},
        ):
            print(event)

            json_event = event_to_json(event)

            inserted_event = create_event(session, run_id, json_event)
            await web_socket_manager.send_json(json_event)

        set_run_status(session, run_id, "finished")

    except Exception as e:
        print("Exception details : ", e.__dict__)
        failed_event_info = {
            "type": "Error",
            "error": str(e),
            "event": event_to_json(event) if 'event' in locals() else None
        }
        create_event(session, run_id, failed_event_info)

        # Set status of run to "failed" in the database
        set_run_status(session, run_id, "failed")

        logging.error(f"Error: {e}")
        await web_socket_manager.send_json({"error": str(e)})
        raise e
    finally:
        await web_socket_manager.delete_current_run_json()
