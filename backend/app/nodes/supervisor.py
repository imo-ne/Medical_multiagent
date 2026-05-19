def supervisor_node(state):

    if not state.get("diagnostic_summary"):

        next_step = "diagnostic_agent"
    elif not state.get("physician_treatment"):

        next_step = "physician_review"
    elif not state.get("final_report"):

        next_step = "report_agent"
    else:

        next_step = "END"
    return {
        **state,
        "next": next_step
    }