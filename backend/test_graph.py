from app.graph import graph

from langgraph.types import Command


config = {
    "configurable": {
        "thread_id": "medical-thread-1"
    }
}


initial_state = {
    "messages": [],
    "next": None,
    "question_count": 0,
    "patient_answers": [],
    "current_question": "",
    "diagnostic_summary": "",
    "interim_care": "",
    "physician_treatment": "",
    "final_report": ""
}


result = graph.invoke(
    initial_state,
    config=config
)

print("\n=== INTERRUPTION ===\n")

print(result)


# reprise du graphe
resume_result = graph.invoke(
    Command(resume="Repos + suivi médical"),
    config=config
)

print("\n=== RAPPORT FINAL ===\n")

print(resume_result["final_report"])