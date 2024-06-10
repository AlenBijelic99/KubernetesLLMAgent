from dotenv import load_dotenv

load_dotenv()

from app.monitoring_agent.crew import MonitoringAssistantCrew


def run():
    namespaces = {
        'namespace': 'bookinfo'
    }
    MonitoringAssistantCrew().crew().kickoff(inputs=namespaces)


if __name__ == "__main__":
    run()

# Example usage
# namespace = "1"
# pod_name = "reviews-v1-69478d86db-95z9h"
# metric_name = "http_requests_total"
