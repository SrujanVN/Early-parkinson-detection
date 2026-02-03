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
        """Generate a professional PDF report from voice analysis data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []

        # Title
        story.append(Paragraph("Acoustic Biomarker Clinical Report", self.title_style))
        story.append(Paragraph(f"Parkinson's Disease Detection System - Voice Analysis", self.styles['Heading3']))
        story.append(Spacer(1, 0.2*inch))

        # Date & Metadata
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        story.append(Paragraph(f"<i>Report generated on: {timestamp}</i>", 
                               ParagraphStyle('Timestamp', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.grey)))
        story.append(Spacer(1, 0.3*inch))

        # Patient Info & Summary
        diagnosis = data.get('diagnosis', 'N/A')
        confidence = data.get('confidence', 0)
        
        # Color indicator based on diagnosis
        status_color = colors.HexColor('#dc2626') if diagnosis == "Parkinson's" else colors.HexColor('#16a34a')
        
        summary_data = [
            ['Patient Information', '', 'Diagnostic Summary', ''],
            ['Name:', data.get('patient_name', 'Anonymous'), 'Status:', diagnosis],
            ['Assessment Type:', 'Isolated Voice', 'Avg Confidence:', f"{confidence:.1%}"],
            ['Stability Index:', f"{data.get('stability_score', 0):.2f}", 'Risk Level:', data.get('risk_level', 'Unknown')]
        ]
        
        st = Table(summary_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#eff6ff')),
            ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (3, 1), (3, 1), status_color),
            ('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold'),
        ]))
        story.append(st)
        story.append(Spacer(1, 0.4*inch))

        # Vocal Biomarker Section
        story.append(Paragraph("Vocal Biomarker Analysis", self.heading_style))
        features = data.get('feature_importance', {})
        stability_score = data.get('stability_score', 0)
        
        biomarker_text = (
            f"The assessment of speech regularity yielded a stability score of <b>{stability_score:.2f}</b>. "
        )
        if data.get('is_stable'):
            biomarker_text += "This indicates high regularity in vocal folds vibration and energy distribution, which is consistent with normal speech control."
        else:
            biomarker_text += "Subtle temporal and spectral irregularities were detected, which are often markers for early-stage motor symptoms affecting speech."
        
        story.append(Paragraph(biomarker_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.15*inch))

        # Features Table
        display_features = [
            ['Acoustic Biomarker', 'Value', 'Reference Range', 'Clinical Significance'],
            ['Pitch (Fo)', f"{features.get('MDVP_Fo_Hz', 0):.1f} Hz", '110-150 Hz', 'Base vocal cord frequency'],
            ['Jitter (Micro-tremors)', f"{features.get('MDVP_Jitter_Percent', 0):.3%}", '< 1.0%', 'Frequency instability'],
            ['Shimmer (Amplitude)', f"{features.get('MDVP_Shimmer_dB', 0):.2f} dB", '< 0.35 dB', 'Volume stability'],
            ['Harmonicty (HNR)', f"{features.get('HNR', 0):.2f}", '> 20.0', 'Voice clarity index'],
        ]
        
        ft = Table(display_features, colWidths=[2.2*inch, 1.3*inch, 1.5*inch, 2.0*inch])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(ft)
        story.append(Spacer(1, 0.4*inch))

        # Model Ensemble Analysis
        story.append(Paragraph("Model Ensemble Analysis (4-Model Breakdown)", self.heading_style))
        model_metrics = data.get('model_metrics', [])
        
        if model_metrics:
            metric_data = [['Analysis Engine', 'Prediction', 'Confidence', 'Accuracy', 'Latency']]
            for m in model_metrics:
                metric_data.append([
                    m.get('name', 'N/A'),
                    m.get('diagnosis', 'N/A'),
                    f"{m.get('probability', 0):.1%}",
                    f"{m.get('accuracy', 0):.1f}%",
                    f"{m.get('latency', 0):.2f}s"
                ])
            
            mt = Table(metric_data, colWidths=[1.8*inch, 1.4*inch, 1.2*inch, 1.3*inch, 1.3*inch])
            mt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.2, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            story.append(mt)
            story.append(Spacer(1, 0.4*inch))

        # Clinical Summary
        story.append(Paragraph("Clinical Analysis Summary", self.heading_style))
        if diagnosis == "Parkinson's":
            summary_text = (
                "The ensemble analysis shows significant acoustic indicators correlated with Parkinson's Disease. "
                "Multiple models have converged on this diagnosis based on frequency instability (Jitter) and vocal stability metrics. "
                "The detected patterns are consistent with vocal cord micro-tremors and reduced volume control often seen in early-to-mid stage neurodegenerative changes."
            )
        else:
            summary_text = (
                "The ensemble analysis indicates vocal patterns within normal clinical thresholds. "
                "No significant indicators of Parkinsonian speech trends were detected by the model ensemble. "
                "Acoustic features such as HNR and Pitch stability remain within healthy variance ranges."
            )
        
        story.append(Paragraph(summary_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Recommendations
        story.append(Paragraph("Recommendations & Next Steps", self.heading_style))
        if diagnosis == "Parkinson's":
            recommendations = [
                "• Immediate consultation with a Neurologist or Movement Disorder Specialist.",
                "• Evaluation by a Speech-Language Pathologist for LSVT LOUD assessment.",
                "• Correlation of these findings with motor symptoms (tremor, bradykinesia).",
                "• Periodic re-testing of vocal biomass markers to track progression."
            ]
        else:
            recommendations = [
                "• Maintenance of vocal hygiene and regular hydration.",
                "• Routine health checkup within 6-12 months.",
                "• Re-test if any noticeable changes in speech clarity or volume occur."
            ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))

        # Footer
        story.append(Spacer(1, 0.6*inch))
        footer_style = ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        story.append(Paragraph("<i>NOTICE: This AI-generated report is for screening purposes and does not constitute a definitive medical diagnosis. Findings should be confirmed by clinical examination.</i>", footer_style))

        doc.build(story)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

voice_report_gen = VoiceReportGenerator()
