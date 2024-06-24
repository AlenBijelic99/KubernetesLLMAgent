import logging

from crewai_tools import tool
from dotenv import load_dotenv
from google.auth import load_credentials_from_file
from google.auth.transport.requests import Request
from google.cloud.container_v1 import ClusterManagerClient
import google.auth
from kubernetes import client
import os

load_dotenv()


def get_gke_credentials(project_id, zone, cluster_id):
    try:
        credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_FILE')
        if not credentials_file:
            raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS_FILE environment variable is not set.")

        # Charger les informations d'identification avec les scopes appropriés
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = load_credentials_from_file(credentials_file, scopes=scopes)[0]

        # Rafraîchir le token si nécessaire
        if not credentials.valid or credentials.expired or credentials.token is None:
            credentials.refresh(Request())

        if not credentials.token:
            raise ValueError("The token could not be retrieved from the credentials.")

        cluster_manager_client = ClusterManagerClient(credentials=credentials)
        cluster = cluster_manager_client.get_cluster(
            name=f'projects/{project_id}/locations/{zone}/clusters/{cluster_id}')

        # Configure kubeconfig
        configuration = client.Configuration()
        configuration.host = f'https://{cluster.endpoint}'
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = cluster.master_auth.cluster_ca_certificate
        configuration.api_key = {"authorization": "Bearer " + credentials.token}
        client.Configuration.set_default(configuration)

        logging.info("Successfully obtained GKE credentials.")
    except Exception as e:
        logging.error(f"Exception when calling get_gke_credentials: {e}")
        return f"Exception when calling get_gke_credentials: {e}"


def get_pod_names(namespace: str) -> list:
    """Returns a list of pod names in the specified namespace."""
    v1 = client.CoreV1Api()

    try:
        pods = v1.list_namespaced_pod(namespace)
        return [pod.metadata.name for pod in pods.items]
    except client.ApiException as e:
        logging.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return f"Exception when calling CoreV1Api->list_namespaced_pod: {e}"
