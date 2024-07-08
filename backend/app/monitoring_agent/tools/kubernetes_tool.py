import logging
import os
from typing import List, Any

from langchain_core.tools import tool
from dotenv import load_dotenv
from kubernetes import client
from google.cloud import logging

from app.monitoring_agent.config.k8s_config import KubernetesConfig, GoogleCloudLogging

load_dotenv()

k8s_config = KubernetesConfig(
    kube_host=os.getenv("KUBE_HOST"),
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FILE"),
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

gcloud_logging_config = GoogleCloudLogging(
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FILE")
)

@tool
def get_pod_names(namespace: str) -> list[Any] | str:
    """Get pods in given namespace. Returns a list of pod names in the specified namespace."""
    v1 = k8s_config.get_client()

    try:
        pods = v1.list_namespaced_pod(namespace)
        return [pod.metadata.name for pod in pods.items]
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->list_namespaced_pod: {e}"


@tool
def get_nodes_resources() -> list[Any] | str:
    """Get nodes resources. Returns a list of nodes resources."""
    v1 = k8s_config.get_client()

    try:
        nodes = v1.list_node()
        return [node.status.capacity for node in nodes.items]
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->list_node: {e}")
        return f"Exception when calling CoreV1Api->list_node: {e}"


@tool
def get_pod_logs(logs_filter: str) -> str | list[Any]:
    """
        Get logs from a pod in a namespace. Returns logs of a pod in the specified namespace.

        Parameters:
        - logs_filter (str): The logs filter in the format of a Google Cloud Logging filter.

        Returns:
        - str: The requested logs.

        Example usage:
        >>> get_pod_logs('resource.type="k8s_container" resource.labels.project_id="plenary-stacker-422509-j4" resource.labels.location="europe-west6-a" resource.labels.cluster_name="gke-monitoring-agent" resource.labels.namespace_name="boutique" labels.k8s-pod/app="adservice" severity>=DEFAULT timestamp>="2024-07-08T16:41:00Z" timestamp<="2024-07-08T16:42:00Z"')
        """
    try:
        logging_client = gcloud_logging_config.get_client()

        entries = logging_client.list_entries(filter_=logs_filter)

        return entries

    except Exception as e:
        logging.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->list_namespaced_pod: {e}"


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
