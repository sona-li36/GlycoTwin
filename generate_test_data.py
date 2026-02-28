import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_clinical_protocol_pdf():
    # Ensure the directory exists
    folder = "./Data of GLP"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, "GLP1_Titration_Protocol.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Clinical Protocol: GLP-1 Titration & Side Effect Management", styles['Title']))
    story.append(Spacer(1, 12))

    # Section 1: Titration Schedule
    story.append(Paragraph("1. Standard Titration Schedule", styles['Heading2']))
    titration_text = (
        "Patients starting Semaglutide should follow a 4-week escalation cycle. "
        "Month 1: 0.25mg weekly. Month 2: 0.5mg weekly. Month 3: 1.0mg weekly. "
        "Month 4: 1.7mg weekly. Maintenance: 2.4mg weekly."
    )
    story.append(Paragraph(titration_text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Section 2: Nausea Management
    story.append(Paragraph("2. Nausea and GI Management", styles['Heading2']))
    nausea_text = (
        "If a patient reports nausea at the 0.5mg dose, the following steps are recommended: "
        "1. Transition to smaller, more frequent meals. "
        "2. Prioritize hydration (at least 2.5L of water daily). "
        "3. Focus on lean protein intake (1.2g per kg of body weight) to maintain muscle mass. "
        "4. If symptoms persist for >72 hours, consider holding the next dose and consulting the prescriber."
    )
    story.append(Paragraph(nausea_text, styles['Normal']))

    # Build the PDF
    doc.build(story)
    print(f"✅ Created clinical protocol at: {file_path}")

if __name__ == "__main__":
    create_clinical_protocol_pdf()