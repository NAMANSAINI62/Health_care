import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.graph import complaint_agent_graph
from agents.state import ComplaintAgentState



def test_log_complaint_workflow():
    initial_state: ComplaintAgentState = {
        "complaint_id": None,
        "user_message": "Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg.",
        "document_text": None,
        "intent": None,
        "existing_fields": {},
        "extracted_fields": {},
        "merged_fields": {},
        "risk_assessment": {},
        "changed_fields": {},
        "assistant_message": "",
        "tool_used": "log_complaint",
        "status": "Pending Triage"
    }

    res = complaint_agent_graph.invoke(initial_state)

    assert res["tool_used"] == "log_complaint"
    assert res["merged_fields"]["product_name"] != ""
    assert res["risk_assessment"]["severity"] in ["Minor", "Major", "Critical"]
    assert "likely_root_cause" in res["risk_assessment"]
    print("[SUCCESS] test_log_complaint_workflow passed!")

def test_edit_complaint_workflow():
    existing = {
        "product_name": "Amoxicillin Capsules",
        "product_strength": "500 mg",
        "batch_lot_number": "OLD-BATCH-123",
        "affected_quantity": "100 capsules"
    }

    initial_state: ComplaintAgentState = {
        "complaint_id": 1,
        "user_message": "Sorry, the batch number is BMX-240602, and the affected quantity is 48 capsules.",
        "document_text": None,
        "intent": None,
        "existing_fields": existing,
        "extracted_fields": {},
        "merged_fields": existing.copy(),
        "risk_assessment": {},
        "changed_fields": {},
        "assistant_message": "",
        "tool_used": "edit_complaint",
        "status": "Pending Triage"
    }

    res = complaint_agent_graph.invoke(initial_state)

    assert res["tool_used"] == "edit_complaint"
    # Verify mentioned fields changed
    assert res["merged_fields"]["batch_lot_number"] == "BMX-240602"
    assert res["merged_fields"]["affected_quantity"] == "48 capsules"
    # Verify unmentioned fields were preserved intact
    assert res["merged_fields"]["product_name"] == "Amoxicillin Capsules"
    assert res["merged_fields"]["product_strength"] == "500 mg"
    print("[SUCCESS] test_edit_complaint_workflow passed! Untouched fields strictly preserved.")


if __name__ == "__main__":
    test_log_complaint_workflow()
    test_edit_complaint_workflow()
