from agents.state import ComplaintAgentState
from agents.llm import call_groq_json
from agents.prompts import RISK_ASSESSMENT_SYSTEM, RISK_ASSESSMENT_USER  # Import templates

def risk_assessment_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 3: Shared reasoning step evaluating full current complaint fields to calculate Severity, Suggested Action, Narrative, and Likely Root Cause."""
    fields = state.get("merged_fields", {}) or {}

    system_prompt = RISK_ASSESSMENT_SYSTEM.format()
    prompt = RISK_ASSESSMENT_USER.format(fields=fields)
    
    risk_res = call_groq_json(prompt, system_prompt)

    cleaned_risk = {
        "severity": str(risk_res.get("severity", "Major")),
        "suggested_next_action": str(risk_res.get("suggested_next_action", "Route to QA Investigation")),
        "initial_risk_assessment": str(risk_res.get("initial_risk_assessment", "Potential impact on finished product quality. Investigation initiated.")),
        "likely_root_cause": str(risk_res.get("likely_root_cause", "Possible primary packaging seal defect or environment exposure."))
    }

    state["risk_assessment"] = cleaned_risk

    # Enforce FDA 21 CFR Part 11 HITL: Critical or Major complaints require Pending QA Signoff
    has_product = bool(fields.get("product_name"))
    has_batch = bool(fields.get("batch_lot_number"))
    has_desc = bool(fields.get("complaint_description"))

    sev = cleaned_risk["severity"]
    if has_product and has_batch and has_desc:
        if sev in ["Critical", "Major"]:
            state["status"] = "Pending QA Signoff"
        else:
            state["status"] = "Approved"
    else:
        state["status"] = "In Progress"

    return state
