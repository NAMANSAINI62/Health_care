import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database.connection as db_conn
from database.models import Complaint
from agents.vector_store import (
    index_complaint_vector,
    query_similar_complaints,
    get_predictive_clusters
)

async def test_vector_trends_without_images():
    print("\n--- TEST: Vector Trends & Clustering Without Any Image Upload ---\n")
    
    # 1. Initialize SQLite database
    await db_conn.init_db_tables()
    
    async with db_conn.AsyncSessionLocal() as db:
        # Create sample text complaints in SQLite
        c1 = Complaint(
            product_name="Amoxicillin 500mg Capsules",
            batch_lot_number="BMX-240602",
            complaint_category="Discolored / Oxydized Capsules",
            complaint_description="Capsule shell discoloration observed upon opening blister pack in warm humid conditions.",
            originating_site_block="Block B - Oral Solid Dosage",
            severity="Major",
            suggested_next_action="Issue Batch Hold Notice & Re-verify Blister Sealing Parameters",
            likely_root_cause="Primary packaging seal pinhole defect causing moisture ingress."
        )
        c2 = Complaint(
            product_name="Amoxicillin 500mg Capsules",
            batch_lot_number="BMX-240603",
            complaint_category="Discolored / Oxydized Capsules",
            complaint_description="Customer reported dark spots on capsules inside blister pack.",
            originating_site_block="Block B - Oral Solid Dosage",
            severity="Major",
            suggested_next_action="Quarantine lot & inspect HVAC humidity logs.",
            likely_root_cause="Moisture absorption due to aluminum foil sealing temperature drop."
        )
        db.add(c1)
        db.add(c2)
        await db.commit()
        await db.refresh(c1)
        await db.refresh(c2)

        # 2. Index complaints into ChromaDB using ONLY text fields (Zero Images!)
        idx1 = index_complaint_vector(c1.id, {
            "product_name": c1.product_name,
            "batch_lot_number": c1.batch_lot_number,
            "complaint_category": c1.complaint_category,
            "complaint_description": c1.complaint_description,
            "originating_site_block": c1.originating_site_block,
            "severity": c1.severity,
            "suggested_next_action": c1.suggested_next_action,
            "likely_root_cause": c1.likely_root_cause
        })
        idx2 = index_complaint_vector(c2.id, {
            "product_name": c2.product_name,
            "batch_lot_number": c2.batch_lot_number,
            "complaint_category": c2.complaint_category,
            "complaint_description": c2.complaint_description,
            "originating_site_block": c2.originating_site_block,
            "severity": c2.severity,
            "suggested_next_action": c2.suggested_next_action,
            "likely_root_cause": c2.likely_root_cause
        })

        print(f"Indexed Complaint #{c1.id} into ChromaDB: {idx1}")
        print(f"Indexed Complaint #{c2.id} into ChromaDB: {idx2}")

        # 3. Query similar complaints using a NEW text query (NO IMAGES AT ALL!)
        query = {
            "product_name": "Amoxicillin 500mg",
            "complaint_category": "Discolored Capsules",
            "complaint_description": "Capsules showing color change in blister packaging",
            "originating_site_block": "Block B - Oral Solid Dosage"
        }
        
        matches = query_similar_complaints(query, top_k=5)
        clusters = get_predictive_clusters()

        print(f"\n[RESULT] Found {len(matches)} ChromaDB Vector Similarity Matches (100% Text-based):")
        for m in matches:
            print(f"  - Complaint: {m['complaint_number']} | Product: {m['product_name']} | Similarity: {m['similarity_score']}%")
            print(f"    Solution: {m['proven_solution']}")

        print(f"\n[RESULT] Found {len(clusters)} Defect Quality Clusters in ChromaDB:")
        for cl in clusters:
            print(f"  - Cluster: {cl['cluster_name']} | Risk: {cl['risk_level']} | Count: {cl['count']}")

        assert len(matches) > 0, "Vector similarity search should return matches!"
        assert len(clusters) > 0, "ChromaDB clustering should compute clusters!"
        print("\n[SUCCESS] Vector store trend prediction verified 100% WORKING WITHOUT IMAGES!\n")

if __name__ == "__main__":
    asyncio.run(test_vector_trends_without_images())
