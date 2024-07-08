import json

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


class LangchainJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (HumanMessage, AIMessage, ToolMessage)):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)