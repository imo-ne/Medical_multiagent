from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing_extensions import Literal
from app.state import MedicalState

class Router(BaseModel):
    next_node: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]

def supervisor_node(state: MedicalState):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
    
    if state.get("question_count", 0) < 5:
        return {"next": "diagnostic_agent"}
    elif not state.get("physician_treatment"):
        return {"next": "physician_review"}
    elif not state.get("final_report"):
        return {"next": "report_agent"}
    else:
        return {"next": "FINISH"}