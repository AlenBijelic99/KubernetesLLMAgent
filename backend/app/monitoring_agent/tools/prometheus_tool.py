from langchain_core.tools import tool
from prometheus_api_client import PrometheusConnect

from app.core.config import settings


@tool
def execute_prometheus_query(query: str) -> str:
    """
    Executes a custom Prometheus query with the prometheus_api_client and returns the result.

    Parameters:
    - query (str): The PromQL query to execute without query

    Returns:
    - str: The result of the query in a readable format.

    Example usage:
    Returns the CPU usage of a specific pod in the last 5 minutes:
    >>> execute_prometheus_query('sum(rate(container_cpu_usage_seconds_total{namespace="bookinfo", pod="details-v1-5997599bc6-vqzjq"}[5m])) by (pod)')
    '{pod="details-v1-5997599bc6-vqzjq"}: 0'
    An example of a query that returns HTTP requests per second by job, which is the name of the app
    >>> execute_prometheus_query('sum(rate(http_requests_total{namespace="testing-apps"}[5m])) by (job)')
    '{job="metric-app"}: 0'
    """
    try:
        prometheus_url = settings.PROMETHEUS_URL or "http://localhost:9090"

        # Connect to Prometheus. TLS verification is enabled unless
        # explicitly disabled with PROMETHEUS_VERIFY_SSL=False.
        prometheus = PrometheusConnect(
            url=prometheus_url, disable_ssl=not settings.PROMETHEUS_VERIFY_SSL
        )

        if not prometheus.check_prometheus_connection():
            return "Prometheus is not available"

        # The LLM sometimes escapes quotes in the generated PromQL
        sanitized_query = query.replace('\\"', '"')

        # Execute the query
        data = prometheus.custom_query(query=sanitized_query)

        # Format the output
        result = "\n".join(
            f"{metric['metric']}: {metric['value'][1]}" for metric in data
        )

        return result
    except Exception as e:
        return f"Error executing Prometheus query: {e}"
