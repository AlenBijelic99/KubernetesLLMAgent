import logging
import os

from dotenv import load_dotenv

from app.monitoring_agent.tools.kubernetes_tool import get_pod_names

load_dotenv()

from app.monitoring_agent.crew import MonitoringAssistantCrew


def run():
    namespaces = {
        'namespace': 'bookinfo'
    }
    try:
        MonitoringAssistantCrew().crew().kickoff(inputs=namespaces)
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    run()

# Example usage
# namespace = "1"
# pod_name = "reviews-v1-69478d86db-95z9h"
# metric_name = "http_requests_total"
