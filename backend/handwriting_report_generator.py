from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64
from datetime import datetime

class HandwritingReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )

    def generate_report(self, data):
        """Generate a PDF report from handwriting analysis data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Title
        story.append(Paragraph("Handwriting Analysis Clinical Report", self.title_style))
        story.append(Paragraph(f"Parkinson's Disease Detection - Diagnostic Insights", self.styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))

        # Patient Info
        patient_data = [
            ['Patient Name:', data.get('patient_name', 'Anonymous')],
            ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Diagnostic Status:', data.get('diagnosis', 'N/A')]
        ]
        t = Table(patient_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))

        # Results Summary
        story.append(Paragraph("Diagnostic Summary", self.heading_style))
        story.append(Paragraph(data.get('summary', 'No summary available.'), self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

        # Model Scores
        story.append(Paragraph("Ensemble Model Breakdown", self.heading_style))
        score_data = [['Analysis Method', 'Prediction', 'Confidence', 'Visual']]
        for model, res in data.get('individual_predictions', {}).items():
            conf = res.get('confidence', 0)
            score_data.append([
                model.upper().replace('_', ' '),
                res.get('prediction', 'N/A'),
                f"{conf:.1%}",
                '█' * int(conf * 20)
            ])
        
        st = Table(score_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.8*inch])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        story.append(st)

        doc.build(story)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

handwriting_report_gen = HandwritingReportGenerator()
