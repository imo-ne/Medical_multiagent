from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.state import MedicalState
from app.nodes.physician_review import physician_review_node
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.report_agent import report_agent_node


workflow = StateGraph(MedicalState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("diagnostic_agent", diagnostic_agent_node)
workflow.add_node("report_agent", report_agent_node)
workflow.add_node("physician_review", physician_review_node)

workflow.set_entry_point("supervisor")


workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        "END": END
    }
)

workflow.add_edge("diagnostic_agent", "supervisor")
workflow.add_edge("report_agent", "supervisor")
workflow.add_edge("physician_review", "supervisor")
memory = MemorySaver()
graph = workflow.compile(
    checkpointer=memory
)