from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node

memory = MemorySaver()

builder = StateGraph(MedicalState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("diagnostic_agent", diagnostic_agent_node)
builder.add_node("physician_review", physician_review_node)
builder.add_node("report_agent", report_agent_node)


builder.add_edge(START, "supervisor")

def route_next(state: MedicalState):
    target = state.get("next")
    if target == "FINISH" or not target:
        return "__end__"
    return target

builder.add_conditional_edges(
    "supervisor",
    route_next,
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        "__end__": END
    }
)

builder.add_edge("diagnostic_agent", "supervisor")
builder.add_edge("physician_review", "supervisor")
builder.add_edge("report_agent", "supervisor")


graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["physician_review"] 
)