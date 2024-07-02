import io
import logging

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
        # Each agent node updates the 'sender' field
        # the tool calling node does not, meaning
        # this edge will route back to the original agent
        # who invoked the tool
        lambda x: x["sender"],
        {
            "metric_analyser": "metric_analyser",
            "diagnostic": "diagnostic",
            "solution": "solution",
        },
    )
    workflow.set_entry_point("metric_analyser")
    graph = workflow.compile()

    # Générer l'image en mémoire
    img_bytes = graph.get_graph(xray=1).draw_mermaid_png()

    # Ouvrir l'image en utilisant PIL
    image = Image.open(io.BytesIO(img_bytes))

    # Sauvegarder l'image sur le disque
    image.save("graph.png")

    # Afficher l'image (facultatif)
    image.show()

    await manager.send_message("Agent started")

    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="Check the metrics for all pods in the 'boutique' namespace."
                )
            ],
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 150},
    )
    for s in events:
        await manager.send_message(f"Step: {s}")
        print(s)
        print("----")

    await manager.send_message("Agent finished successfully")
