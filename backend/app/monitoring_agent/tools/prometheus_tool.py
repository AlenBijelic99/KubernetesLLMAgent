import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from prometheus_api_client import PrometheusConnect

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
    Returns the CPU usage of a specific pod in the last 5 minutes:
    >>> execute_prometheus_query('sum(rate(container_cpu_usage_seconds_total{namespace="bookinfo", pod="details-v1-5997599bc6-vqzjq"}[5m])) by (pod)')
    '{pod="details-v1-5997599bc6-vqzjq"}: 0'
    An example of a query that returns HTTP requests per second by job, which is the name of the app
    >>> execute_prometheus_query('sum(rate(http_requests_total{namespace="testing-apps"}[5m])) by (job)')
    '{job="metric-app"}: 0'
    """

    try:
        prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

        # Connect to Prometheus
        prometheus = PrometheusConnect(url=prometheus_url, disable_ssl=True)

        if not prometheus.check_prometheus_connection():
            return "Prometheus is not available"

        # Sanitize input to avoid injection
        sanitized_query = query.replace('\\"', '"')

        # Execute the query
        data = prometheus.custom_query(query=sanitized_query)

        # Format the output
        result = "\n".join([f"{metric['metric']}: {metric['value'][1]}" for metric in data])

        return result
    except Exception as e:
        return f"Error executing Prometheus query: {e}"

@tool
def get_http_request_per_seconds_by_job(job: str) -> str:
    """
    Get the HTTP request per seconds for a specific job in the last minute.

    Parameters:
    - job (str): The job name to filter the request duration. It is made of {namespace}-{service name}.

    Returns:
    - str: The request duration for the specified job in the last minute.

    Notes:
    - Not all jobs may have HTTP requests, so the result may be 0 or No data found.

    Example usage:
    >>> get_http_request_per_seconds_by_job('sock-shop-user')
    '{job="sock-shop-user"}: 0.7'
    """

    query = f'sum(rate(request_duration_seconds_count{{job="{job}"}}[5m])) by (job)'
    return execute_prometheus_query(query)