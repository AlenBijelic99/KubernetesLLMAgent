import io
import json
import logging
from typing import Any

from PIL import Image
from dotenv import load_dotenv
from kubernetes import client
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from app.monitoring_agent.agent_nodes import metric_analyser_node, diagnostic_node, solution_node, \
    incident_reporter_node
from app.monitoring_agent.edge import router
from app.monitoring_agent.graph import AgentState
from app.monitoring_agent.tools.kubernetes_tool import get_pod_names, get_pod_logs
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query

load_dotenv()

tools = [get_pod_names, execute_prometheus_query, get_pod_logs]
tool_node = ToolNode(tools)


def extract_message_info(message):
    if isinstance(message, HumanMessage):
        return {"type": "HumanMessage", "content": message.content}
    elif isinstance(message, AIMessage):
        tool_calls_info = []
        for tool_call in message.additional_kwargs.get('tool_calls', []):
            tool_call_info = {
                "function_name": tool_call.get('function', {}).get('name'),
                "arguments": tool_call.get('function', {}).get('arguments')
            }
            tool_calls_info.append(tool_call_info)
        return {
            "type": "AIMessage",
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


async def run(manager):
    workflow = StateGraph(AgentState)

    workflow.add_node("metric_analyser", metric_analyser_node)
    """workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("solution", solution_node)
    workflow.add_node("incident_reporter", incident_reporter_node)"""
    workflow.add_node("call_tool", tool_node)

    workflow.add_conditional_edges(
        "metric_analyser",
        router,
        {"continue": END, "call_tool": "call_tool", "__end__": END},
    )
    """
    workflow.add_conditional_edges(
        "diagnostic",
        router,
        {"continue": "solution", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "solution",
        router,
        {"continue": "incident_reporter", "call_tool": "call_tool", "__end__": END},
    )"""

    workflow.add_conditional_edges(
        "call_tool",
        lambda x: x["sender"],
        {
            "metric_analyser": "metric_analyser",
        },
    )
    workflow.set_entry_point("metric_analyser")
    graph = workflow.compile()

    img_bytes = graph.get_graph(xray=1).draw_mermaid_png()
    image = Image.open(io.BytesIO(img_bytes))
    image.save("graph.png")
    image.show()

    async for event in graph.astream(
            {
                "messages": [
                    HumanMessage(
                        content="Check the metrics for all pods in the 'boutique' namespace."
                    )
                ],
            },
            stream_mode="updates"
    ):
        try:
            extracted_info = []

            for key, value in event.items():
                if isinstance(value, list):
                    for message in value:
                        extracted_info.append(extract_message_info(message))
                else:
                    extracted_info.append({key: value})

            print("Extraced_info", extracted_info)
            #extracted_info_json = json.dumps(extracted_info, indent=2)
            #print(extracted_info_json)
            #await manager.send_json(extracted_info_json)

        except Exception as e:
            logging.error(f"Error: {e}")
            await manager.send_json({"error": str(e)})
