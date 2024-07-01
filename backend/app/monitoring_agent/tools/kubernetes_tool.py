import logging
import os

from langchain_core.tools import tool
from dotenv import load_dotenv
from kubernetes import client

from app.monitoring_agent.config.k8s_config import KubernetesConfig

load_dotenv()

k8s_config = KubernetesConfig(
    kube_host=os.getenv("KUBE_HOST"),
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FILE"),
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)


@tool
def get_pod_names(namespace: str) -> list:
    """Get pods in given namespace. Returns a list of pod names in the specified namespace."""
    v1 = k8s_config.get_client()

    try:
        pods = v1.list_namespaced_pod(namespace)
        return [pod.metadata.name for pod in pods.items]
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->list_namespaced_pod: {e}"


@tool
def get_pod_logs(pod: str, namespace: str) -> str:
    """ Get logs from a pod in a namespace. Returns logs of a pod in the specified namespace."""
    v1 = k8s_config.get_client()

    try:
        logs = v1.read_namespaced_pod_log(pod, namespace)
        return logs
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->read_namespaced_pod_log: {e}")
        return f"Exception when calling CoreV1Api->read_namespaced_pod_log: {e}"


@tool
def get_pod_yaml(pod: str, namespace: str) -> str:
    """Get pod YAML configuration in a namespace. Returns the YAML configuration of a pod in the specified namespace."""
    v1 = k8s_config.get_client()

    try:
        pod = v1.read_namespaced_pod(pod, namespace)
        return pod
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->read_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->read_namespaced_pod: {e}"
