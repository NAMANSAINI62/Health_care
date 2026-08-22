from agents.state import ComplaintAgentState
from agents.llm import call_llm_json
from agents.prompts import INTENT_ROUTER_SYSTEM, INTENT_ROUTER_USER

def intent_router_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Node 1: Classifies the user message into log_complaint, edit_complaint, or document_extraction."""
    user_msg = state.get("user_message", "")
    doc_text = state.get("document_text", "")
    complaint_id = state.get("complaint_id")

    if doc_text and doc_text.strip():
        state["intent"] = "document_extraction"
        return state

    system_prompt = INTENT_ROUTER_SYSTEM.format()
    prompt = INTENT_ROUTER_USER.format(complaint_id=complaint_id, user_msg=user_msg)

    result = call_llm_json(prompt, system_prompt)
    intent = result.get("intent", "log_complaint")

    if complaint_id and intent == "log_complaint":
        update_keywords = ["update", "change", "correct", "sorry", "instead", "is actually", "should be", "wrong", "fix"]
        if any(k in user_msg.lower() for k in update_keywords):
            intent = "edit_complaint"


    state["intent"] = intent
    return state
