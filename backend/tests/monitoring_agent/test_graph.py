import asyncio
import json
from typing import Any

from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from sqlmodel import Session

from app.crud import create_run, get_run_events
from app.models import AgentRun
from app.monitoring_agent import main as agent_main
from app.monitoring_agent.tools import kubernetes_tool
from app.websocket.websocket import ConnectionManager


class FakeToolChatModel(GenericFakeChatModel):
    """Fake chat model that accepts (and ignores) tool binding."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "FakeToolChatModel":
        return self


def _patch_llm(monkeypatch, messages: list[AIMessage]) -> None:
    fake = FakeToolChatModel(messages=iter(messages))
    monkeypatch.setattr("app.monitoring_agent.agent_nodes.get_llm", lambda: fake)


def test_generate_graph_compiles(monkeypatch) -> None:
    _patch_llm(monkeypatch, [])
    graph = agent_main.generate_graph()
    assert sorted(graph.get_graph().nodes.keys()) == [
        "__end__",
        "__start__",
        "call_tool",
        "diagnostic",
        "incident_reporter",
        "metric_analyser",
        "solution",
    ]


def test_event_to_json_is_json_serializable() -> None:
    event = {
        "metric_analyser": {
            "messages": [AIMessage(content="all good", name="metric_analyser")],
            "sender": "metric_analyser",
        }
    }
    json_event = agent_main.event_to_json(event)
    serialized = json.dumps(json_event)
    assert "all good" in serialized
    assert json_event["metric_analyser"]["messages"][0]["type"] == "ai"


def test_mocked_agent_run_end_to_end(db: Session, monkeypatch) -> None:
    """Full agent run with a scripted LLM and stubbed Kubernetes tool.

    Exercises the graph routing (tool call -> back to the agent -> finish),
    event serialization, persistence and websocket broadcasting without any
    LLM credentials or cluster.
    """
    scripted_messages = [
        # metric_analyser asks for the pod names
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "get_pod_names",
                    "args": {"namespace": "default"},
                    "id": "call_1",
                    "type": "tool_call",
                }
            ],
        ),
        # metric_analyser concludes after seeing the tool result
        AIMessage(content="All metrics look fine. FINISHED"),
        # incident_reporter writes the final report
        AIMessage(content="Incident report: no issues found."),
    ]
    _patch_llm(monkeypatch, scripted_messages)
    monkeypatch.setattr(
        kubernetes_tool.get_pod_names,
        "func",
        lambda namespace: ["pod-a", "pod-b"],
    )

    run_row = create_run(session=db)
    manager = ConnectionManager()
    broadcast: list[Any] = []

    async def record_broadcast(message: Any) -> None:
        broadcast.append(message)

    monkeypatch.setattr(manager, "send_json", record_broadcast)

    asyncio.run(agent_main.run(manager, db, run_row.id))

    db.refresh(run_row)
    assert run_row.status == "finished"

    events = [
        event.event_data for event in get_run_events(session=db, run_id=run_row.id)
    ]
    assert len(events) == len(broadcast) + 1  # the input event is not broadcast

    # All persisted events are JSON serializable as stored
    json.dumps(events)

    nodes_seen = [next(iter(event.keys())) for event in events]
    assert nodes_seen[0] == "metric_analyser"
    assert "call_tool" in nodes_seen
    assert nodes_seen[-1] == "incident_reporter"

    tool_event = events[nodes_seen.index("call_tool")]
    tool_message = tool_event["call_tool"]["messages"][0]
    assert tool_message["type"] == "tool"
    assert "pod-a" in tool_message["content"]

    report_message = events[-1]["incident_reporter"]["messages"][0]
    assert report_message["type"] == "ai"
    assert "Incident report" in report_message["content"]
    assert report_message["name"] == "incident_reporter"


def test_failed_run_is_marked_failed(db: Session, monkeypatch) -> None:
    def broken_graph() -> Any:
        raise RuntimeError("graph construction failed")

    monkeypatch.setattr(agent_main, "generate_graph", broken_graph)

    run_row = create_run(session=db)
    manager = ConnectionManager()

    try:
        asyncio.run(agent_main.run(manager, db, run_row.id))
    except RuntimeError:
        pass
    else:
        raise AssertionError("run() should re-raise the failure")

    refreshed = db.get(AgentRun, run_row.id)
    assert refreshed is not None
    assert refreshed.status == "failed"
    events = get_run_events(session=db, run_id=run_row.id)
    assert any(e.event_data.get("type") == "Error" for e in events)
    # The websocket replay buffer is cleared after the run
    assert manager.current_run_json == []
