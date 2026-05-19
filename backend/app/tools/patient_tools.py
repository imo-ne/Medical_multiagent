QUESTIONS = [
    "Depuis combien de temps avez-vous les symptômes ?",
    "Avez-vous de la fièvre ?",
    "Avez-vous des difficultés respiratoires ?",
    "Ressentez-vous de la fatigue ?",
    "Prenez-vous déjà un traitement ?"
]


def ask_patient(question_count: int):

    if question_count < len(QUESTIONS):
        return QUESTIONS[question_count]

    return None