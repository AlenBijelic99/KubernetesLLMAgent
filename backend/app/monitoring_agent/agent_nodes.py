import functools
import os

from langchain_core.messages import AIMessage, ToolMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_openai import ChatOpenAI

from app.monitoring_agent.agent import create_agent
from app.monitoring_agent.llm import get_llm
from app.monitoring_agent.prompts import tasks_config
from app.monitoring_agent.tools.kubernetes_tool import get_pod_names, get_pod_logs, get_nodes_resources, get_pod_yaml
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query, get_http_request_per_seconds_by_job

base_dir = os.path.dirname(os.path.abspath(__file__))


def parse_config(config):
    return f"role: {config['role']}, goal: {config['goal']}, backstory: {config['backstory']}, description: {config['description']}, expected_output: {config['expected_output']}, examples: {config['examples']}"


# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


metric_analyser_tools = [get_pod_names, execute_prometheus_query, get_nodes_resources,
                         get_http_request_per_seconds_by_job]
diagnostic_tools = [execute_prometheus_query, get_pod_logs, get_pod_yaml, get_http_request_per_seconds_by_job]
solution_tools = []
incident_tools = []

metric_analyser_agent = create_agent(
    get_llm(metric_analyser_tools),
    metric_analyser_tools,
    system_message=parse_config(tasks_config["analyse_metric_task"]),
)
metric_analyser_node = functools.partial(agent_node, agent=metric_analyser_agent, name="metric_analyser")

diagnostic_agent = create_agent(
    get_llm(diagnostic_tools),
    diagnostic_tools,
    system_message=parse_config(tasks_config["diagnose_issue_task"]),
)
diagnostic_node = functools.partial(agent_node, agent=diagnostic_agent, name="diagnostic")

solution_agent = create_agent(
    get_llm(solution_tools),
    solution_tools,
    system_message=parse_config(tasks_config["provide_solution_task"]),
)
solution_node = functools.partial(agent_node, agent=solution_agent, name="solution")

incident_reporter_agent = create_agent(
    get_llm(incident_tools),
    incident_tools,
    system_message=parse_config(tasks_config["report_incident_task"]),
)
incident_reporter_node = functools.partial(agent_node, agent=incident_reporter_agent, name="incident_reporter")
