from crewai_tools import tool
from kubernetes import client, config


@tool("Get pods in a given namespace")
def get_pod_names(namespace: str) -> list:
    """Returns a list of pod names in the specified namespace."""
    config.load_kube_config(context='gke_plenary-stacker-422509-j4_europe-west6-a_gke-monitoring-agent')
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]
