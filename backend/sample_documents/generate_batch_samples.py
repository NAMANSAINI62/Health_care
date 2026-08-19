import os
import json
import csv

def generate_samples():
    sample_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(sample_dir, exist_ok=True)

    # 1. Unique CSV Sample Batch File
    csv_file = os.path.join(sample_dir, "pharma_batch_manifest_2026.csv")
    csv_records = [
        {
            "Complaint_Ref": "BCH-2026-001",
            "Reporting_Entity": "Apex Regional Distributor",
            "Product_Name": "Ciprofloxacin 500mg Tablets",
            "Product_Strength": "500mg",
            "Batch_Lot_Number": "CPX-9901",
            "Mfg_Date": "Feb 2026",
            "Exp_Date": "Feb 2028",
            "Quantity_Affected": "250 Cartons",
            "Complaint_Category": "Blister Foil Pinhole Leakage",
            "Defect_Description": "Pinhole perforations on blister foil causing humidity exposure and tablet crumbling.",
            "Site_Block": "Block E - Oral Solid Facility"
        },
        {
            "Complaint_Ref": "BCH-2026-002",
            "Reporting_Entity": "St. Jude Hospital Pharmacy",
            "Product_Name": "Levofloxacin 750mg Infusion",
            "Product_Strength": "750mg/150mL",
            "Batch_Lot_Number": "LVX-7742",
            "Mfg_Date": "Mar 2026",
            "Exp_Date": "Mar 2028",
            "Quantity_Affected": "80 Infusion Bags",
            "Complaint_Category": "Solution Cloudiness & Precipitate",
            "Defect_Description": "Fine white crystalline precipitate observed in intravenous infusion bag upon inspection.",
            "Site_Block": "Block C - Parenteral Sterile Block"
        },
        {
            "Complaint_Ref": "BCH-2026-003",
            "Reporting_Entity": "Metro General Hospital",
            "Product_Name": "Ceftriaxone 1g Injection",
            "Product_Strength": "1g Vial",
            "Batch_Lot_Number": "CFT-3310",
            "Mfg_Date": "Jan 2026",
            "Exp_Date": "Jan 2028",
            "Quantity_Affected": "300 Vials",
            "Complaint_Category": "Rubber Stopper Fragmentation",
            "Defect_Description": "Rubber particles shedding into reconstituted solution during needle puncture.",
            "Site_Block": "Block C - Lyophilized Injectables"
        },
        {
            "Complaint_Ref": "BCH-2026-004",
            "Reporting_Entity": "CareFirst Pharmacy Network",
            "Product_Name": "Montelukast 10mg Chewable",
            "Product_Strength": "10mg",
            "Batch_Lot_Number": "MLK-5521",
            "Mfg_Date": "Feb 2026",
            "Exp_Date": "Feb 2028",
            "Quantity_Affected": "500 Tablets",
            "Complaint_Category": "Tablet Capping & Weight Variance",
            "Defect_Description": "Tablets splitting along upper crown face during automatic counting.",
            "Site_Block": "Block A - Tableting Line 2"
        },
        {
            "Complaint_Ref": "BCH-2026-005",
            "Reporting_Entity": "Global Logistics Healthcare",
            "Product_Name": "Enoxaparin 40mg Prefilled Syringe",
            "Product_Strength": "40mg/0.4mL",
            "Batch_Lot_Number": "ENX-1188",
            "Mfg_Date": "Apr 2026",
            "Exp_Date": "Apr 2028",
            "Quantity_Affected": "150 Syringes",
            "Complaint_Category": "Needle Shield Misalignment",
            "Defect_Description": "Safety rigid needle shield detached inside primary blister tray.",
            "Site_Block": "Block F - Biologics & Syringes"
        }
    ]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_records[0].keys()))
        writer.writeheader()
        writer.writerows(csv_records)

    print(f"Generated sample CSV: {csv_file}")

    # 2. Unique JSON Sample Batch File
    json_file = os.path.join(sample_dir, "hospital_qa_incident_batch.json")
    json_data = {
        "batch_source": "Hospital System Audit Export Q3",
        "total_records": 3,
        "records": [
            {
                "customer_name": "Sunrise Medical Center",
                "product_name": "Pantoprazole 40mg IV",
                "product_strength": "40mg Vial",
                "batch_lot_number": "PNZ-6630",
                "manufacturing_date": "Jan 2026",
                "expiry_date": "Jan 2028",
                "affected_quantity": "120 Vials",
                "complaint_category": "Vial Glass Hairline Crack",
                "complaint_description": "Hairline crack detected near vial base with slight liquid leakage.",
                "originating_site_block": "Block C - Sterile Injectable Block"
            },
            {
                "customer_name": "National Health Dispensary",
                "product_name": "Clopidogrel 75mg Film-Coated",
                "product_strength": "75mg",
                "batch_lot_number": "CPG-4091",
                "manufacturing_date": "Feb 2026",
                "expiry_date": "Feb 2028",
                "affected_quantity": "400 Tablets",
                "complaint_category": "Film Coating Peeling",
                "complaint_description": "Outer pink film coating peeling off inside blister pockets.",
                "originating_site_block": "Block A - Coating Line 1"
            },
            {
                "customer_name": "United Pharma Wholesalers",
                "product_name": "Meropenem 1g Sterile Powder",
                "product_strength": "1g",
                "batch_lot_number": "MPN-8802",
                "manufacturing_date": "Mar 2026",
                "expiry_date": "Mar 2028",
                "affected_quantity": "90 Vials",
                "complaint_category": "Discoloration & Yellowing",
                "complaint_description": "Sterile cake powder turned pale yellow after storage at 25°C.",
                "originating_site_block": "Block C - Aseptic Suite 4"
            }
        ]
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Generated sample JSON: {json_file}")

if __name__ == "__main__":
    generate_samples()
