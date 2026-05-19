État d’avancement du projet:
création de quatres agents :Supervisor(agent central du système),Diagnostic Agent(responsable de l’interaction avec le patient), Physician Review Agent (Human-in-the-Loop), Report Agent(génére le rapport médical final).
tools:Patient Tool(questions médicales posées au patient),Care Recommendation Tool(génère une recommandation intermédiaire prudente)
MCP:get_emergency_level(estimer un niveau d’urgence à partir des symptômes du patient) POUR LE MOMENT le MCP est opérationnel mais pas encore intégré
API FastAPI: développé une API REST qui permet de (POST /consultation/start,POST /consultation/answer,POST /consultation/resume,GET /consultation/report)
Frontend Streamlitutilisé pour avoir une interface web interactive.
