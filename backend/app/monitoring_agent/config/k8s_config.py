import logging
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from kubernetes import client


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
