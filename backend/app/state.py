from typing import Annotated
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages

def update_count(current: int, new: int) -> int:
    if new is None:
        return current
    return new

class MedicalState(TypedDict):
    messages: Annotated[list, add_messages]
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    question_count: Annotated[int, update_count] 
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str