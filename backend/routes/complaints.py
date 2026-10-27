from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import Complaint, ComplaintChatMessage, ComplaintFieldAudit, CAPA, CAPAActionItem
from schemas.complaint_schema import ComplaintRead, AuditLogRead, ChatMessageRead
from routes.capa import generate_capa_number

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

@router.get("", response_model=List[ComplaintRead])
async def list_complaints(db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).order_by(Complaint.updated_at.desc())
    result = await db.execute(stmt)
    complaints = result.scalars().all()
    
    response = []
    for c in complaints:
        # Load related data using ForeignKey
        chat_stmt = select(ComplaintChatMessage).filter(ComplaintChatMessage.complaint_id == c.id).order_by(ComplaintChatMessage.created_at.asc())
        chat_res = await db.execute(chat_stmt)
        chat_messages = chat_res.scalars().all()

        audit_stmt = select(ComplaintFieldAudit).filter(ComplaintFieldAudit.complaint_id == c.id).order_by(ComplaintFieldAudit.changed_at.desc())
        audit_res = await db.execute(audit_stmt)
        audit_logs = audit_res.scalars().all()

        capa_stmt = select(CAPA).filter(CAPA.complaint_id == c.id).order_by(CAPA.updated_at.desc())
        capa_res = await db.execute(capa_stmt)
        capas = capa_res.scalars().all()

        capas_with_items = []
        for capa in capas:
            item_stmt = select(CAPAActionItem).filter(CAPAActionItem.capa_id == capa.id)
            item_res = await db.execute(item_stmt)
            capa.action_items = item_res.scalars().all()
            capas_with_items.append(capa)

        c.chat_messages = chat_messages
        c.audit_logs = audit_logs
        c.capas = capas_with_items
        response.append(c)

    return response

@router.get("/{complaint_id}", response_model=ComplaintRead)
async def get_complaint(complaint_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Complaint).filter(Complaint.id == complaint_id)
    result = await db.execute(stmt)
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Load related data using ForeignKey
    chat_stmt = select(ComplaintChatMessage).filter(ComplaintChatMessage.complaint_id == complaint.id).order_by(ComplaintChatMessage.created_at.asc())
    chat_res = await db.execute(chat_stmt)
    complaint.chat_messages = chat_res.scalars().all()

    audit_stmt = select(ComplaintFieldAudit).filter(ComplaintFieldAudit.complaint_id == complaint.id).order_by(ComplaintFieldAudit.changed_at.desc())
    audit_res = await db.execute(audit_stmt)
    complaint.audit_logs = audit_res.scalars().all()

    capa_stmt = select(CAPA).filter(CAPA.complaint_id == complaint.id).order_by(CAPA.updated_at.desc())
    capa_res = await db.execute(capa_stmt)
    capas = capa_res.scalars().all()

    capas_with_items = []
    for capa in capas:
        item_stmt = select(CAPAActionItem).filter(CAPAActionItem.capa_id == capa.id)
        item_res = await db.execute(item_stmt)
        capa.action_items = item_res.scalars().all()
        capas_with_items.append(capa)

    complaint.capas = capas_with_items
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

