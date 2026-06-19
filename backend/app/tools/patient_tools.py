from langchain_core.tools import tool
from app.state import MedicalState

@tool
def ask_patient_tool(question: str):
    """
    Utilisez cet outil pour poser une question spécifique au patient 
    lorsque vous avez besoin de clarifications sur ses symptômes.
    """
    return f"Question posée au patient : {question}"