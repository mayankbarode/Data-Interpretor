from typing import TypedDict, Annotated, List, Union
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    file_path: str
    session_id: str  # Session ID for user isolation
    df_head: str
    analysis_code: str
    analysis_output: str
    image_path: str
    plotly_html: List  # List of Plotly figure HTML strings with insights
    error: str  # Track execution errors
    retry_count: int  # Track number of retries
