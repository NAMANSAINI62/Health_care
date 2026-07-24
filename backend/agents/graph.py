from langgraph.graph import StateGraph, END
from agents.state import ComplaintAgentState
from agents.nodes.intent_router import intent_router_node
from agents.nodes.log_complaint_tool import log_complaint_tool_node
from agents.nodes.edit_complaint_tool import edit_complaint_tool_node
from agents.nodes.document_extraction_tool import document_extraction_tool_node
from agents.nodes.risk_assessment_node import risk_assessment_node
from agents.nodes.response_formatter import response_formatter_node

def route_intent(state: ComplaintAgentState) -> str:
    intent = state.get("intent", "log_complaint")
    if intent == "edit_complaint":
        return "edit_complaint_node"
    elif intent == "document_extraction":
        return "document_extraction_node"
    else:
        return "log_complaint_node"

# Create State Graph
workflow = StateGraph(ComplaintAgentState)

# Add Nodes
workflow.add_node("intent_router", intent_router_node)
workflow.add_node("log_complaint_node", log_complaint_tool_node)
workflow.add_node("edit_complaint_node", edit_complaint_tool_node)
workflow.add_node("document_extraction_node", document_extraction_tool_node)
workflow.add_node("risk_assessment_node", risk_assessment_node)
workflow.add_node("response_formatter_node", response_formatter_node)

# Set Entry Point
workflow.set_entry_point("intent_router")

# Add Conditional Edges from Intent Router
workflow.add_conditional_edges(
    "intent_router",
    route_intent,
    {
        "log_complaint_node": "log_complaint_node",
        "edit_complaint_node": "edit_complaint_node",
        "document_extraction_node": "document_extraction_node"
    }
)

# Connect Tools to Risk Assessment Node
workflow.add_edge("log_complaint_node", "risk_assessment_node")
workflow.add_edge("edit_complaint_node", "risk_assessment_node")
workflow.add_edge("document_extraction_node", "risk_assessment_node")

# Connect Risk Assessment to Response Formatter
workflow.add_edge("risk_assessment_node", "response_formatter_node")
workflow.add_edge("response_formatter_node", END)

# Compile Graph
complaint_agent_graph = workflow.compile()
