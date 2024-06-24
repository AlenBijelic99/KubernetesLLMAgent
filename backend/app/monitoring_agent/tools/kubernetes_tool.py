import logging
import os

from crewai_tools import tool
from dotenv import load_dotenv
from kubernetes import client

from app.monitoring_agent.config.k8s_config import KubernetesConfig

load_dotenv()

k8s_config = KubernetesConfig(
    kube_host=os.getenv("KUBE_HOST"),
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FILE"),
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)


@tool("Get pod names in a namespace")
def get_pod_names(namespace: str) -> list:
    """Returns a list of pod names in the specified namespace."""
    v1 = k8s_config.get_client()

    try:
        pods = v1.list_namespaced_pod(namespace)
        return [pod.metadata.name for pod in pods.items]
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->list_namespaced_pod: {e}"
