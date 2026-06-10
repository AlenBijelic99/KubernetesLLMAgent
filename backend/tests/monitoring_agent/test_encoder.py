import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.encoder.langchain_json_encoder import LangchainJSONEncoder


def test_encoder_serializes_messages() -> None:
    messages = [
        HumanMessage(content="check the cluster"),
        AIMessage(
            content="",
            name="metric_analyser",
            tool_calls=[
                {
                    "name": "get_pod_names",
                    "args": {"namespace": "default"},
                    "id": "call_1",
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(content="['pod-a']", name="get_pod_names", tool_call_id="call_1"),
    ]

    decoded = json.loads(json.dumps({"messages": messages}, cls=LangchainJSONEncoder))

    human, ai, tool = decoded["messages"]
    assert human["type"] == "human"
    assert human["content"] == "check the cluster"
    assert ai["type"] == "ai"
    assert ai["tool_calls"][0]["name"] == "get_pod_names"
    assert ai["tool_calls"][0]["args"] == {"namespace": "default"}
    assert tool["type"] == "tool"
    assert tool["tool_call_id"] == "call_1"
