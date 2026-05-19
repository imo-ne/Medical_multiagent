from fastapi import FastAPI

from langgraph.types import Command

from app.graph import graph


app = FastAPI(
    title="Medical Multi Agent API"
)


@app.post("/consultation/start")
def start_consultation():

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

    return result

@app.post("/consultation/answer")
def answer_question(answer: str):

    config = {
        "configurable": {
            "thread_id": "medical-thread-1"
        }
    }

    result = graph.invoke(
        Command(resume=answer),
        config=config
    )

    return result

@app.post("/consultation/resume")
def resume_consultation(treatment: str):

    config = {
        "configurable": {
            "thread_id": "medical-thread-1"
        }
    }

    result = graph.invoke(
        Command(resume=treatment),
        config=config
    )

    return result


@app.get("/consultation/report")
def get_report():

    config = {
        "configurable": {
            "thread_id": "medical-thread-1"
        }
    }

    state = graph.get_state(config)

    return {
        "final_report": state.values.get(
            "final_report"
        )
    }