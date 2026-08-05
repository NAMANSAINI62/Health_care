import os
from PIL import Image, ImageDraw, ImageFont
import random

output_dir = r"d:\Health_care\test_images"
os.makedirs(output_dir, exist_ok=True)

test_cases = [
    {
        "filename": "image1_amoxicillin_crushed.png",
        "product": "Amoxicillin 500mg Capsules",
        "batch": "BMX-240602",
        "mfg_date": "Jan 2026",
        "exp_date": "Jan 2028",
        "defect_type": "Blister Pack Crushed / Foil Seal Failure",
        "color": (255, 230, 230) # Light red
    },
    {
        "filename": "image2_paracetamol_crack.png",
        "product": "Paracetamol Injection 10mg/mL",
        "batch": "LOT-9988",
        "mfg_date": "Feb 2026",
        "exp_date": "Feb 2029",
        "defect_type": "Hairline Glass Crack / Liquid Leakage",
        "color": (230, 240, 255) # Light blue
    },
    {
        "filename": "image3_metformin_chipped.png",
        "product": "Metformin 500mg Tablets",
        "batch": "MFM-8801",
        "mfg_date": "Mar 2026",
        "exp_date": "Mar 2028",
        "defect_type": "Tablet Edge Chipping / Deformation",
        "color": (245, 245, 220) # Beige
    },
    {
        "filename": "image4_diclofenac_seal.png",
        "product": "Diclofenac Sodium Gel",
        "batch": "DFG-1122",
        "mfg_date": "Apr 2026",
        "exp_date": "Apr 2027",
        "defect_type": "Tube Crimp Seal Leakage",
        "color": (230, 255, 230) # Light green
    },
    {
        "filename": "image5_ibuprofen_discolor.png",
        "product": "Ibuprofen 400mg Tablets",
        "batch": "IBU-3344",
        "mfg_date": "May 2026",
        "exp_date": "May 2028",
        "defect_type": "Coating Discoloration / Oxidation",
        "color": (255, 240, 220) # Light orange
    },
    {
        "filename": "image6_cetirizine_empty.png",
        "product": "Cetirizine 10mg Tablets",
        "batch": "CET-5566",
        "mfg_date": "Jun 2026",
        "exp_date": "Jun 2028",
        "defect_type": "Empty Blister Cavity (Missing Tablet)",
        "color": (240, 230, 255) # Light purple
    },
    {
        "filename": "image7_omeprazole_print.png",
        "product": "Omeprazole 20mg Capsules",
        "batch": "OMP-7788",
        "mfg_date": "Jul 2026",
        "exp_date": "Jul 2028",
        "defect_type": "Inkjet Batch Print Fading / Illegible",
        "color": (255, 255, 230) # Light yellow
    },
    {
        "filename": "image8_salbutamol_dent.png",
        "product": "Salbutamol Inhaler 100mcg",
        "batch": "SAL-9900",
        "mfg_date": "Aug 2026",
        "exp_date": "Aug 2027",
        "defect_type": "Aluminum Canister Dented",
        "color": (220, 220, 220) # Light grey
    },
    {
        "filename": "image9_azithromycin_label.png",
        "product": "Azithromycin 250mg Tablets",
        "batch": "AZI-1122",
        "mfg_date": "Sep 2026",
        "exp_date": "Sep 2028",
        "defect_type": "Label Misalignment / Wrinkling",
        "color": (255, 225, 245) # Light pink
    },
    {
        "filename": "image10_pantoprazole_moisture.png",
        "product": "Pantoprazole 40mg Injection",
        "batch": "PAN-3344",
        "mfg_date": "Oct 2026",
        "exp_date": "Oct 2028",
        "defect_type": "Moisture Ingress / Powder Caking",
        "color": (220, 255, 255) # Light cyan
    }
]

def create_image(case):
    img = Image.new('RGB', (800, 600), color=case['color'])
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, otherwise use default
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_medium = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Draw border
    draw.rectangle([20, 20, 780, 580], outline="black", width=5)

    # Draw Header
    draw.text((40, 40), "PHARMACEUTICAL PACKAGING LABEL", fill="black", font=font_large)
    draw.line([(40, 80), (760, 80)], fill="black", width=2)

    # Draw Text Details
    y_offset = 120
    draw.text((40, y_offset), f"Product Name: {case['product']}", fill="navy", font=font_medium)
    y_offset += 50
    draw.text((40, y_offset), f"Batch / Lot No: {case['batch']}", fill="black", font=font_medium)
    y_offset += 50
    draw.text((40, y_offset), f"Mfg Date: {case['mfg_date']}", fill="black", font=font_medium)
    y_offset += 50
    draw.text((40, y_offset), f"Exp Date: {case['exp_date']}", fill="black", font=font_medium)
    
    # Draw Defect Simulation Area
    y_offset += 80
    draw.rectangle([40, y_offset, 760, y_offset + 180], outline="red", width=3, fill=(255, 200, 200))
    draw.text((60, y_offset + 20), "SIMULATED VISUAL DEFECT AREA", fill="red", font=font_large)
    draw.text((60, y_offset + 70), f"Defect Type: {case['defect_type']}", fill="darkred", font=font_medium)
    
    # Draw random visual noise to simulate defect texture
    for _ in range(50):
        x1 = random.randint(40, 760)
        y1 = random.randint(y_offset, y_offset + 180)
        x2 = x1 + random.randint(10, 50)
        y2 = y1 + random.randint(10, 50)
        draw.line([(x1, y1), (x2, y2)], fill="red", width=random.randint(1, 5))

    img.save(os.path.join(output_dir, case['filename']))

for case in test_cases:
    create_image(case)

print(f"Generated 10 test images in {output_dir}")
