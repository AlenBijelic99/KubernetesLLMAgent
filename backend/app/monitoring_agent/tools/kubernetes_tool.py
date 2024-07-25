import logging
import os
from typing import List, Any, Dict

from langchain_core.tools import tool
from dotenv import load_dotenv
from kubernetes import client
from kubernetes.client import ApiClient
from kubernetes.client.api import custom_objects_api

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
def get_pod_resources(pod: str, namespace: str) -> Dict[str, Any] | str:
    """
     Get resources allocated to a specific pod in a namespace. Returns a dictionary with resource requests and
    limits.
    """
    v1 = k8s_config.get_client()

    try:
        pod_info = v1.read_namespaced_pod(pod, namespace)
        containers = pod_info.spec.containers
        resources = {
            'pod': pod,
            'namespace': namespace,
            'containers': []
        }

        for container in containers:
            container_resources = {
                'name': container.name,
                'requests': container.resources.requests if container.resources.requests else {},
                'limits': container.resources.limits if container.resources.limits else {}
            }
            resources['containers'].append(container_resources)

        return resources
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->read_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->read_namespaced_pod: {e}"

@tool
def get_nodes_resources() -> List[Dict[str, Any]] | str:
    """Get nodes resources. Returns a list of nodes resources including capacity and usage."""
    v1 = k8s_config.get_client()
    try:
        nodes = v1.list_node()
        metrics_api = custom_objects_api.CustomObjectsApi(ApiClient())
        node_metrics = metrics_api.list_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "nodes"
        )
        node_resources = []
        for node in nodes.items:
            capacity = node.status.capacity
            allocatable = node.status.allocatable
            usage = next((item['usage'] for item in node_metrics['items'] if item['metadata']['name'] == node.metadata.name), {})
            node_resources.append({
                'node': node.metadata.name,
                'capacity': capacity,
                'allocatable': allocatable,
                'usage': usage
            })
        return node_resources
    except Exception as e:
        logging.error(f"Exception when calling Metrics API: {e}")
        return f"Exception when calling Metrics API: {e}"


@tool
def get_pod_logs(logs_filter: str) -> str | list[Any]:
    """
        Get logs from a pod in a namespace. Returns logs of a pod in the specified namespace.

        Parameters:
        - logs_filter (str): The logs filter in the format of a Google Cloud Logging filter.

        Returns:
        - str: The requested logs.

        Notes:
        - Always use timestamp>= and timestamp<= to filter logs by time and avoid fetching all unnecessary logs.

        Example usage:
        >>> get_pod_logs('resource.type="k8s_container" resource.labels.project_id="plenary-stacker-422509-j4" resource.labels.location="europe-west6-a" resource.labels.cluster_name="gke-monitoring-agent" resource.labels.namespace_name="boutique" labels.k8s-pod/app="adservice" severity>=DEFAULT timestamp>="2024-07-08T16:41:00Z" timestamp<="2024-07-08T16:42:00Z"')
        """
    try:
        logging_client = gcloud_logging_config.get_client()

        entries = logging_client.list_entries(filter_=logs_filter, page_size=50)

        formatted_entries = [entry.to_api_repr() for entry in entries]

        # Convert list of entries to a single string
        entries_str = ''.join(map(str, formatted_entries))

        # Get the last 10000 characters to avoid OpenAI token limit
        if len(entries_str) > 10000:
            entries_str = entries_str[-10000:]

        return entries_str

    except Exception as e:
        logging.error(f"Exception with get_pod_logs: {e}")
        return f"Exception with get_pod_logs: {e}"


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
