import logging
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from kubernetes import client
from google.cloud import logging as gcloud_logging


class KubernetesConfig:
    """
    Manage the configuration of the Kubernetes client
    """

    def __init__(self, kube_host: str, credentials_path: str, scopes: list):
        """
        Initialize the Kubernetes configuration
        """
        self.kube_host = kube_host
        self.credentials_path = credentials_path
        self.scopes = scopes
        self.configuration = None
        self.v1 = None

    def authenticate(self):
        """
        Authenticate with the Kubernetes cluster
        """
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.scopes
        )

        # Get access token
        credentials.refresh(Request())

        # Configure the Kubernetes client
        self.configuration = client.Configuration()
        self.configuration.host = self.kube_host
        self.configuration.verify_ssl = False
        self.configuration.debug = True
        self.configuration.api_key = {"authorization": "Bearer " + credentials.token}
        client.Configuration.set_default(self.configuration)
        self.v1 = client.CoreV1Api()

    def get_client(self):
        """
        Singleton method to get the Kubernetes client
        """
        if not self.v1:
            self.authenticate()
        return self.v1


class GoogleCloudLogging:
    """
    Manage the configuration of the Google Cloud Logging client
    """

    def __init__(self, credentials_path: str):
        """
        Initialize the Google Cloud Logging configuration
        """
        self.credentials_path = credentials_path
        self.client = None

    def authenticate(self):
        """
        Authenticate with Google Cloud Logging
        """
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path
        )

        # Create a logging client
        self.client = gcloud_logging.Client(credentials=credentials)

    def get_client(self):
        """
        Singleton method to get the Google Cloud Logging client
        """
        if not self.client:
            self.authenticate()
        return self.client
