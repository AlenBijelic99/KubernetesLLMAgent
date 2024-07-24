import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    The state passed between each node in the graph.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
