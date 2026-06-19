# 🏥 Système Multi-Agents d'Orientation Clinique Dynamique

## 1. Introduction & Objectifs

L'intégration des grands modèles de langage (LLM) dans le domaine de la santé connaît une expansion sans précédent. Cependant, leur utilisation en milieu clinique se heurte à des barrières critiques : manque de contrôle sur le flux de discussion, risques d'hallucinations et absence de supervision médicale directe. Un chatbot médical classique a tendance à adopter une posture passive ou linéaire, posant trop de questions simultanément ou s'égarant du protocole clinique de base.

### 1.1 Problématique
Comment concevoir une application d'intelligence artificielle capable de mener un interrogatoire médical strict, adaptatif et sécurisé, tout en garantissant qu'aucune décision finale ne soit prise sans l'avis d'un professionnel de santé ?

### 1.2 Objectifs du projet
Ce projet vise à développer une architecture logicielle robuste répondant aux exigences suivantes :
* **Mener un pré-interrogatoire standardisé :** Poser exactement 5 questions dynamiques basées sur les réponses progressives du patient.
* **Découpler le cycle de vie des agents :** Permettre des pauses d'exécution asynchrones adaptées aux contraintes d'une architecture Web.
* **Garantir la sécurité (Human-in-the-Loop) :** Un médecin valide, modifie et signe un compte-rendu officiel avant toute clôture de dossier.

---

## 2. Architecture Technique & Choix Technologiques

Le système repose sur une architecture découplée (Client/Serveur) permettant une séparation stricte des responsabilités. 

* **Frontend (Interface Utilisateur) :** Développé avec **Streamlit**. Il offre une interface web réactive et gère l'affichage dynamique par écrans applicatifs.
* **Backend (API REST) :** Conçu avec **FastAPI**, fournissant des endpoints asynchrones hautement performants pour initialiser le graphe, injecter les réponses et reprendre le flux de discussion.
* **Orchestration Multi-Agents :** Propulsé par **LangGraph** (écosystème LangChain), choisi pour sa capacité à modéliser des workflows cycliques et des architectures d'agents sous forme de graphes d'états déterministes.
* **Moteur LLM :** **Llama 3.3 (70B Versatile)** hébergé sur l'infrastructure d'inférence ultra-rapide de **Groq**, garantissant des temps de réponse inférieurs à la seconde.

| Composant | Technologie Choisie | Alternative Évaluée | Justification du Choix |
| :--- | :--- | :--- | :--- |
| **Orchestration** | LangGraph | Autogen / CrewAI | Meilleur contrôle sur les transitions logiques et la persistance native |
| **Moteur LLM** | Llama 3.3 70B (Groq) | OpenAI GPT-4o | Clé d'API Groq gratuite, infrastructure d'inférence ultra-rapide (<1s) |
| **Backend API** | FastAPI | Flask / Django | Support natif de l'asynchronisme (`async/await`) requis par LangGraph |
| **Interface** | Streamlit | React.js / Vue.js | Prototypage rapide en Python pur, idéal pour les démonstrations |

---

## 3. Modélisation du Graphe d'États (`MedicalState`)

Le socle du système repose sur un dictionnaire d'état typé et persistant qui transite à travers tous les nœuds du réseau :
* `messages` : Historique complet des interactions enrichi par un réducteur d'ajout (`add_messages`).
* `question_count` : Compteur entier strict, supervisé par une fonction de réduction personnalisée pour éviter les conflits d'écrasement lors des requêtes REST concurrentes.
* `diagnostic_summary` et `interim_care` : Mémoire tampon stockant la synthèse clinique générée à la fin du cycle d'interrogatoire.
* `physician_treatment` : Chaîne de caractères capturant l'avis final du médecin humain.

### 3.1 Cartographie des Nœuds (Agents)
Le graphe est articulé autour de 4 nœuds fonctionnels majeurs :
* **Le Superviseur (`supervisor_node`) :** Point de routage algorithmique évaluant le compteur `question_count` pour aiguiller dynamiquement le flux.
* **L'Agent de Diagnostic (`diagnostic_agent_node`) :** Cerveau conversationnel chargé d'analyser l'historique global pour formuler la question suivante.
* **La Revue Médicale (`physician_review_node`) :** Point de blocage logique protégeant l'accès aux étapes d'écriture de rapports.
* **L'Agent de Rapport (`report_agent_node`) :** Compilateur final chargé de formaliser le document de sortie au format standard de l'industrie médicale.

---

## 4. Focus Backend : La Puissance de FastAPI

FastAPI a été sélectionné comme framework backend principal pour sa gestion native et asynchrone des requêtes, un prérequis fondamental pour orchestrer les agents de LangGraph sans bloquer le thread principal du serveur.
<img width="959" height="436" alt="FastApiF" src="https://github.com/user-attachments/assets/bd8321c0-96ef-46dd-81a8-7a61b825329b" />

### 4.1 Caractéristiques Clés Implémentées :
* **Gestion Asynchrone Native (`async/await`) :** Permet de paralléliser les appels d'API vers les LLM (Groq) et de gérer les interactions avec le moteur de persistance de LangGraph de manière fluide.
* **Validation des Données via Pydantic :** Sécurise les payloads entrants (`ConsultationStartRequest`, `PatientAnswerRequest`) en garantissant le typage strict des données échangées entre le frontend Streamlit et le backend.
* **Génération Automatique de la Documentation (Swagger UI) :** Facilite le test des points de terminaison REST en fournissant une interface interactive accessible directement sur `/docs`.

---

## 5. Parcours Utilisateur & Validation Clinique Pas-à-Pas

L'expérience utilisateur au sein de l'application est découpée en trois phases distinctes, assurant une transition fluide de la collecte d'informations jusqu'au diagnostic final contrôlé.
[Écran 1: Motif Initial] ──> [Écran 2: Cycle des 5 Questions] ──> [Écran 3: Espace Médecin & Rapport]
### 5.1 Écran 1 : Initialisation du Cas Patient
Le patient accède à l'interface et saisit son motif de consultation initial (ex: *"J'ai une forte fièvre et des maux de tête depuis hier soir"*). Dès la validation, le frontend Streamlit communique avec l'endpoint `/consultation/start` de FastAPI, instancie un `thread_id` unique pour la session et initialise le `MedicalState` avec un compteur de questions fixé à zéro.

### 5.2 Écran 2 : Interrogatoire Dynamique Temporisé
Pour rompre avec la linéarité habituelle des LLM, cette phase force un flux pas-à-pas :
* L'interface affiche une barre de progression évolutive ($1/5$ à $5/5$).
* Le `Diagnostic Agent` formule une question clinique ciblée à la fois, puis le graphe se fige grâce au mécanisme d'interruption contrôlée.
* L'utilisateur saisit sa réponse au sein d'un composant de formulaire bloquant (`with st.form`). Ce choix UX empêche les rafraîchissements parasites de Streamlit et suspend l'exécution du graphe tant que l'utilisateur n'a pas cliqué sur le bouton de soumission.
* Une fois validée, la réponse est injectée dans le backend, le compteur s'incrémente et la question suivante est générée.

### 5.3 Écran 3 : Espace de Validation Médicale et Clôture
Une fois le cap des 5 questions atteint, l'interface bascule automatiquement sur l'espace praticien. L'accès direct au rapport final est verrouillé. 
* Le médecin consulte d'abord la **synthèse clinique préliminaire** rédigée par l'IA ainsi que les conseils d'orientation automatiques.
* Le médecin saisit ensuite ses propres directives (prescriptions, examens complémentaires, posologies) au sein d'une zone dédiée.
* À la validation, le `Report Agent` fusionne l'historique de l'IA et l'ordonnance officielle du professionnel pour éditer le **Compte-Rendu Médical Final Officiel** au format Markdown, prêt à être exporté.

---

## 6. Visualisation & Débogage : LangGraph Studio

Pour valider l'intégrité de notre architecture multi-agents et suivre le cycle de vie du `MedicalState` en temps réel, nous avons intégré **LangGraph Studio** au cycle de développement.

### 6.1 Avantages Apportés au Projet :
* **Visualisation Graphique du Workflow :** Permet de cartographier visuellement les nœuds (`supervisor`, `diagnostic_agent`, etc.) et de s'assurer de l'exactitude des arêtes conditionnelles (`conditional_edges`).
* <img width="325" height="111" alt="langGraph_Studio" src="https://github.com/user-attachments/assets/9453d8a9-fd57-49ab-9338-cd0a1a6046a6" />

* **Inspection de l'État en Direct (State Inspection) :** Offre la possibilité de surveiller l'évolution des variables à chaque étape, validant ainsi que le compteur `question_count` s'incrémente correctement sans être écrasé à l'étape supérieure.
* **Gestion des Points d'Arrêt (Time-Travel Debugging) :** Permet de rejouer des nœuds spécifiques ou de modifier manuellement la réponse d'un patient à l'étape $N$ pour observer le comportement de réadaptation de l'agent au cours des étapes suivantes.

---

## 7. Conclusion

Ce projet démontre l'efficacité des architectures multi-agents pour standardiser et sécuriser des processus complexes et sensibles comme l'orientation médicale. En associant la puissance générative de Llama 3.3 à la rigueur structurelle de LangGraph et à la performance de FastAPI, nous avons conçu un système conversationnel fiable et entièrement supervisé par l'humain (*Human-in-the-Loop*).
