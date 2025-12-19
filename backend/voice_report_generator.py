from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64
from datetime import datetime

class VoiceReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'), # blue-600
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        )

    def generate_report(self, data):
        """Generate a PDF report from voice analysis data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Title
        story.append(Paragraph("Voice/Speech Analysis Clinical Report", self.title_style))
        story.append(Paragraph(f"Parkinson's Disease Detection - Isolated Voice Assessment", self.styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))

        # Patient Info
        patient_data = [
            ['Patient Name:', data.get('patient_name', 'Anonymous')],
            ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Diagnostic Status:', data.get('diagnosis', 'N/A')],
            ['Confidence Score:', f"{data.get('confidence', 0):.1%}"]
        ]
        t = Table(patient_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))

        # Vocal Stability Assessment
        story.append(Paragraph("Vocal Stability Assessment", self.heading_style))
        stability_text = f"The automated assessment of speech regularity resulted in a stability score of <b>{data.get('stability_score', 0):.2f}</b>. "
        if data.get('is_stable'):
            stability_text += "The speech patterns show high regularity and stability, which is typically observed in healthy controls."
        else:
            stability_text += "Subtle irregularities in speech cadence or energy stability were detected, which may correlate with early Parkinsonian speech trends."
        
        story.append(Paragraph(stability_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

        # Acoustic Features
        story.append(Paragraph("Key Acoustic Feature Analysis", self.heading_style))
        features = data.get('feature_importance', {}) # Using actual values
        
        # Select representative features for report
        display_features = [
            ['Feature Group', 'Value', 'Clinical Significance'],
            ['Avg Fundamental Freq (Fo)', f"{features.get('MDVP_Fo_Hz', 0):.2f} Hz", 'Mean pitch level'],
            ['Jitter (%)', f"{features.get('MDVP_Jitter_Percent', 0):.2f}%", 'Freq instability (Micro-tremors)'],
            ['Shimmer (dB)', f"{features.get('MDVP_Shimmer_dB', 0):.2f} dB", 'Amplitude variation'],
            ['HNR', f"{features.get('HNR', 0):.2f}", 'Harmonic-to-noise ratio'],
            ['Stability Score', f"{data.get('stability_score', 0):.2f}", 'Speech regularity index']
        ]
        
        ft = Table(display_features, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        story.append(ft)
        story.append(Spacer(1, 0.4*inch))

        # Model Performance Metrics
        story.append(Paragraph("Model Performance & Execution Metrics", self.heading_style))
        model_metrics = data.get('model_metrics', [])
        if model_metrics:
            metric_data = [['Analysis Engine', 'Accuracy', 'Latency', 'Status']]
            for m in model_metrics:
                metric_data.append([
                    m.get('name', 'N/A'),
                    f"{m.get('accuracy', 0):.1f}%",
                    f"{m.get('latency', 0):.2f}s",
                    m.get('status', 'N/A')
                ])
            
            mt = Table(metric_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
            mt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eff6ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            story.append(mt)
            story.append(Spacer(1, 0.4*inch))

        # Recommendations
        story.append(Paragraph("Clinical Recommendations", self.heading_style))
        if data.get('diagnosis') == "Parkinson's":
            recommendations = [
                "• Consultation with a Speech-Language Pathologist (SLP) for detailed evaluation.",
                "• Lee Silverman Voice Treatment (LSVT LOUD) assessment may be beneficial.",
                "• Regular monitoring of vocal loudness and speech clarity.",
                "• Neurological follow-up regarding motor control aspects of speech."
            ]
        else:
            recommendations = [
                "• Continue regular health screenings.",
                "• Maintaining vocal health through hydration and avoiding vocal strain.",
                "• Re-test in 6-12 months if any changes are noted by family or patient."
            ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

voice_report_gen = VoiceReportGenerator()
