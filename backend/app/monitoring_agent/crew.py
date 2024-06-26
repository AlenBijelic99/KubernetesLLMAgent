import os
import yaml

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.monitoring_agent.tools.kubernetes_tool import get_pod_names, get_pod_logs, get_pod_yaml
from app.monitoring_agent.tools.prometheus_tool import execute_prometheus_query

load_dotenv()

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


@CrewBase
class MonitoringAssistantCrew():
    """A crew that assists with monitoring Kubernetes clusters."""
    agents_config_path = os.path.join(base_dir, 'config', 'agents.yaml')
    tasks_config_path = os.path.join(base_dir, 'config', 'tasks.yaml')

    def __init__(self) -> None:
        self.agents_config = load_yaml(self.agents_config_path)
        self.tasks_config = load_yaml(self.tasks_config_path)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
        self.get_pod_names = get_pod_names
        self.get_pod_logs = get_pod_logs
        self.get_pod_yaml = get_pod_yaml
        self.execute_prometheus_query = execute_prometheus_query
        self.agents = [
            self.metrics_analyser()
        ]

    @agent
    def metrics_analyser(self):
        return Agent(config=self.agents_config['metrics_analyser'], llm=self.llm,
                     tools=[self.get_pod_names, self.execute_prometheus_query])

    """
    @agent
    def diagnostic_expert(self):
        return Agent(config=self.agents_config['diagnostic_expert'], llm=self.llm)

    @agent
    def solution_expert(self):
        return Agent(config=self.agents_config['solution_expert'], llm=self.llm)

    @agent
    def incident_reporter(self):
        return Agent(config=self.agents_config['incident_reporter'], llm=self.llm)
    """

    @task
    def analyse_metric_task(self) -> Task:
        return Task(config=self.tasks_config['analyse_metric_task'], agent=self.metrics_analyser())

    @task
    def execute_query_task(self) -> Task:
        return Task(config=self.tasks_config['execute_query_task'], agent=self.metrics_analyser())

    """
    @task
    def diagnose_issue_task(self) -> Task:
        return Task(config=self.tasks_config['diagnose_issue_task'], agent=self.diagnostic_expert())

    @task
    def provide_solution_task(self) -> Task:
        return Task(config=self.tasks_config['provide_solution_task'], agent=self.solution_expert())

    @task
    def report_incident_task(self) -> Task:
        return Task(config=self.tasks_config['report_incident_task'], agent=self.incident_reporter())
    """

    @crew
    def crew(self) -> Crew:
        """Create a crew of agents and tasks."""
        return Crew(
            agents=self.agents,
            tasks=[
                self.analyse_metric_task()
            ],
            process=Process.sequential,
            verbose=2
        )
