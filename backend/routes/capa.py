from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import CAPA, CAPAActionItem, Complaint, ComplaintFieldAudit
from schemas.complaint_schema import CAPARead, CAPACreate, CAPAUpdate, CAPAActionItemRead, CAPAActionItemCreate

router = APIRouter(prefix="/api/capas", tags=["capas"])

async def generate_capa_number(db: AsyncSession) -> str:
    year = datetime.now().year
    stmt = select(CAPA).order_by(CAPA.id.desc())
    result = await db.execute(stmt)
    last_capa = result.scalars().first()
    next_id = (last_capa.id + 1) if last_capa else 1
    return f"CAPA-{year}-{next_id:03d}"

@router.get("", response_model=List[CAPARead])
async def list_capas(
    department: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CAPA).options(selectinload(CAPA.action_items)).order_by(CAPA.updated_at.desc())
    result = await db.execute(stmt)
    capas = result.scalars().all()
    
    filtered = []
    for c in capas:
        if department and c.owner_department.lower() != department.lower():
            continue
        if status and c.status.lower() != status.lower():
            continue
        if severity and c.severity.lower() != severity.lower():
            continue
        filtered.append(c)
    return filtered

@router.get("/{capa_id}", response_model=CAPARead)
async def get_capa(capa_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(CAPA).options(selectinload(CAPA.action_items)).filter(CAPA.id == capa_id)
    result = await db.execute(stmt)
    capa = result.scalar_one_or_none()
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA task not found")
    return capa

@router.post("", response_model=CAPARead)
async def create_capa(payload: CAPACreate, db: AsyncSession = Depends(get_db)):
    capa_num = await generate_capa_number(db)
    due_dt = datetime.now() + timedelta(days=payload.due_days or 30)

    owner_dept = payload.owner_department
    root_cause_desc = payload.root_cause

    if payload.complaint_id:
        stmt = select(Complaint).filter(Complaint.id == payload.complaint_id)
        res = await db.execute(stmt)
        complaint = res.scalar_one_or_none()
        if complaint:
            if complaint.originating_site_block and not owner_dept:
                owner_dept = complaint.originating_site_block
            if complaint.likely_root_cause and not root_cause_desc:
                root_cause_desc = complaint.likely_root_cause

    new_capa = CAPA(
        capa_number=capa_num,
        complaint_id=payload.complaint_id,
        title=payload.title,
        description=payload.description,
        root_cause=root_cause_desc,
        severity=payload.severity,
        owner_department=owner_dept or "Quality Assurance",
        assignee_name=payload.assignee_name or "QA Lead",
        status="Open",
        due_date=due_dt,
        escalation_status="Normal"
    )
    db.add(new_capa)
    await db.flush()

    action_items_to_add = payload.action_items or []
    if not action_items_to_add:
        action_items_to_add = [
            CAPAActionItemCreate(
                action_type="Corrective Action",
                description=f"Isolate affected product lot and conduct batch record review for {owner_dept or 'Production'}.",
                assignee=payload.assignee_name or "Department Supervisor",
                due_date=datetime.now() + timedelta(days=7)
            ),
            CAPAActionItemCreate(
                action_type="Preventive Action",
                description="Update Standard Operating Procedure (SOP) and recalibrate equipment parameters to prevent recurrence.",
                assignee="Quality Assurance Lead",
                due_date=datetime.now() + timedelta(days=21)
            )
        ]

    for item in action_items_to_add:
        ai = CAPAActionItem(
            capa_id=new_capa.id,
            action_type=item.action_type,
            description=item.description,
            assignee=item.assignee,
            due_date=item.due_date or (datetime.now() + timedelta(days=14)),
            status="Pending"
        )
        db.add(ai)

    if payload.complaint_id:
        audit_log = ComplaintFieldAudit(
            complaint_id=payload.complaint_id,
            field_name="capa_initiated",
            old_value="None",
            new_value=f"Generated {capa_num} assigned to {owner_dept or 'QA'}",
            changed_by="system_capa_engine"
        )
        db.add(audit_log)
        
        stmt_comp = select(Complaint).filter(Complaint.id == payload.complaint_id)
        comp_res = await db.execute(stmt_comp)
        comp_obj = comp_res.scalar_one_or_none()
        if comp_obj and comp_obj.status != "Closed":
            comp_obj.status = "CAPA Initiated"

    await db.commit()

    stmt_full = select(CAPA).options(selectinload(CAPA.action_items)).filter(CAPA.id == new_capa.id)
    res_full = await db.execute(stmt_full)
    return res_full.scalar_one()

@router.put("/{capa_id}", response_model=CAPARead)
async def update_capa(capa_id: int, payload: CAPAUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(CAPA).options(selectinload(CAPA.action_items)).filter(CAPA.id == capa_id)
    result = await db.execute(stmt)
    capa = result.scalar_one_or_none()
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA task not found")

    for field, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(capa, field, val)

    await db.commit()
    await db.refresh(capa)
    return capa

@router.post("/{capa_id}/action-items", response_model=CAPAActionItemRead)
async def add_action_item(capa_id: int, item: CAPAActionItemCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(CAPA).filter(CAPA.id == capa_id)
    res = await db.execute(stmt)
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="CAPA task not found")

    ai = CAPAActionItem(
        capa_id=capa_id,
        action_type=item.action_type,
        description=item.description,
        assignee=item.assignee,
        due_date=item.due_date or (datetime.now() + timedelta(days=14)),
        status="Pending"
    )
    db.add(ai)
    await db.commit()
    await db.refresh(ai)
    return ai

@router.put("/action-items/{item_id}", response_model=CAPAActionItemRead)
async def toggle_action_item_status(item_id: int, status: str, db: AsyncSession = Depends(get_db)):
    stmt = select(CAPAActionItem).filter(CAPAActionItem.id == item_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    item.status = status
    if status == "Completed":
        item.completed_at = datetime.now()
    else:
        item.completed_at = None

    await db.commit()
    await db.refresh(item)

    stmt_capa = select(CAPA).options(selectinload(CAPA.action_items)).filter(CAPA.id == item.capa_id)
    capa_res = await db.execute(stmt_capa)
    capa_obj = capa_res.scalar_one_or_none()
    if capa_obj and all(a.status == "Completed" for a in capa_obj.action_items):
        capa_obj.status = "Completed"
        await db.commit()

    return item

@router.post("/{capa_id}/escalate")
async def escalate_capa(capa_id: int, level: str = "Escalated - Level 1", db: AsyncSession = Depends(get_db)):
    stmt = select(CAPA).filter(CAPA.id == capa_id)
    res = await db.execute(stmt)
    capa = res.scalar_one_or_none()
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA task not found")

    capa.escalation_status = level
    capa.status = "Overdue"
    
    if capa.complaint_id:
        audit_log = ComplaintFieldAudit(
            complaint_id=capa.complaint_id,
            field_name="capa_escalation",
            old_value="Normal",
            new_value=f"{level} - Triggered for {capa.capa_number} ({capa.owner_department})",
            changed_by="qa_escalation_engine"
        )
        db.add(audit_log)

    await db.commit()
    return {"id": capa.id, "capa_number": capa.capa_number, "escalation_status": capa.escalation_status}
