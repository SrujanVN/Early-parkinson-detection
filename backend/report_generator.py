"""
PDF Report Generator for Parkinson's Detection
Generates professional medical analysis reports with rich GradCAM and LIME visualizations
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
import base64
import os
from PIL import Image as PILImage


def generate_medical_report(prediction_data, patient_name="You", include_xai=True):
    """
    Generate a professional medical analysis report PDF with XAI visualizations
    
    Args:
        prediction_data: Dict containing prediction results, GradCAM, and LIME
        patient_name: Patient name
        include_xai: Whether to include XAI visualizations
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3498DB'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph("Parkinson's Disease Analysis Report", title_style)
    elements.append(title)
    
    # Date
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    subtitle = Paragraph(f"Generated on {date_str}", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Information and Analysis Results
    diagnosis = prediction_data.get('diagnosis', 'Unknown')
    confidence = prediction_data.get('confidence', 0) * 100
    
    # Color based on diagnosis
    if diagnosis == "Parkinson's":
        result_color = colors.HexColor('#E74C3C')
    elif diagnosis == "Normal":
        result_color = colors.HexColor('#27AE60')
    else:
        result_color = colors.HexColor('#F39C12')
    
    patient_analysis_data = [
        ['Patient Information', '', 'Analysis Results', ''],
        ['Patient Name:', patient_name, 'Diagnosis:', diagnosis],
        ['Analysis Date:', datetime.now().strftime("%m/%d/%Y"), 'Confidence:', f"{confidence:.1f}%"],
        ['', '', 'Status:', 'Completed']
    ]
    
    patient_analysis_table = Table(patient_analysis_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    patient_analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#ECF0F1')),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#ECF0F1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('TEXTCOLOR', (3, 1), (3, 1), result_color),
        ('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold'),
    ]))
    elements.append(patient_analysis_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Class Probabilities
    elements.append(Paragraph("Class Probabilities", heading_style))
    
    class_probs = prediction_data.get('class_probabilities', {})
    prob_data = [
        ['Class', 'Probability', 'Visual'],
        ['Normal', f"{class_probs.get('Normal', 0)*100:.1f}%", '█' * int(class_probs.get('Normal', 0)*20)],
        ["Parkinson's", f"{class_probs.get('Parkinsons', 0)*100:.1f}%", '█' * int(class_probs.get('Parkinsons', 0)*20)],
        ['Unknown', f"{class_probs.get('Unknown', 0)*100:.1f}%", '█' * int(class_probs.get('Unknown', 0)*20)]
    ]
    
    prob_table = Table(prob_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(prob_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Individual Model Predictions
    elements.append(Paragraph("Individual Model Predictions", heading_style))
    
    individual_preds = prediction_data.get('individual_predictions', {})
    model_data = [['Model', 'Prediction', 'Confidence']]
    
    for model_name, pred_info in individual_preds.items():
        model_short = model_name.replace('MRI_', '')
        pred = pred_info.get('prediction', 'N/A')
        conf = pred_info.get('confidence', 0) * 100
        model_data.append([model_short, pred, f"{conf:.1f}%"])
    
    model_table = Table(model_data, colWidths=[2*inch, 2*inch, 2*inch])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(model_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # XAI Visualizations
    if include_xai:
        elements.append(Paragraph("Explainable AI Visualizations", heading_style))
        
        xai_note = Paragraph(
            "<i>Visual explanations showing which brain regions influenced the AI's decision</i>",
            ParagraphStyle('XAINote', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#7f8c8d'))
        )
        elements.append(xai_note)
        elements.append(Spacer(1, 0.1*inch))
        
        # Check if visualizations are available
        gradcam_data = prediction_data.get('gradcam', {})
        lime_data = prediction_data.get('lime', {})
        
        print(f"📄 Report Generator: GradCAM available={gradcam_data.get('available')}")
        print(f"📄 Report Generator: LIME available={lime_data.get('available')}")
        
        viz_elements = []
        
        # GradCAM
        if gradcam_data.get('available', False):
            gradcam_base64 = gradcam_data.get('image_base64', '')
            if gradcam_base64 and gradcam_base64.startswith('data:image'):
                try:
                    # Extract and save image
                    image_data = gradcam_base64.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    temp_gradcam = "temp_gradcam.png"
                    with open(temp_gradcam, 'wb') as f:
                        f.write(image_bytes)
                    
                    viz_elements.append(['GradCAM Heatmap'])
                    viz_elements.append([RLImage(temp_gradcam, width=2.5*inch, height=2.5*inch)])
                    viz_elements.append([Paragraph("<i>Red areas show high AI attention</i>", 
                                                   ParagraphStyle('Caption', parent=styles['Normal'], fontSize=8, textColor=colors.grey))])
                except Exception as e:
                    print(f"Error adding GradCAM: {e}")
        
        # LIME
        if lime_data.get('available', False):
            lime_base64 = lime_data.get('image_base64', '')
            if lime_base64 and lime_base64.startswith('data:image'):
                try:
                    # Extract and save image
                    image_data = lime_base64.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    temp_lime = "temp_lime.png"
                    with open(temp_lime, 'wb') as f:
                        f.write(image_bytes)
                    
                    viz_elements.append(['LIME Feature Importance'])
                    viz_elements.append([RLImage(temp_lime, width=2.5*inch, height=2.5*inch)])
                    viz_elements.append([Paragraph("<i>Green supports, red opposes diagnosis</i>", 
                                                   ParagraphStyle('Caption', parent=styles['Normal'], fontSize=8, textColor=colors.grey))])
                except Exception as e:
                    print(f"Error adding LIME: {e}")
        
        if viz_elements:
            viz_table = Table(viz_elements, colWidths=[6*inch])
            viz_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(viz_table)
        else:
            elements.append(Paragraph("<i>XAI visualizations not available for this analysis</i>", 
                                     ParagraphStyle('NoViz', parent=styles['Normal'], fontSize=9, textColor=colors.grey)))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Analysis Summary
    elements.append(Paragraph("Clinical Analysis Summary", heading_style))
    
    if diagnosis == "Parkinson's":
        summary_text = (
            f"<b>Diagnosis:</b> The ensemble AI model has detected patterns consistent with Parkinson's disease "
            f"with {confidence:.1f}% confidence.<br/><br/>"
            
            "<b>Model Analysis:</b> All four state-of-the-art deep learning models (DenseNet121, "
            "EfficientNet-B0, EfficientNet-B3, and ResNet50) were employed in this analysis. "
            "Each model independently analyzed the MRI scan and contributed to the final ensemble prediction.<br/><br/>"
            
            "<b>XAI Insights:</b> The GradCAM heatmap visualization highlights the specific brain regions "
            "that the AI models focused on when making this prediction. Red and yellow areas indicate "
            "regions of high importance. The LIME feature importance map shows which image features "
            "supported (green) or opposed (red) the Parkinson's diagnosis.<br/><br/>"
            
            "<b>Clinical Significance:</b> The detected patterns are consistent with neurodegeneration "
            "affecting dopamine-producing neurons in the substantia nigra, a hallmark of Parkinson's disease. "
            "The AI has identified subtle changes in brain structure that may indicate early-stage disease.<br/><br/>"
            
            "<b>Recommendations:</b><br/>"
            "• Consult with a movement disorder specialist or neurologist for comprehensive clinical evaluation<br/>"
            "• Consider additional diagnostic tests (DaTscan, clinical motor assessment, genetic testing)<br/>"
            "• Early intervention may help manage symptoms and slow disease progression<br/>"
            "• Regular monitoring and follow-up imaging recommended<br/><br/>"
            
            "<b>Important Note:</b> This AI analysis is a screening tool and should not replace professional "
            "medical diagnosis. A qualified neurologist should review these findings in conjunction with "
            "clinical symptoms, medical history, and physical examination."
        )
    elif diagnosis == "Normal":
        summary_text = (
            f"<b>Diagnosis:</b> The ensemble AI model indicates normal brain imaging patterns "
            f"with {confidence:.1f}% confidence.<br/><br/>"
            
            "<b>Model Analysis:</b> All four deep learning models (DenseNet121, EfficientNet-B0, "
            "EfficientNet-B3, and ResNet50) independently analyzed the MRI scan. No significant "
            "patterns associated with Parkinson's disease were detected.<br/><br/>"
            
            "<b>XAI Insights:</b> The GradCAM and LIME visualizations show the brain regions analyzed "
            "by the AI system. The models did not identify abnormal patterns typically associated with "
            "neurodegeneration or Parkinson's disease.<br/><br/>"
            
            "<b>Clinical Significance:</b> The brain structure appears normal with no visible signs of "
            "dopaminergic neuron loss or other Parkinson's-related changes. This suggests healthy brain "
            "tissue without evidence of neurodegenerative disease.<br/><br/>"
            
            "<b>Recommendations:</b><br/>"
            "• Continue regular health monitoring as part of preventive care<br/>"
            "• Maintain a healthy lifestyle with regular exercise and balanced diet<br/>"
            "• If symptoms develop, consult a healthcare provider promptly<br/>"
            "• Consider periodic screening if family history of Parkinson's disease exists<br/><br/>"
            
            "<b>Note:</b> While the AI analysis shows normal patterns, this does not rule out very early-stage "
            "disease that may not yet be visible on imaging. Clinical correlation is always recommended."
        )
    else:
        summary_text = (
            f"<b>Diagnosis:</b> The AI model's confidence level is {confidence:.1f}%, which is below "
            "the clinical threshold for a definitive diagnosis.<br/><br/>"
            
            "<b>Model Analysis:</b> The four deep learning models showed mixed or uncertain predictions, "
            "suggesting the imaging patterns do not clearly match either normal or Parkinson's disease profiles.<br/><br/>"
            
            "<b>Possible Reasons:</b><br/>"
            "• Image quality or artifacts affecting analysis<br/>"
            "• Very early-stage disease with subtle changes<br/>"
            "• Atypical presentation requiring expert review<br/>"
            "• Other neurological conditions with similar imaging patterns<br/><br/>"
            
            "<b>Recommendations:</b><br/>"
            "• <b>Strongly recommended:</b> Consult with a neurologist for expert evaluation<br/>"
            "• Consider repeat imaging with optimized protocols<br/>"
            "• Additional diagnostic tests may be warranted (DaTscan, clinical assessment)<br/>"
            "• Do not delay seeking professional medical advice<br/><br/>"
            
            "<b>Important:</b> An inconclusive AI result requires professional medical review. "
            "A neurologist can provide comprehensive evaluation combining clinical symptoms, "
            "physical examination, and additional diagnostic tests."
        )
    
    summary = Paragraph(summary_text, styles['Normal'])
    elements.append(summary)
    
    # Footer note
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    footer = Paragraph(
        "<i>This report is generated by AI and should be reviewed by a qualified medical professional.</i>",
        footer_style
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Clean up temp files
    try:
        if os.path.exists("temp_gradcam.png"):
            os.remove("temp_gradcam.png")
        if os.path.exists("temp_lime.png"):
            os.remove("temp_lime.png")
    except:
        pass
    
    buffer.seek(0)
    return buffer
