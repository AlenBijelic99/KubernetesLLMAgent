from google.auth.transport.requests import Request
from google.cloud import logging as gcloud_logging
from google.oauth2 import service_account
from kubernetes import client

from app.core.config import settings


class KubernetesConfig:
    """
    Manage the configuration of the Kubernetes client
    """

    def __init__(
        self, kube_host: str | None, credentials_path: str | None, scopes: list[str]
    ):
        """
        Initialize the Kubernetes configuration
        """
        self.kube_host = kube_host
        self.credentials_path = credentials_path
        self.scopes = scopes
        self.configuration: client.Configuration | None = None
        self.v1: client.CoreV1Api | None = None

    def authenticate(self) -> None:
        """
        Authenticate with the Kubernetes cluster
        """
        if not self.kube_host or not self.credentials_path:
            raise ValueError(
                "Kubernetes access is not configured: set KUBE_HOST and "
                "GOOGLE_APPLICATION_CREDENTIALS_FILE"
            )

        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
            self.credentials_path, scopes=self.scopes
        )

        # Get access token
        credentials.refresh(Request())

        # Configure the Kubernetes client. TLS verification is enabled by
        # default; for clusters with a private CA (e.g. GKE), point
        # K8S_SSL_CA_CERT to the cluster CA certificate file.
        self.configuration = client.Configuration()
        self.configuration.host = self.kube_host
        self.configuration.verify_ssl = settings.K8S_VERIFY_SSL
        if settings.K8S_SSL_CA_CERT:
            self.configuration.ssl_ca_cert = settings.K8S_SSL_CA_CERT
        self.configuration.api_key = {"authorization": "Bearer " + credentials.token}
        client.Configuration.set_default(self.configuration)
        self.v1 = client.CoreV1Api()

    def get_client(self) -> client.CoreV1Api:
        """
        Singleton method to get the Kubernetes client
        """
        if not self.v1:
            self.authenticate()
        assert self.v1 is not None
        return self.v1


class GoogleCloudLogging:
    """
    Manage the configuration of the Google Cloud Logging client
    """

    def __init__(self, credentials_path: str | None):
        """
        Initialize the Google Cloud Logging configuration
        """
        self.credentials_path = credentials_path
        self.client: gcloud_logging.Client | None = None

    def authenticate(self) -> None:
        """
        Authenticate with Google Cloud Logging
        """
        if not self.credentials_path:
            raise ValueError(
                "Google Cloud Logging is not configured: set "
                "GOOGLE_APPLICATION_CREDENTIALS_FILE"
            )

        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
            self.credentials_path
        )

        # Create a logging client
        self.client = gcloud_logging.Client(  # type: ignore[no-untyped-call]
            credentials=credentials
        )

    def get_client(self) -> gcloud_logging.Client:
        """
        Singleton method to get the Google Cloud Logging client
        """
        if not self.client:
            self.authenticate()
        assert self.client is not None
        return self.client
