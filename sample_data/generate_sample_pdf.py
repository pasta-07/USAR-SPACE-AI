import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_sample_timetable_pdf(output_path: str = "sample_data/USAR_AIML_Timetable_Test.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        name='SubTitleStyle',
        fontName='Helvetica',
        fontSize=10,
        alignment=1,
        spaceAfter=10
    )
    cell_style = ParagraphStyle(
        name='CellStyle',
        fontName='Helvetica',
        fontSize=7,
        leading=8,
        alignment=1
    )
    header_cell_style = ParagraphStyle(
        name='HeaderCellStyle',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9,
        alignment=1
    )

    story = []

    # Title
    story.append(Paragraph("Time Table: Odd Semester 2026-27 (w.e.f. 3rd August, 2026)", title_style))
    story.append(Paragraph("AIML-III_B1 (Department of Artificial Intelligence & Machine Learning)", subtitle_style))

    # Timetable data grid
    headers = [
        Paragraph("", header_cell_style),
        Paragraph("9:00", header_cell_style),
        Paragraph("10:00", header_cell_style),
        Paragraph("11:00", header_cell_style),
        Paragraph("12:00", header_cell_style),
        Paragraph("13:00", header_cell_style),
        Paragraph("14:00", header_cell_style),
        Paragraph("15:00", header_cell_style),
        Paragraph("16:00", header_cell_style),
    ]

    def c(text):
        return Paragraph(text.replace("\n", "<br/>"), cell_style)

    data = [
        headers,
        [
            Paragraph("Mo", header_cell_style),
            c(""),
            c("Priya Dr. Annu<br/>AIML-III-B1-ARM 201<br/>ARM-201<br/>A-601-CR"),
            c("Dalal Dr. Renu<br/>AIML-III-B1-ARM 205<br/>ARM-205<br/>A-601-CR"),
            c("Singh Dr. Amrit Pal<br/>AIML-III-B1-ARM 203<br/>ARM-203<br/>A-601-CR"),
            c(""),
            c("Singh Mr. Neeraj<br/>AIML-III-B1-ARM 209<br/>ARM-209<br/>A-601-CR"),
            c("Jindal Ms. Kanika<br/>AIML-III-B1-ARM 211<br/>ARM-211<br/>A-601-CR"),
            c("Aggarwal Prof. Abha<br/>AIML-III-B1-ARM 213<br/>ARM-213<br/>A-601-CR"),
        ],
        [
            Paragraph("Tu", header_cell_style),
            c(""),
            c("Dalal Dr. Renu<br/>AIML-III-B1-ARM 205<br/>ARM-205<br/>A-209-CR"),
            c("Kumar Dr. Ashok<br/>AIML-III-B1-B-ARM 253<br/>ARM-253<br/>AUB-03-Com Lab"),
            c("Kumar Dr. Ashok<br/>AIML-III-B1-B-ARM 253<br/>ARM-253<br/>AUB-03-Com Lab"),
            c(""),
            c("Singh Dr. Amrit Pal<br/>AIML-III-B1-ARM 203<br/>ARM-203<br/>A-601-CR"),
            c("Singh Mr. Neeraj<br/>AIML-III-B1-ARM 209<br/>ARM-209<br/>A-601-CR"),
            c(""),
        ],
        [
            Paragraph("We", header_cell_style),
            c("Sehgal Dr. Ruchika<br/>AIML-III-B1-ARM 207<br/>ARM-207<br/>A-601-CR"),
            c("Aggarwal Prof. Abha<br/>AIML-III-B1-ARM 213<br/>ARM-213<br/>A-601-CR"),
            c("Singh Dr. Amrit Pal<br/>AIML-III-B1-ARM 203<br/>ARM-203<br/>A-601-CR"),
            c(""),
            c("Singh Dr. Abhishek<br/>AIML-III-B1-A-ARM 253<br/>ARM-253<br/>AUB-03-Com Lab"),
            c("Singh Dr. Abhishek<br/>AIML-III-B1-A-ARM 253<br/>ARM-253<br/>AUB-03-Com Lab"),
            c("Dalal Dr. Renu<br/>AIML-III-B1-ARM 205<br/>ARM-205<br/>A-601-CR"),
            c(""),
        ],
        [
            Paragraph("Th", header_cell_style),
            c(""),
            c(""),
            c("Singh Dr. Amrit Pal<br/>AIML-III-B1-A-ARM 251<br/>ARM-251<br/>A-203-Com Lab"),
            c("Singh Dr. Amrit Pal<br/>AIML-III-B1-A-ARM 251<br/>ARM-251<br/>A-203-Com Lab"),
            c(""),
            c("Jindal Ms. Kanika<br/>AIML-III-B1-ARM 211<br/>ARM-211<br/>A-601-CR"),
            c("Priya Dr. Annu<br/>AIML-III-B1-ARM 201<br/>ARM-201<br/>A-601-CR"),
            c("Sehgal Dr. Ruchika<br/>AIML-III-B1-ARM 207<br/>ARM-207<br/>A-601-CR"),
        ],
        [
            Paragraph("Fr", header_cell_style),
            c(""),
            c(""),
            c("Priya Dr. Annu<br/>AIML-III-B1-ARM 201<br/>ARM-201<br/>A-601-CR"),
            c("Singh Mr. Neeraj<br/>AIML-III-B1-ARM 209<br/>ARM-209<br/>A-601-CR"),
            c("Sehgal Dr. Ruchika<br/>AIML-III-B1-ARM 207<br/>ARM-207<br/>A-601-CR"),
            c(""),
            c(""),
            c(""),
        ]
    ]

    col_widths = [30, 80, 80, 80, 80, 80, 80, 80, 80]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(t)
    doc.build(story)
    print(f"Generated sample timetable PDF at: {output_path}")

if __name__ == "__main__":
    generate_sample_timetable_pdf()
