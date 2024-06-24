import os
from dotenv import load_dotenv
from crewai_tools import tool
from prometheus_api_client import PrometheusConnect
import re

load_dotenv()

@tool("Execute Prometheus query")
def execute_prometheus_query(query: str) -> str:
    """Executes a custom Prometheus query and returns the result"""

    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

    # Connect to Prometheus
    prometheus = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    if not prometheus.check_prometheus_connection():
        return "Prometheus is not available"

    # Sanitize input to avoid injection
    sanitized_query = re.sub(r'[^\w\s{}[\]:,=()<>\'"]', '', query)

    # Execute the query
    data = prometheus.custom_query(query=sanitized_query)
    if not data:
        return "No data found"

    # Format the output
    result = "\n".join([f"{metric['metric']}: {metric['value'][1]}" for metric in data])

    return result
