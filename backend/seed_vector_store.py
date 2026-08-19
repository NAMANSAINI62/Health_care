import asyncio
import database.connection as db_conn
from database.models import Complaint
from sqlalchemy.future import select
from agents.vector_store import index_complaint_vector

async def seed():
    await db_conn.init_db_tables()
    async with db_conn.AsyncSessionLocal() as db:
        stmt = select(Complaint)
        res = await db.execute(stmt)
        complaints = res.scalars().all()
        print(f"Found {len(complaints)} existing complaints in database. Indexing into ChromaDB Vector Store...")

        count = 0
        for comp in complaints:
            success = index_complaint_vector(comp.id, {
                "product_name": comp.product_name,
                "batch_lot_number": comp.batch_lot_number,
                "complaint_category": comp.complaint_category,
                "complaint_description": comp.complaint_description,
                "originating_site_block": comp.originating_site_block,
                "severity": comp.severity,
                "suggested_next_action": comp.suggested_next_action,
                "likely_root_cause": comp.likely_root_cause
            })
            if success:
                count += 1

        print(f"[SUCCESS] Indexed {count} complaints into ChromaDB Persistent Collection 'pharma_complaints_vector_store'!")

if __name__ == "__main__":
    asyncio.run(seed())
