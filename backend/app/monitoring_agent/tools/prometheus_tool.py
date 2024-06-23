import os
from dotenv import load_dotenv
from crewai_tools import tool
from prometheus_api_client import PrometheusConnect
import re

load_dotenv()


def is_valid_namespace(namespace: str) -> bool:
    """Validate namespace to be alphanumeric and possibly include some allowed characters."""
    pattern = re.compile(r'^[a-zA-Z0-9-_]+$')
    return bool(pattern.match(namespace))


@tool("Get summarized metrics of a namespace using Prometheus")
def get_metrics_of_namespace(namespace: str) -> str:
    """Returns summarized metrics of a namespace using Prometheus"""

    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

    # Connect to Prometheus
    prometheus = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    if not prometheus.check_prometheus_connection():
        return "Prometheus is not available"

    # Sanitize input to avoid injection
    if not is_valid_namespace(namespace):
        return "Invalid namespace. Only alphanumeric characters, dashes, and underscores are allowed."

    # Construct the queries
    queries = {
        "cpu_usage": f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}"}}[5m])) by (namespace)',
        "memory_usage": f'sum(container_memory_usage_bytes{{namespace="{namespace}"}}) by (namespace)'
    }

    results = {}
    for metric, query in queries.items():
        data = prometheus.custom_query(query=query)
        if data:
            results[metric] = data[0]['value'][1]  # Extract the value
        else:
            results[metric] = "No data"

    # Format the output
    result = "\n".join([f"{metric}: {value}" for metric, value in results.items()])

    return result


@tool("Execute Prometheus query")
def execute_prometheus_query(query: str) -> str:
    """Executes a custom Prometheus query and returns the result"""

    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

    # Connect to Prometheus
    prometheus = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    if not prometheus.check_prometheus_connection():
        return "Prometheus is not available"

    # Sanitize input to avoid injection
    sanitized_query = re.sub(r'[^\w\s{}[\]:,=()<>-]', '', query)

    # Execute the query
    data = prometheus.custom_query(query=sanitized_query)
    if not data:
        return "No data found"

    # Format the output
    result = "\n".join([f"{metric['metric']}: {metric['value'][1]}" for metric in data])

    return result
