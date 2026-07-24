from agents.state import ComplaintAgentState
from agents.llm import call_groq_json

def log_complaint_tool_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 2A: Extracts and intelligently infers ALL 12 complaint fields from user complaint text."""
    user_msg = state.get("user_message", "")

    system_prompt = (
        "You are an expert pharmaceutical Quality Assurance AI Assistant.\n"
        "Extract and intelligently infer ALL 12 fields from the user's complaint message into a JSON object:\n"
        "- complaint_source (e.g. Pharmacy, Hospital, Email, Distributor, Patient)\n"
        "- customer_name (e.g. Apollo Pharmacy, CVS, MedPlus, John Doe)\n"
        "- product_name (e.g. Amoxicillin Capsules, Paracetamol Injection, Metformin 500mg)\n"
        "- product_strength (e.g. 500mg, 10 mg/mL, 250mg)\n"
        "- batch_lot_number (e.g. BMX-240602, CHG-260712A, LOT-9911)\n"
        "- manufacturing_date (e.g. Jan 2026, 2026-01-15 — infer standard Mfg date if missing)\n"
        "- expiry_date (e.g. Jan 2028, 2028-01-15 — infer standard 2-year Expiry date if missing)\n"
        "- affected_quantity (e.g. 48 capsules, 50 vials, 100 tablets)\n"
        "- complaint_category (e.g. Discoloration, Packaging Defect, Contamination, Labeling Error)\n"
        "- complaint_description (Detailed complaint narrative)\n"
        "- originating_site_block (e.g. Block A - Sterile Injectables, Block B - Solid Oral Dosage, Block C - Liquid Packaging)\n"
        "- impacted_npm (Non-Product Materials e.g. PVC/PVDC Blister Foil, Type-1 Glass Vial & Rubber Stopper, HDPE Bottle)\n\n"
        "IMPORTANT RULES:\n"
        "1. Extract all explicitly mentioned values accurately.\n"
        "2. For fields NOT explicitly mentioned (such as manufacturing_date, expiry_date, originating_site_block, impacted_npm), INTELLIGENTLY INFER realistic pharmaceutical defaults based on the product type and complaint defect so that ALL 12 FIELDS are populated!"
    )

    prompt = f"User Complaint Input:\n'{user_msg}'"
    extracted = call_groq_json(prompt, system_prompt)

    all_keys = [
        "complaint_source", "customer_name", "product_name", "product_strength",
        "batch_lot_number", "manufacturing_date", "expiry_date", "affected_quantity",
        "complaint_category", "complaint_description", "originating_site_block", "impacted_npm"
    ]
    cleaned = {}
    for k in all_keys:
        cleaned[k] = str(extracted.get(k, "") or "")

    state["extracted_fields"] = cleaned
    state["merged_fields"] = cleaned.copy()
    state["tool_used"] = "log_complaint"
    state["changed_fields"] = {k: {"old_value": "", "new_value": v} for k, v in cleaned.items() if v}
    return state
