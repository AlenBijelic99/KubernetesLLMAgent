import inspect
from typing import Dict, Any


def extract_tool_metadata(tool_func) -> Dict[str, Any]:
    """Extracts the metadata for a tool function."""
    signature = inspect.signature(tool_func)
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for name, param in signature.parameters.items():
        param_type = param.annotation

        if name == "callbacks":
            break

        if param.default == param.empty:
            parameters["required"].append(name)

        if param_type == str:
            parameters["properties"][name] = {"type": "string"}
        elif param_type == int:
            parameters["properties"][name] = {"type": "integer"}
        elif param_type == bool:
            parameters["properties"][name] = {"type": "boolean"}
        else:
            parameters["properties"][name] = {"type": "string"}  # Default to string if type is unknown

    return {
        "name": tool_func.name,
        "description": tool_func.description,
        "parameters": parameters
    }
