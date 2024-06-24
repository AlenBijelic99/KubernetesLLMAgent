import logging
import os

from dotenv import load_dotenv

from app.monitoring_agent.tools.kubernetes_tool import get_pod_names, get_gke_credentials

load_dotenv()

from app.monitoring_agent.crew import MonitoringAssistantCrew


def run():
    namespaces = {
        'namespace': 'bookinfo'
    }
    project_id = "plenary-stacker-422509-j4"
    zone = "europe-west6-a"
    cluster_id = "gke-monitoring-agent"
    credentials_status = get_gke_credentials(project_id, zone, cluster_id)
    if isinstance(credentials_status, str) and "Exception" in credentials_status:
        logging.error(credentials_status)
    else:
        logging.info(get_pod_names('bookinfo'))
    MonitoringAssistantCrew().crew().kickoff(inputs=namespaces)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the monitoring agent")
    logging.info(get_pod_names('bookinfo'))
    run()

# Example usage
# namespace = "1"
# pod_name = "reviews-v1-69478d86db-95z9h"
# metric_name = "http_requests_total"
