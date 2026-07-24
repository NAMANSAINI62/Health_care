import os

def generate_sample_file():
    content = (
        "PHARMA CARE QMS - CUSTOMER COMPLAINT REPORT\n"
        "Date: July 24, 2026\n"
        "Complaint Source: Email / Quality Notice\n"
        "Reporting Customer: Apollo Pharmacy (Regional Distribution Center)\n\n"
        "PRODUCT DETAILS:\n"
        "- Product Name: Amoxicillin Capsules\n"
        "- Dosage & Strength: 500 mg\n"
        "- Batch/Lot Number: BMX-240602\n"
        "- Manufacturing Date: March 2026\n"
        "- Expiry Date: March 2028\n"
        "- Affected Quantity: 48 capsules (2 blisters of 24)\n"
        "- Manufacturing Block: Block B - Solid Dosage Facility\n"
        "- Impacted Non-Product Material: Aluminum Foil Blister & HDPE Container\n\n"
        "DEFECT DESCRIPTION:\n"
        "The customer reported dark brown discoloration on multiple 500mg Amoxicillin capsule shells "
        "upon opening a sealed carton delivered from Batch BMX-240602. Moisture ingress suspected "
        "due to micro-pinholes in primary blister sealing foil.\n"
    )

    out_dir = os.path.dirname(__file__)
    
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PHARMA CARE QMS - CUSTOMER COMPLAINT REPORT", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        for line in content.split("\n"):
            pdf.cell(0, 7, line, ln=True)
        pdf_path = os.path.join(out_dir, "sample_pharma_complaint.pdf")
        pdf.output(pdf_path)
        print(f"[SUCCESS] Generated sample PDF at: {pdf_path}")
    except Exception:
        txt_path = os.path.join(out_dir, "sample_pharma_complaint.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SUCCESS] Generated sample text file at: {txt_path}")

if __name__ == "__main__":
    generate_sample_file()


