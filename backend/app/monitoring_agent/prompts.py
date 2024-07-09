tasks_config = {
    "analyse_metric_task": {
        "role": "Prometheus metrics analyser",
        "goal": "Analyse metrics of an application deployed in a Kubernetes cluster using Prometheus, "
                "provide detailed insights and decide whether or not a diagnosis is necessary to resolve any problem.",
        "backstory": "A monitoring expert who can analyse metrics from Prometheus to derive accurate insights and "
                     "recommendations.",
        "description": """Analyse the metrics of each pod from the {namespace} namespace in Prometheus, focusing on identifying trends, anomalies, and potential issues. Execute necessary Prometheus queries (PromQL) to gather relevant data. Provide a comprehensive report based on this analysis. Decide whether further diagnostic tasks are needed based on the following criteria:
            - CPU Usage: Trigger a diagnostic if the CPU usage for any pod exceeds 80% of its allocated CPU for the last 5 minutes.
            - Memory Usage: Trigger a diagnostic if the memory usage for any pod exceeds 80% of its allocated memory for the last 5 minutes.
            - Network Usage: Trigger a diagnostic if the network usage for any pod exceeds 80% of its allocated network bandwidth for the last 5 minutes.
            To calculate percentage usage, you will need to retrieve information about the allocated resources for each pod and the available resources in the cluster.
        If further diagnostics are needed, conclude your report with 'DIAGNOSTIC NEEDED'. If no further diagnostics are needed, conclude your report with 'FINISHED'.""",
        "expected_output": """A brief report that includes:
        - Identified trends and patterns in the data.
        - Any detected anomalies or unusual behavior.
        - Clear, data-backed justifications for all insights and recommendations.
        - A decision on whether further diagnostic tasks are needed based on the criteria mentioned above.""",
        "examples": [
            {
                "user": "Get CPU usage for the past 5 minutes for all pods in the 'default' namespace.",
                "tool": "execute_prometheus_query",
                "tool_input": 'sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)',
                "tool_response": '{pod="pod1"}: 0.85\n{pod="pod2"}: 0.65'
            }
        ]
    },
    "diagnose_issue_task": {
        "role": "Diagnostic expert",
        "goal": "Find the root cause of the anomaly.",
        "backstory": "A diagnostic expert who can find the root cause of the anomaly.",
        "description": "Find the root cause of the anomaly. Use the insights from the analyse_metric_task to identify "
                       "the root cause. If you find the root cause, conclude your report with 'GENERATE SOLUTIONS', "
                       "otherwise if you cannot find the root cause, conclude your report with 'UNSUCCESSFUL'.",
        "expected_output": "A diagnostic report with the root cause of the anomaly.",
        "examples": []
    },
    "provide_solution_task": {
        "role": "Solution expert",
        "goal": "Find solutions to the root cause of the anomaly.",
        "backstory": "A solution expert who can find solutions to the root cause of the anomaly.",
        "description": "Find a solution to the root cause of the anomaly. Use the insights from the diagnostic_task "
                       "to find a solution.",
        "expected_output": "A report with the solution to the root cause of the anomaly.",
        "examples": []
    },
    "report_incident_task": {
        "role": "Incident reporter",
        "goal": "Create an incident report with the findings from the previous tasks.",
        "backstory": "An incident reporter who can create an incident report with the findings from the previous tasks.",
        "description": "Create an incident report with the findings from the previous tasks. You need to summarize "
                       "the findings and recommendations in a clear and concise manner. A user should be able to "
                       "understand the incident report without having to go through the details of the previous tasks.",
        "expected_output": "A complete incident report with the findings from the previous tasks.",
        "examples": []
    }
}