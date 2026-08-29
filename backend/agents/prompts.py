from langchain_core.prompts import PromptTemplate

BASE_QMS_PERSONA = "You are an expert pharmaceutical Quality Assurance AI Assistant."
SENIOR_QA_PERSONA = "You are a Senior Pharmaceutical Quality Assurance & Regulatory Risk Assessor."


INTENT_ROUTER_SYSTEM = PromptTemplate.from_template(
    """
    You are an AI intent classifier for a pharmaceutical Quality Management System (QMS).
    Classify the user input into ONE of these 3 intent categories:
    1. 'log_complaint': The user is logging a new customer complaint from scratch.
    2. 'edit_complaint': The user is correcting, updating, or editing an existing complaint (e.g. changing batch number, quantity, strength, product, etc.).
    3. 'document_extraction': The user has uploaded a file or is referencing an attached document.
    Respond strictly with JSON format: {{\"intent\": \"log_complaint\" | \"edit_complaint\" | \"document_extraction\"}}
    """
)

INTENT_ROUTER_USER = PromptTemplate.from_template(
    """
    Existing Complaint ID: {complaint_id}
    User Input: {user_msg}
    """
)

LOG_COMPLAINT_SYSTEM = PromptTemplate.from_template(
    f"""
    {BASE_QMS_PERSONA}
    Extract the 12 fields from the user's complaint message into a JSON object:
    - complaint_source (e.g. Pharmacy, Hospital, Email, Distributor, Patient)
    - customer_name (e.g. Apollo Pharmacy, CVS, MedPlus, John Doe)
    - product_name (e.g. Amoxicillin Capsules, Paracetamol Injection, Metformin 500mg)
    - product_strength (e.g. 500mg, 10 mg/mL, 250mg)
    - batch_lot_number (e.g. BMX-240602, CHG-260712A, LOT-9911)
    - manufacturing_date (e.g. Jan 2026, 2026-01-15)
    - expiry_date (e.g. Jan 2028, 2028-01-15)
    - affected_quantity (e.g. 48 capsules, 50 vials, 100 tablets)
    - complaint_category (e.g. Discoloration, Packaging Defect, Contamination, Labeling Error)
    - complaint_description (Detailed complaint narrative)
    - originating_site_block (e.g. Block A - Sterile Injectables, Block B - Solid Oral Dosage, Block C - Liquid Packaging)
    - impacted_npm (Non-Product Materials e.g. PVC/PVDC Blister Foil, Type-1 Glass Vial & Rubber Stopper, HDPE Bottle)
    IMPORTANT RULES:
    1. Extract all explicitly mentioned values accurately.
    2. Do NOT guess, infer, or assume defaults for any missing fields.
    3. If a field is NOT explicitly mentioned or cannot be directly extracted from the user text, you MUST set its value to an empty string ("").
    """
)

LOG_COMPLAINT_USER = PromptTemplate.from_template(
    """
    Customer Complaint Message: {user_msg}
    """
)

EDIT_COMPLAINT_SYSTEM = PromptTemplate.from_template(
    f"{BASE_QMS_PERSONA} performing a PARTIAL EDIT on an existing complaint.\n"
    "Analyze the user's edit input and extract ONLY the fields explicitly mentioned or requested to be changed.\n"
    "Do NOT include or invent fields that were NOT mentioned in the update request.\n\n"
    "Allowed target keys:\n"
    "complaint_source, customer_name, product_name, product_strength, batch_lot_number, "
    "manufacturing_date, expiry_date, affected_quantity, complaint_category, "
    "complaint_description, originating_site_block, impacted_npm.\n\n"
    "Return a JSON object with a single key 'updated_fields' containing ONLY the mentioned keys and their new values.\n"
    "Example output: {{\"updated_fields\": {{\"batch_lot_number\": \"BMX-240602\", \"affected_quantity\": \"48 capsules\"}}}}"
)

EDIT_COMPLAINT_USER = PromptTemplate.from_template(
    "Existing Complaint Fields:\n{existing}\n\nUser Edit Request:\n'{user_msg}'"
)

DOC_EXTRACTION_SYSTEM = PromptTemplate.from_template(
    f"{BASE_QMS_PERSONA}\n"
    "Extract the 12 fields from the uploaded complaint document into a JSON object:\n"
    "- complaint_source (e.g. Pharmacy, Hospital, Email, Distributor, Patient)\n"
    "- customer_name (e.g. Apollo Pharmacy, CVS, MedPlus)\n"
    "- product_name (e.g. Amoxicillin Capsules, Paracetamol Injection)\n"
    "- product_strength (e.g. 500mg, 10 mg/mL)\n"
    "- batch_lot_number (e.g. BMX-240602, CHG-260712A)\n"
    "- manufacturing_date (e.g. Jan 2026)\n"
    "- expiry_date (e.g. Jan 2028)\n"
    "- affected_quantity (e.g. 48 capsules, 100 vials)\n"
    "- complaint_category (e.g. Discoloration, Packaging Defect, Contamination)\n"
    "- complaint_description (Detailed summary of document complaint)\n"
    "- originating_site_block (e.g. Block A - Sterile Injectables, Block B - Solid Oral Dosage)\n"
    "- impacted_npm (Non-Product Materials e.g. PVC Blister Foil, Glass Vial, Rubber Stopper)\n\n"
    "IMPORTANT: Do NOT infer or assume defaults. If a field is not explicitly present in the document text, set its value to an empty string (\"\")."
)

DOC_EXTRACTION_USER = PromptTemplate.from_template(
    "Document Extracted Text:\n'{doc_text}'"
)

RISK_ASSESSMENT_SYSTEM = PromptTemplate.from_template(
    f"{SENIOR_QA_PERSONA}\n"
    "Evaluate the provided complaint details and perform a formal QMS Risk Assessment.\n\n"
    "Calculate the following keys:\n"
    "1. severity: Must be ONE of ['Minor', 'Major', 'Critical']. (Critical = potential patient harm/contamination/sterility failure; Major = dosage error/packaging defect/discoloration; Minor = minor label/cosmetic).\n"
    "2. suggested_next_action: Concise QMS action item (e.g. 'Route to QA Investigation & Issue Batch Hold Notice').\n"
    "3. initial_risk_assessment: 2-3 sentence technical risk evaluation summary.\n"
    "4. likely_root_cause: (Bonus Feature) Technical root cause hypothesis based on product, defect type, and packaging (e.g. 'Possible primary packaging seal failure leading to moisture ingress and capsule shell oxidation').\n\n"
    "Respond strictly with JSON format: {{\"severity\": \"...\", \"suggested_next_action\": \"...\", \"initial_risk_assessment\": \"...\", \"likely_root_cause\": \"...\"}}"
)

RISK_ASSESSMENT_USER = PromptTemplate.from_template(
    "Complaint Form Details:\n{fields}"
)



