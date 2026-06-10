import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import create_event, create_run
from app.websocket.websocket import ConnectionManager


def test_run_agent_requires_auth(client: TestClient) -> None:
    response = client.post(f"{settings.API_V1_STR}/agent/run")
    assert response.status_code == 401


def test_get_runs_requires_auth(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/agent/runs")
    assert response.status_code == 401


def test_run_agent(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    monkeypatch,
) -> None:
    executed_runs: list[uuid.UUID] = []

    async def fake_run(
        _manager: ConnectionManager, _session: Session, run_id: uuid.UUID
    ) -> None:
        executed_runs.append(run_id)

    monkeypatch.setattr("app.api.routes.agent.run", fake_run)

    response = client.post(
        f"{settings.API_V1_STR}/agent/run", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Agent run finished successfully"}
    assert len(executed_runs) == 1


def test_run_agent_failure_returns_generic_error(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    monkeypatch,
) -> None:
    async def failing_run(
        _manager: ConnectionManager, _session: Session, _run_id: uuid.UUID
    ) -> None:
        raise RuntimeError("secret internal details")

    monkeypatch.setattr("app.api.routes.agent.run", failing_run)

    response = client.post(
        f"{settings.API_V1_STR}/agent/run", headers=superuser_token_headers
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Agent run failed"
    assert "secret" not in response.text


def test_get_runs(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    run = create_run(session=db, status="finished")

    response = client.get(
        f"{settings.API_V1_STR}/agent/runs", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert any(r["id"] == str(run.id) for r in content["data"])


def test_get_run_with_events(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    run = create_run(session=db, status="finished")
    event_one = create_event(
        session=db,
        run_id=run.id,
        event_data={"metric_analyser": {"messages": [{"type": "human"}]}},
    )
    event_two = create_event(
        session=db,
        run_id=run.id,
        event_data={"incident_reporter": {"messages": [{"type": "ai"}]}},
    )

    response = client.get(
        f"{settings.API_V1_STR}/agent/run/{run.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(run.id)
    assert [e["id"] for e in content["events"]] == [
        str(event_one.id),
        str(event_two.id),
    ]


def test_get_run_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/agent/run/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"
