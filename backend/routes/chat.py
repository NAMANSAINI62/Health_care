import io
import time
import logging
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Complaint, ComplaintChatMessage, ComplaintFieldAudit
from schemas.complaint_schema import ChatRequest, ChatResponse, ComplaintFormData, RiskAssessmentData
from agents.graph import complaint_agent_graph
from agents.state import ComplaintAgentState
from agents.vision import call_groq_vision_ocr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/complaints", tags=["chat"])

FORM_FIELDS = [
    "complaint_source", "customer_name", "product_name", "product_strength",
    "batch_lot_number", "manufacturing_date", "expiry_date", "affected_quantity",
    "complaint_category", "complaint_description", "originating_site_block", "impacted_npm"
]

# Security 1: In-Memory IP Rate Limiter (Max 5 requests per minute per IP)
ip_rate_tracker: Dict[str, list] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 5

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    
    if client_ip not in ip_rate_tracker:
        ip_rate_tracker[client_ip] = []
    
    # Filter out timestamps older than rate limit window
    ip_rate_tracker[client_ip] = [t for t in ip_rate_tracker[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(ip_rate_tracker[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Maximum 5 requests per minute allowed.")
    
    ip_rate_tracker[client_ip].append(now)

def complaint_to_dict(c: Complaint) -> dict:
    return {field: getattr(c, field, "") or "" for field in FORM_FIELDS}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(
    req: ChatRequest,
    raw_request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Enforce Rate Limiting
    check_rate_limit(raw_request)
    
    # Security 2: Payload Sanitization & Input Length Cap
    if len(req.message) > 5000:
        raise HTTPException(status_code=400, detail="Message exceeds maximum length of 5000 characters.")

    try:
        existing_fields = {}
        complaint_obj = None

        if req.complaint_id:
            stmt = select(Complaint).filter(Complaint.id == req.complaint_id)
            result = await db.execute(stmt)
            complaint_obj = result.scalar_one_or_none()
            if complaint_obj:
                existing_fields = complaint_to_dict(complaint_obj)

        initial_state: ComplaintAgentState = {
            "complaint_id": req.complaint_id,
            "user_message": req.message,
            "document_text": None,
            "intent": None,
            "existing_fields": existing_fields,
            "extracted_fields": {},
            "merged_fields": existing_fields.copy(),
            "risk_assessment": {},
            "changed_fields": {},
            "assistant_message": "",
            "tool_used": "log_complaint",
            "status": "Pending Triage"
        }

        # Run LangGraph pipeline
        final_state = complaint_agent_graph.invoke(initial_state)

        merged = final_state.get("merged_fields", {})
        risk = final_state.get("risk_assessment", {})
        tool_used = final_state.get("tool_used", "log_complaint")
        assistant_msg = final_state.get("assistant_message", "Complaint processed.")
        status = final_state.get("status", "Pending Triage")
        changed = final_state.get("changed_fields", {})

        # Database Persistence
        if not complaint_obj:
            complaint_obj = Complaint(
                complaint_source=merged.get("complaint_source"),
                customer_name=merged.get("customer_name"),
                product_name=merged.get("product_name"),
                product_strength=merged.get("product_strength"),
                batch_lot_number=merged.get("batch_lot_number"),
                manufacturing_date=merged.get("manufacturing_date"),
                expiry_date=merged.get("expiry_date"),
                affected_quantity=merged.get("affected_quantity"),
                complaint_category=merged.get("complaint_category"),
                complaint_description=merged.get("complaint_description"),
                originating_site_block=merged.get("originating_site_block"),
                impacted_npm=merged.get("impacted_npm"),
                status=status,
                severity=risk.get("severity"),
                suggested_next_action=risk.get("suggested_next_action"),
                initial_risk_assessment=risk.get("initial_risk_assessment"),
                likely_root_cause=risk.get("likely_root_cause")
            )
            db.add(complaint_obj)
            await db.flush()
        else:
            for f in FORM_FIELDS:
                if f in merged:
                    setattr(complaint_obj, f, merged[f])
            complaint_obj.status = status
            complaint_obj.severity = risk.get("severity")
            complaint_obj.suggested_next_action = risk.get("suggested_next_action")
            complaint_obj.initial_risk_assessment = risk.get("initial_risk_assessment")
            complaint_obj.likely_root_cause = risk.get("likely_root_cause")

        # Chat history
        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="user", content=req.message, tool_used=tool_used))
        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="assistant", content=assistant_msg, tool_used=tool_used))

        # Audit Trail Logging
        for field_name, audit_data in changed.items():
            db.add(ComplaintFieldAudit(
                complaint_id=complaint_obj.id,
                field_name=field_name,
                old_value=audit_data.get("old_value"),
                new_value=audit_data.get("new_value"),
                changed_by="ai_agent"
            ))

        await db.commit()

        form_data_obj = ComplaintFormData(**{f: merged.get(f, "") for f in FORM_FIELDS})
        risk_obj = RiskAssessmentData(
            severity=risk.get("severity", "Minor"),
            suggested_next_action=risk.get("suggested_next_action", ""),
            initial_risk_assessment=risk.get("initial_risk_assessment", ""),
            likely_root_cause=risk.get("likely_root_cause", "")
        )

        return ChatResponse(
            complaint_id=complaint_obj.id,
            form_data=form_data_obj,
            risk_assessment=risk_obj,
            status=complaint_obj.status,
            assistant_message=assistant_msg,
            tool_used=tool_used
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing complaint AI request.")


@router.post("/scan-image", response_model=ChatResponse)
async def scan_packaging_image(
    raw_request: Request,
    file: UploadFile = File(...),
    complaint_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    check_rate_limit(raw_request)

    filename = file.filename or ""
    allowed_image_extensions = (".png", ".jpg", ".jpeg", ".webp")
    if not filename.lower().endswith(allowed_image_extensions):
        raise HTTPException(
            status_code=400,
            detail="Invalid image type for packaging scan. Only PNG, JPG, JPEG, and WEBP files are allowed."
        )

    content_bytes = await file.read()
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image file size exceeds maximum allowed limit of 5MB.")

    parsed_cid = None
    if complaint_id and str(complaint_id).strip() not in ("null", "undefined", ""):
        try:
            parsed_cid = int(complaint_id)
        except ValueError:
            parsed_cid = None

    try:
        # Run Groq Vision LLM OCR & defect detection
        ocr_result = call_groq_vision_ocr(content_bytes, filename)

        extracted_form = ocr_result.get("form_data", {})
        extracted_risk = ocr_result.get("risk_assessment", {})
        detected_defects = ocr_result.get("detected_defects", [])
        assistant_msg = ocr_result.get("assistant_message", f"Groq Vision LLM analyzed {filename}.")

        existing_fields = {}
        complaint_obj = None
        if parsed_cid:
            stmt = select(Complaint).filter(Complaint.id == parsed_cid)
            result = await db.execute(stmt)
            complaint_obj = result.scalar_one_or_none()
            if complaint_obj:
                existing_fields = complaint_to_dict(complaint_obj)

        # Merge extracted form fields with existing complaint
        merged_fields = existing_fields.copy()
        changed_fields = {}
        for f in FORM_FIELDS:
            new_val = extracted_form.get(f)
            if new_val and new_val != merged_fields.get(f):
                changed_fields[f] = {
                    "old_value": merged_fields.get(f, ""),
                    "new_value": new_val
                }
                merged_fields[f] = new_val

        status = "Pending Triage"

        if not complaint_obj:
            complaint_obj = Complaint(
                complaint_source=merged_fields.get("complaint_source", "Patient Image Upload"),
                customer_name=merged_fields.get("customer_name"),
                product_name=merged_fields.get("product_name"),
                product_strength=merged_fields.get("product_strength"),
                batch_lot_number=merged_fields.get("batch_lot_number"),
                manufacturing_date=merged_fields.get("manufacturing_date"),
                expiry_date=merged_fields.get("expiry_date"),
                affected_quantity=merged_fields.get("affected_quantity"),
                complaint_category=merged_fields.get("complaint_category"),
                complaint_description=merged_fields.get("complaint_description"),
                originating_site_block=merged_fields.get("originating_site_block"),
                impacted_npm=merged_fields.get("impacted_npm"),
                status=status,
                severity=extracted_risk.get("severity", "Major"),
                suggested_next_action=extracted_risk.get("suggested_next_action"),
                initial_risk_assessment=extracted_risk.get("initial_risk_assessment"),
                likely_root_cause=extracted_risk.get("likely_root_cause")
            )
            db.add(complaint_obj)
            await db.flush()
        else:
            for f in FORM_FIELDS:
                if f in merged_fields and merged_fields[f]:
                    setattr(complaint_obj, f, merged_fields[f])
            complaint_obj.status = status
            complaint_obj.severity = extracted_risk.get("severity", complaint_obj.severity)
            complaint_obj.suggested_next_action = extracted_risk.get("suggested_next_action", complaint_obj.suggested_next_action)
            complaint_obj.initial_risk_assessment = extracted_risk.get("initial_risk_assessment", complaint_obj.initial_risk_assessment)
            complaint_obj.likely_root_cause = extracted_risk.get("likely_root_cause", complaint_obj.likely_root_cause)

        # Record Chat history
        tool_name = "multimodal_image_ocr"
        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="user", content=f"Uploaded packaging image: {filename}", tool_used=tool_name))
        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="assistant", content=assistant_msg, tool_used=tool_name))

        # Record Audit Trail entries
        for field_name, audit_data in changed_fields.items():
            db.add(ComplaintFieldAudit(
                complaint_id=complaint_obj.id,
                field_name=field_name,
                old_value=audit_data.get("old_value"),
                new_value=audit_data.get("new_value"),
                changed_by="groq_vision_ocr"
            ))

        await db.commit()

        form_data_obj = ComplaintFormData(**{f: merged_fields.get(f, "") for f in FORM_FIELDS})
        risk_obj = RiskAssessmentData(
            severity=extracted_risk.get("severity", "Major"),
            suggested_next_action=extracted_risk.get("suggested_next_action", ""),
            initial_risk_assessment=extracted_risk.get("initial_risk_assessment", ""),
            likely_root_cause=extracted_risk.get("likely_root_cause", "")
        )

        return ChatResponse(
            complaint_id=complaint_obj.id,
            form_data=form_data_obj,
            risk_assessment=risk_obj,
            status=complaint_obj.status,
            assistant_message=assistant_msg,
            tool_used=tool_name,
            detected_defects=detected_defects
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning packaging image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing packaging image.")


@router.post("/upload", response_model=ChatResponse)
async def upload_document(
    raw_request: Request,
    file: UploadFile = File(...),
    complaint_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    check_rate_limit(raw_request)

    filename = file.filename or ""
    image_extensions = (".png", ".jpg", ".jpeg", ".webp")
    doc_extensions = (".pdf", ".txt", ".eml", ".doc", ".docx")

    # If an image file is uploaded to /upload, route it to scan_packaging_image seamlessly
    if filename.lower().endswith(image_extensions):
        return await scan_packaging_image(raw_request, file, complaint_id, db)

    if not filename.lower().endswith(doc_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, TXT, EML, DOC, DOCX, PNG, JPG, JPEG, and WEBP files are allowed.")

    content_bytes = await file.read()
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 5MB.")

    parsed_cid = None
    if complaint_id and str(complaint_id).strip() not in ("null", "undefined", ""):
        try:
            parsed_cid = int(complaint_id)
        except ValueError:
            parsed_cid = None

    extracted_text = ""
    try:
        if filename.lower().endswith(".pdf"):
            try:
                import pypdf
                pdf_reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                text_pages = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
                extracted_text = "\n".join(text_pages)
            except Exception:
                extracted_text = content_bytes.decode("utf-8", errors="ignore")
        else:
            extracted_text = content_bytes.decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            extracted_text = f"Sample Complaint File: {filename}\nExtract details cleanly."

        existing_fields = {}
        complaint_obj = None
        if parsed_cid:
            stmt = select(Complaint).filter(Complaint.id == parsed_cid)
            result = await db.execute(stmt)
            complaint_obj = result.scalar_one_or_none()
            if complaint_obj:
                existing_fields = complaint_to_dict(complaint_obj)

        initial_state: ComplaintAgentState = {
            "complaint_id": complaint_id,
            "user_message": f"Extract complaint details from document: {filename}",
            "document_text": extracted_text,
            "intent": "document_extraction",
            "existing_fields": existing_fields,
            "extracted_fields": {},
            "merged_fields": existing_fields.copy(),
            "risk_assessment": {},
            "changed_fields": {},
            "assistant_message": "",
            "tool_used": "document_extraction",
            "status": "Pending Triage"
        }

        final_state = complaint_agent_graph.invoke(initial_state)

        merged = final_state.get("merged_fields", {})
        risk = final_state.get("risk_assessment", {})
        tool_used = "document_extraction"
        assistant_msg = final_state.get("assistant_message", f"Extracted details from {filename}.")
        status = final_state.get("status", "Pending Triage")
        changed = final_state.get("changed_fields", {})

        if not complaint_obj:
            complaint_obj = Complaint(
                complaint_source=merged.get("complaint_source"),
                customer_name=merged.get("customer_name"),
                product_name=merged.get("product_name"),
                product_strength=merged.get("product_strength"),
                batch_lot_number=merged.get("batch_lot_number"),
                manufacturing_date=merged.get("manufacturing_date"),
                expiry_date=merged.get("expiry_date"),
                affected_quantity=merged.get("affected_quantity"),
                complaint_category=merged.get("complaint_category"),
                complaint_description=merged.get("complaint_description"),
                originating_site_block=merged.get("originating_site_block"),
                impacted_npm=merged.get("impacted_npm"),
                status=status,
                severity=risk.get("severity"),
                suggested_next_action=risk.get("suggested_next_action"),
                initial_risk_assessment=risk.get("initial_risk_assessment"),
                likely_root_cause=risk.get("likely_root_cause")
            )
            db.add(complaint_obj)
            await db.flush()
        else:
            for f in FORM_FIELDS:
                if f in merged:
                    setattr(complaint_obj, f, merged[f])
            complaint_obj.status = status
            complaint_obj.severity = risk.get("severity")
            complaint_obj.suggested_next_action = risk.get("suggested_next_action")
            complaint_obj.initial_risk_assessment = risk.get("initial_risk_assessment")
            complaint_obj.likely_root_cause = risk.get("likely_root_cause")

        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="user", content=f"Uploaded file: {filename}", tool_used=tool_used))
        db.add(ComplaintChatMessage(complaint_id=complaint_obj.id, role="assistant", content=assistant_msg, tool_used=tool_used))

        for field_name, audit_data in changed.items():
            db.add(ComplaintFieldAudit(
                complaint_id=complaint_obj.id,
                field_name=field_name,
                old_value=audit_data.get("old_value"),
                new_value=audit_data.get("new_value"),
                changed_by="ai_agent"
            ))

        await db.commit()

        form_data_obj = ComplaintFormData(**{f: merged.get(f, "") for f in FORM_FIELDS})
        risk_obj = RiskAssessmentData(
            severity=risk.get("severity", "Minor"),
            suggested_next_action=risk.get("suggested_next_action", ""),
            initial_risk_assessment=risk.get("initial_risk_assessment", ""),
            likely_root_cause=risk.get("likely_root_cause", "")
        )

        return ChatResponse(
            complaint_id=complaint_obj.id,
            form_data=form_data_obj,
            risk_assessment=risk_obj,
            status=complaint_obj.status,
            assistant_message=assistant_msg,
            tool_used=tool_used
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling file upload request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing uploaded file.")

