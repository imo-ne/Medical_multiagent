from typing import TypedDict, List, Optional


class MedicalState(TypedDict):

    messages: List[str]
    next: Optional[str]
    question_count: int
    patient_answers: List[str]
    current_question: str
    diagnostic_summary: str
    interim_care: str
    physician_treatment: str
    final_report: str