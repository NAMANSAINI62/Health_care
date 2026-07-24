from agents.state import ComplaintAgentState
from agents.llm import call_groq_json

def risk_assessment_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 3: Shared reasoning step evaluating full current complaint fields to calculate Severity, Suggested Action, Narrative, and Likely Root Cause."""
    fields = state.get("merged_fields", {}) or {}

    system_prompt = (
        "You are a Senior Pharmaceutical Quality Assurance & Regulatory Risk Assessor.\n"
        "Evaluate the provided complaint details and perform a formal QMS Risk Assessment.\n\n"
        "Calculate the following keys:\n"
        "1. severity: Must be ONE of ['Minor', 'Major', 'Critical']. (Critical = potential patient harm/contamination/sterility failure; Major = dosage error/packaging defect/discoloration; Minor = minor label/cosmetic).\n"
        "2. suggested_next_action: Concise QMS action item (e.g. 'Route to QA Investigation & Issue Batch Hold Notice').\n"
        "3. initial_risk_assessment: 2-3 sentence technical risk evaluation summary.\n"
        "4. likely_root_cause: (Bonus Feature) Technical root cause hypothesis based on product, defect type, and packaging (e.g. 'Possible primary packaging seal failure leading to moisture ingress and capsule shell oxidation').\n\n"
        "Respond strictly with JSON format: {\"severity\": \"...\", \"suggested_next_action\": \"...\", \"initial_risk_assessment\": \"...\", \"likely_root_cause\": \"...\"}"
    )

    prompt = f"Complaint Form Details:\n{fields}"
    risk_res = call_groq_json(prompt, system_prompt)

    cleaned_risk = {
        "severity": str(risk_res.get("severity", "Major")),
        "suggested_next_action": str(risk_res.get("suggested_next_action", "Route to QA Investigation")),
        "initial_risk_assessment": str(risk_res.get("initial_risk_assessment", "Potential impact on finished product quality. Investigation initiated.")),
        "likely_root_cause": str(risk_res.get("likely_root_cause", "Possible primary packaging seal defect or environment exposure."))
    }

    state["risk_assessment"] = cleaned_risk

    # Automatically set status based on completeness
    has_product = bool(fields.get("product_name"))
    has_batch = bool(fields.get("batch_lot_number"))
    has_desc = bool(fields.get("complaint_description"))

    if has_product and has_batch and has_desc:
        state["status"] = "Ready to Commit"
    else:
        state["status"] = "Pending Triage"

    return state
