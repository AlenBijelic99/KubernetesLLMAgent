import logging
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from prometheus_api_client import PrometheusConnect
import re

load_dotenv()


@tool
def execute_prometheus_query(query: str) -> str:
    """
    Executes a custom Prometheus query with the prometheus_api_client and returns the result.

    Parameters:
    - query (str): The PromQL query to execute without query

    Returns:
    - str: The result of the query in a readable format.

    Example usage:
    >>> execute_prometheus_query('sum(rate(container_cpu_usage_seconds_total{namespace="bookinfo", pod="details-v1-5997599bc6-vqzjq"}[5m])) by (pod)')
    '{pod="details-v1-5997599bc6-vqzjq"}: 0'
    """

    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

    # Connect to Prometheus
    prometheus = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    if not prometheus.check_prometheus_connection():
        return "Prometheus is not available"

    # Sanitize input to avoid injection
    sanitized_query = re.sub(r'[^\w\s{}[\]:,=()\-\'"]', '', query.replace('\\"', '"'))

    # Execute the query
    data = prometheus.custom_query(query=sanitized_query)
    if not data:
        return "No data found"

    # Format the output
    result = "\n".join([f"{metric['metric']}: {metric['value'][1]}" for metric in data])

    return result
