import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


class LangchainJSONEncoder(json.JSONEncoder):
    """Serializes LangChain message objects to plain dictionaries."""

    def default(self, o: Any) -> Any:
        if isinstance(o, HumanMessage | AIMessage | ToolMessage):
            return o.model_dump()
        return json.JSONEncoder.default(self, o)
