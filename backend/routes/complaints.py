from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import hashlib
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import Complaint, ComplaintChatMessage, ComplaintFieldAudit, QASignature, CAPA, CAPAActionItem
from schemas.complaint_schema import ComplaintRead, AuditLogRead, ChatMessageRead, QASignatureCreate, QASignatureRead
from routes.capa import generate_capa_number

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

@router.get("", response_model=List[ComplaintRead])
async def list_complaints(db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.qa_signatures),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).order_by(Complaint.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{complaint_id}", response_model=ComplaintRead)
async def get_complaint(complaint_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.qa_signatures),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.get("/{complaint_id}/audit", response_model=List[AuditLogRead])
async def get_complaint_audit(complaint_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ComplaintFieldAudit).filter(ComplaintFieldAudit.complaint_id == complaint_id).order_by(ComplaintFieldAudit.changed_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{complaint_id}/status")
async def update_complaint_status(complaint_id: int, status: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = status
    await db.commit()
    await db.refresh(complaint)
    return {"id": complaint.id, "status": complaint.status}

@router.post("/{complaint_id}/sign-off", response_model=ComplaintRead)
async def qa_sign_off_complaint(complaint_id: int, payload: QASignatureCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.qa_signatures),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Record QA Digital Signature (FDA 21 CFR Part 11)
    sig = QASignature(
        complaint_id=complaint.id,
        signer_name=payload.signer_name,
        signer_role=payload.signer_role,
        signature_meaning=payload.signature_meaning,
        checksum_hash=payload.checksum_hash,
        comments=payload.comments
    )
    db.add(sig)

    # Log immutable audit entry
    audit_log = ComplaintFieldAudit(
        complaint_id=complaint.id,
        field_name="qa_digital_signature",
        old_value=complaint.status,
        new_value=f"Digitally signed off by {payload.signer_name} ({payload.signer_role}) [Hash: {payload.checksum_hash[:12]}...]",
        changed_by=payload.signer_name
    )
    db.add(audit_log)

    # Update Complaint status
    complaint.status = "QA Approved"

    # Auto-spawn CAPA if severity is Critical or Major and requested
    is_high_risk = complaint.severity in ["Critical", "Major"]
    if payload.auto_spawn_capa and is_high_risk and len(complaint.capas) == 0:
        capa_num = await generate_capa_number(db)
        owner_dept = complaint.originating_site_block or "Quality Assurance"
        
        new_capa = CAPA(
            capa_number=capa_num,
            complaint_id=complaint.id,
            title=f"CAPA for Complaint #{complaint.id}: {complaint.product_name or 'Product Quality Issue'}",
            description=complaint.complaint_description or "Root cause investigation and corrective actions required.",
            root_cause=complaint.likely_root_cause or "Investigating equipment calibration / packaging defect.",
            severity=complaint.severity or "Major",
            owner_department=owner_dept,
            assignee_name=payload.signer_name,
            status="Open",
            due_date=datetime.now() + timedelta(days=30),
            escalation_status="Normal"
        )
        db.add(new_capa)
        await db.flush()

        ai1 = CAPAActionItem(
            capa_id=new_capa.id,
            action_type="Corrective Action",
            description=f"Quarantine batch {complaint.batch_lot_number or 'N/A'} and conduct line inspection in {owner_dept}.",
            assignee=payload.signer_name,
            due_date=datetime.now() + timedelta(days=7),
            status="Pending"
        )
        ai2 = CAPAActionItem(
            capa_id=new_capa.id,
            action_type="Preventive Action",
            description=f"Revise packaging & sterility SOPs and train technicians in {owner_dept}.",
            assignee="QA Compliance Specialist",
            due_date=datetime.now() + timedelta(days=21),
            status="Pending"
        )
        db.add(ai1)
        db.add(ai2)
        complaint.status = "CAPA Initiated"

    await db.commit()

    # Re-fetch updated complaint
    stmt_updated = select(Complaint).options(
        selectinload(Complaint.chat_messages),
        selectinload(Complaint.audit_logs),
        selectinload(Complaint.qa_signatures),
        selectinload(Complaint.capas).selectinload(CAPA.action_items)
    ).filter(Complaint.id == complaint_id)
    res_updated = await db.execute(stmt_updated)
    return res_updated.scalar_one()

