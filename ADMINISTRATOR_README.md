# Kubernetes AI Agent - Administrator Documentation

## Introduction

The Kubernetes AI Agent is a tool that helps you monitor and manage your Kubernetes cluster. It uses AI reasoning to analyze the state of your cluster and provides suggestions on how to resolve issues.

This guide provides information on how to set up the Kubernetes AI Agent to monitor your Kubernetes cluster.

## Prerequisites

- A Kubernetes cluster deployed on Google Kubernetes Engine.
- A Kubeconfig file to authenticate with the Kubernetes cluster.
- An application running on the cluster that exposes Prometheus metrics.
- A Prometheus server with a public IP address to scrape the metrics.
- Activated Google Kubernetes Engine API and Google Logging API
- A Google Service Account with Kubernetes Engine Service Agent, Logs Viewer and Private Logs Viewer roles.
- (Optionally) Helm installed on your machine to deploy Prometheus or any other charts.
- (Testing) For testing purpose you can use Chaos Mesh to simulate issues on the cluster.

### Connect Kubectl to the Google Kubernetes Engine

To connect `kubectl` to the Google Kubernetes Engine, run the following command:

```bash
gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE --project=PROJECT_ID
```

Replace `CLUSTER_NAME`, `ZONE`, and `PROJECT_ID` with your cluster details. You may need to authenticate with your Google account if it is not already done [here](https://cloud.google.com/sdk/gcloud/reference/auth/login).

### Deploy Prometheus

To deploy Prometheus on the Kubernetes cluster, you can use the provided `values.yaml` file. Modify it to add your application and to suits your need. Run the following command to deploy it with Helm:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n apm -f values.yaml
```

To access Prometheus, you can use port forwarding and access with your browser at `http://localhost:9090`.

```bash
kubectl port-forward -n apm prometheus-prometheus-kube-prometheus-prometheus-0 9090
```

Or you can modify the type of the service to `LoadBalancer` and access it with the public IP address.

```bash
kubectl patch svc prometheus-operated -n apm --type='json' -p='[{"op": "replace", "path": "/spec/type", "value": "LoadBalancer"}]'
```

To get the public IP address, run the following command:

```bash
kubectl get svc prometheus-operated -n apm
```

To uninstall Prometheus, run the following command:

```bash
helm uninstall prometheus -n apm
```

### Deploy Chaos Mesh

To deploy Chaos Mesh on the Kubernetes cluster, you can use the provided Helm chart. Run the following commands to deploy it with Helm:

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create ns chaos-mesh
helm install chaos-mesh chaos-mesh/chaos-mesh -n=chaos-mesh --set chaosDaemon.runtime=containerd --set chaosDaemon.socketPath=/run/containerd/containerd.sock --version 2.6.3
```

To access the Chaos Dashboard, you can use port forwarding and access with your browser at `http://localhost:2333`.

```bash
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
```

You will see instructions to create a token to access the dashboard.

## Installation

### Step 1: Clone the repository

Clone the repository to your local machine.

```bash
git clone git@github.com:AlenBijelic99/TBAgentApp.git
```

### Step 2: Set up the environment

Create a duplicate of the `.env.example` file and name it `.env`. Fill in the required environment variables.

You may change the default `SECRET_KEY` and `FIRST_SUPERUSER_PASSWORD` values.

The mandatory values are as follows:

```bash
DOMAIN=

ENVIRONMENT=

PROJECT_NAME=
STACK_NAME=

BACKEND_CORS_ORIGINS= # Add the frontend URL here (comma-separated)
SECRET_KEY=
FIRST_SUPERUSER=
FIRST_SUPERUSER_PASSWORD=

POSTGRES_SERVER=
POSTGRES_PORT=5432
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

DOCKER_IMAGE_BACKEND=backend
DOCKER_IMAGE_FRONTEND=frontend

TIMEZONE=Europe/Zurich # Set your timezone

NAMESPACES=default # Comma-separated list of namespaces to monitor
KUBE_HOST=
KUBE_CONFIG_DIR=~/.kube
GOOGLE_APPLICATION_CREDENTIALS_FILE=
K8S_VERIFY_SSL=True
K8S_SSL_CA_CERT=

PROMETHEUS_URL=
PROMETHEUS_VERIFY_SSL=True

LANGCHAIN_TRACING_V2=false  # Set to true to use LangSmith for tracing
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=  # https://smith.langchain.com/settings
OPENAI_API_KEY=     # https://platform.openai.com/account/api-keys
LLM_MODEL=gpt-4o # gpt-* models use OpenAI; any other name (e.g. llama3.1) is served by Ollama
OLLAMA_BASE_URL="http://host.docker.internal:11434" # Only used when LLM_MODEL is not a gpt-* model
```

Note: unlike the original version of this project, user self-registration is
always enabled by the underlying template (the `USERS_OPEN_REGISTRATION`
variable no longer exists). Remove the `/signup` route in the frontend if you
do not want open registration.

`PROMETHEUS_URL` is the URL of the Prometheus server that scrapes the metrics from the Kubernetes cluster. It generally looks like `http://prometheus-ip:9090`.

`PROMETHEUS_VERIFY_SSL` controls TLS certificate verification when connecting to Prometheus. Keep it `True` in production; only set it to `False` for a local or test Prometheus without a valid certificate.

`KUBE_HOST` is the URL of the Kubernetes API server (e.g. `https://<cluster-endpoint>`). It can be found in the cluster details of the Google Cloud Platform console.

`KUBE_CONFIG_DIR` is the host directory that is mounted read-only into the backend container at `/app/.kube`. By default, on Windows it is `C:\Users\username\.kube` and on Linux it is `~/.kube`. Place the Google Service Account JSON file in this directory.

`GOOGLE_APPLICATION_CREDENTIALS_FILE` is the path to the Google Service Account JSON file as seen from inside the backend container, e.g. `/app/.kube/service-account.json`. You can download the file from the Google Cloud Platform console.

`K8S_VERIFY_SSL` controls TLS certificate verification towards the Kubernetes API and is enabled by default. GKE clusters use a private cluster CA, so to connect with verification enabled, download the cluster CA certificate (cluster details > security > cluster CA certificate, or `gcloud container clusters describe CLUSTER_NAME --format="value(masterAuth.clusterCaCertificate)" | base64 -d`), place it in `KUBE_CONFIG_DIR`, and set `K8S_SSL_CA_CERT=/app/.kube/cluster-ca.pem`.

By setting up emails environment variables, you can enable email based password recovery.

### Step 3: Build and start the Docker containers

To build and start the Docker containers, run the following command:

```bash
docker compose up -d
```

The `compose.yml` files are provided by the [Full Stack FastAPI template](https://github.com/fastapi/full-stack-fastapi-template).

If everything is set up correctly, you should be able to access the OpenAPI documentation at `http://localhost:8000/docs` and the frontend at `http://localhost:5173`.

If you encounter any issues, check the backend logs for any configuration errors.

### Step 4: Set up the namespace to monitor

The agent monitors the namespaces listed in the `NAMESPACES` environment variable in `.env` (comma-separated):

```bash
NAMESPACES=testing-apps,default
```

## LangSmith

By enabling LangSmith for tracing, you can use the LangSmith service to trace the agent's reasoning process. You can sign up for a free account at [LangSmith](https://smith.langchain.com/).

You will be able to see all the reasoning steps and the generated AI messages as well as the number of tokens used and the price of the reasoning process.

## License

The Kubernetes AI Agent is licensed under the terms of the MIT license.