import os
from dotenv import load_dotenv
load_dotenv()
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from app.graph import graph

app = FastAPI(
    title="Système Multi-Agents Médical API",
    description="API FastAPI exposant le workflow d'orientation clinique LangGraph",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConsultationStartRequest(BaseModel):
    patient_case: str  

class ConsultationResumeRequest(BaseModel):
    thread_id: str
    physician_treatment: str

class PatientAnswerRequest(BaseModel):
    thread_id: str
    answer: str


from langgraph.types import Command

@app.post("/consultation/start", summary="Démarrer une nouvelle consultation")
async def start_consultation(request: ConsultationStartRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "messages": [],
            "question_count": 0
        }
        
        
        await graph.ainvoke(initial_state, config=config)
        
        current_state = await graph.aget_state(config)
        
        current_question = ""
        if current_state.tasks:
            current_question = current_state.tasks[0].interrupts[0].value

        return {
            "thread_id": thread_id,
            "status": "running",
            "state": {
                **current_state.values,
                "current_question": current_question # On la passe explicitement au front
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur au démarrage : {str(e)}")


@app.post("/consultation/answer", summary="Soumettre la réponse du patient")
async def submit_patient_answer(request: PatientAnswerRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    try:
        await graph.ainvoke(Command(resume=request.answer), config=config)
        
        current_state = await graph.aget_state(config)
        current_question = ""
        if current_state.tasks and current_state.tasks[0].interrupts:
            current_question = current_state.tasks[0].interrupts[0].value
            
        return {
            "state": {
                **current_state.values,
                "current_question": current_question
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la réponse : {str(e)}")

@app.get("/consultation/{thread_id}", summary="Récupérer l'état actuel de la consultation")
async def get_consultation_status(thread_id: str):
    """
    Permet de lire l'état actuel de la consultation (les messages échangés, le compteur de questions, etc.).
    """
    config = {"configurable": {"thread_id": thread_id}}
    current_state = await graph.aget_state(config)
    
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")
        
    return {
        "thread_id": thread_id,
        "next_step": current_state.next, 
        "values": current_state.values
    }


@app.post("/consultation/resume", summary="Reprendre le workflow après validation du médecin (Human-in-the-Loop)")
async def resume_consultation(request: ConsultationResumeRequest):
    """
    Reçoit la décision du médecin, met à jour l'état partagé et lève l'interruption 
    pour permettre au Report Agent de générer le compte rendu final.
    """
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        await graph.aupdate_state(
            config,
            {"physician_treatment": request.physician_treatment},
            as_node="physician_review" 
        )
        
        await graph.ainvoke(None, config=config)
        
        final_state = await graph.aget_state(config)
        
        return {
            "thread_id": request.thread_id,
            "status": "completed",
            "values": final_state.values
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la reprise du workflow : {str(e)}")


@app.get("/consultation/{thread_id}/report", summary="Récupérer uniquement le rapport final")
async def get_final_report(thread_id: str):
    """
    Retourne le rapport structuré généré par le Report Agent à la fin du cycle.
    """
    config = {"configurable": {"thread_id": thread_id}}
    current_state = await graph.aget_state(config)
    
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")
        
    final_report = current_state.values.get("final_report")
    if not final_report:
        raise HTTPException(status_code=400, detail="Le rapport final n'a pas encore été généré. Attente de la validation du médecin.")
        
    return {
        "thread_id": thread_id,
        "final_report": final_report
    }