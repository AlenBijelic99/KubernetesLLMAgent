import io
import logging
from asyncio import sleep

from PIL import Image
from dotenv import load_dotenv
from kubernetes import client
from langchain_core.messages import HumanMessage
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


async def run(manager):
    workflow = StateGraph(AgentState)

    workflow.add_node("metric_analyser", metric_analyser_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("solution", solution_node)
    workflow.add_node("incident_reporter", incident_reporter_node)
    workflow.add_node("call_tool", tool_node)

    workflow.add_conditional_edges(
        "metric_analyser",
        router,
        {"continue": "diagnostic", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "diagnostic",
        router,
        {"continue": "solution", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "solution",
        router,
        {"continue": "incident_reporter", "call_tool": "call_tool", "__end__": END},
    )

    workflow.add_conditional_edges(
        "call_tool",
        lambda x: x["sender"],
        {
            "metric_analyser": "metric_analyser",
            "diagnostic": "diagnostic",
            "solution": "solution",
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
        await manager.send_json(f"{event}")

    await manager.send_json("Agent finished successfully")
    logging.warning("Sent: Agent finished successfully")

