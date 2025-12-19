"""
FastAPI Backend for Multi-Modal Parkinson's Disease Detection
Supports: MRI images, Handwriting images, Voice audio, CSV features
Includes: Ensemble predictions, XAI (GradCAM, LIME), PDF reports, AI Chatbot
"""

import os
import io
import base64
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from PIL import Image
import cv2
import librosa
import joblib

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models as torchvision_models
import timm

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# XAI imports
from captum.attr import GradCAM
from lime import lime_image
from lime.wrappers.scikit_image import SegmentationAlgorithm

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Gemini AI
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL VARIABLES FOR MODELS
# ============================================================================
MRI_MODELS = {}
HANDWRITING_MODELS = {}
VOICE_MODELS = {}
CSV_MODEL = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GEMINI_MODEL = None

# Model paths
BASE_MODEL_PATH = "models"
MRI_PATH = os.path.join(BASE_MODEL_PATH, "Parkinson_mri")
HANDWRITING_PATH = os.path.join(BASE_MODEL_PATH, "Parkinson_handwriting")
VOICE_PATH = os.path.join(BASE_MODEL_PATH, "parkinsons_voice")
CSV_PATH = os.path.join(BASE_MODEL_PATH, "parkinsions_csv")

# Class mappings
CLASS_NAMES = {0: "Normal", 1: "Parkinson's", 2: "Unknown"}
BINARY_CLASS_NAMES = {0: "Normal", 1: "Parkinson's"}

# CSV feature names (22 features from Parkinson's dataset)
CSV_FEATURES = [
    "MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)", "MDVP:Jitter(%)", 
    "MDVP:Jitter(Abs)", "MDVP:RAP", "MDVP:PPQ", "Jitter:DDP",
    "MDVP:Shimmer", "MDVP:Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5",
    "MDVP:APQ", "Shimmer:DDA", "NHR", "HNR", "RPDE", "DFA",
    "spread1", "spread2", "D2", "PPE"
]

# ============================================================================
# PYTORCH MODEL ARCHITECTURES
# ============================================================================

def create_resnet50(num_classes=3):
    """Create ResNet50 model for Parkinson's detection"""
    model = torchvision_models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

def create_densenet121(num_classes=3):
    """Create DenseNet121 model for Parkinson's detection"""
    model = torchvision_models.densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, num_classes)
    return model

def create_efficientnet_b0(num_classes=3):
    """Create EfficientNet-B0 model for Parkinson's detection"""
    model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=num_classes)
    return model

def create_efficientnet_b3(num_classes=3):
    """Create EfficientNet-B3 model for Parkinson's detection"""
    model = timm.create_model('efficientnet_b3', pretrained=False, num_classes=num_classes)
    return model

# ============================================================================
# MODEL LOADING FUNCTIONS
# ============================================================================

def load_mri_models():
    """Load all PyTorch MRI models"""
    global MRI_MODELS
    logger.info("Loading MRI models...")
    
    try:
        # ResNet50
        model_resnet = create_resnet50(num_classes=3)
        model_resnet.load_state_dict(torch.load(
            os.path.join(MRI_PATH, "best_resnet50.pth"),
            map_location=DEVICE
        ))
        model_resnet.to(DEVICE)
        model_resnet.eval()
        MRI_MODELS['resnet50'] = model_resnet
        logger.info("✓ ResNet50 loaded")
        
        # DenseNet121
        model_densenet = create_densenet121(num_classes=3)
        model_densenet.load_state_dict(torch.load(
            os.path.join(MRI_PATH, "best_densenet121.pth"),
            map_location=DEVICE
        ))
        model_densenet.to(DEVICE)
        model_densenet.eval()
        MRI_MODELS['densenet121'] = model_densenet
        logger.info("✓ DenseNet121 loaded")
        
        # EfficientNet-B0
        model_effb0 = create_efficientnet_b0(num_classes=3)
        model_effb0.load_state_dict(torch.load(
            os.path.join(MRI_PATH, "best_efficientnet_b0.pth"),
            map_location=DEVICE
        ))
        model_effb0.to(DEVICE)
        model_effb0.eval()
        MRI_MODELS['efficientnet_b0'] = model_effb0
        logger.info("✓ EfficientNet-B0 loaded")
        
        # EfficientNet-B3
        model_effb3 = create_efficientnet_b3(num_classes=3)
        model_effb3.load_state_dict(torch.load(
            os.path.join(MRI_PATH, "best_efficientnet_b3.pth"),
            map_location=DEVICE
        ))
        model_effb3.to(DEVICE)
        model_effb3.eval()
        MRI_MODELS['efficientnet_b3'] = model_effb3
        logger.info("✓ EfficientNet-B3 loaded")
        
        logger.info(f"Successfully loaded {len(MRI_MODELS)} MRI models")
    except Exception as e:
        logger.error(f"Error loading MRI models: {e}")
        raise

def load_handwriting_models():
    """Load all handwriting models (sklearn/XGBoost)"""
    global HANDWRITING_MODELS
    logger.info("Loading Handwriting models...")
    
    try:
        HANDWRITING_MODELS['ensemble'] = joblib.load(
            os.path.join(HANDWRITING_PATH, "parkinson_ensemble_open_set.pkl")
        )
        HANDWRITING_MODELS['hog_svm'] = joblib.load(
            os.path.join(HANDWRITING_PATH, "hog_svm_open_set.pkl")
        )
        HANDWRITING_MODELS['lbp_rf'] = joblib.load(
            os.path.join(HANDWRITING_PATH, "lbp_rf_open_set.pkl")
        )
        HANDWRITING_MODELS['mobilenet_svm'] = joblib.load(
            os.path.join(HANDWRITING_PATH, "mobilenet_svm_open_set.pkl")
        )
        logger.info(f"✓ Successfully loaded {len(HANDWRITING_MODELS)} handwriting models")
    except Exception as e:
        logger.error(f"Error loading handwriting models: {e}")
        raise

def load_voice_models():
    """Load all voice models (sklearn/XGBoost)"""
    global VOICE_MODELS
    logger.info("Loading Voice models...")
    
    try:
        VOICE_MODELS['ensemble'] = joblib.load(
            os.path.join(VOICE_PATH, "ensemble_parkinson_voice.pkl")
        )
        VOICE_MODELS['random_forest'] = joblib.load(
            os.path.join(VOICE_PATH, "random_forest_parkinson_voice.pkl")
        )
        VOICE_MODELS['svm'] = joblib.load(
            os.path.join(VOICE_PATH, "svm_parkinson_voice.pkl")
        )
        VOICE_MODELS['xgboost'] = joblib.load(
            os.path.join(VOICE_PATH, "xgboost_parkinson_voice.pkl")
        )
        logger.info(f"✓ Successfully loaded {len(VOICE_MODELS)} voice models")
    except Exception as e:
        logger.error(f"Error loading voice models: {e}")
        raise

def load_csv_model():
    """Load CSV XGBoost model"""
    global CSV_MODEL
    logger.info("Loading CSV model...")
    
    try:
        CSV_MODEL = joblib.load(
            os.path.join(CSV_PATH, "parkinson_xgboost.pkl")
        )
        logger.info("✓ Successfully loaded CSV XGBoost model")
    except Exception as e:
        logger.error(f"Error loading CSV model: {e}")
        raise

def initialize_gemini():
    """Initialize Gemini AI chatbot"""
    global GEMINI_MODEL
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return
        
        genai.configure(api_key=api_key)
        GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("✓ Gemini AI initialized")
    except Exception as e:
        logger.error(f"Error initializing Gemini: {e}")

# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models on startup"""
    logger.info("="*60)
    logger.info("Starting Parkinson's Detection API Server")
    logger.info(f"Device: {DEVICE}")
    logger.info("="*60)
    
    # Load all models
    load_mri_models()
    load_handwriting_models()
    load_voice_models()
    load_csv_model()
    initialize_gemini()
    
    logger.info("="*60)
    logger.info("All models loaded successfully!")
    logger.info("="*60)
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Parkinson's Disease Detection API",
    description="Multi-modal AI system for early Parkinson's disease detection",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CSVPredictionRequest(BaseModel):
    features: Dict[str, float]
    patient_name: Optional[str] = "Anonymous"

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

# ============================================================================
# IMAGE PREPROCESSING
# ============================================================================

def preprocess_image_pytorch(image_bytes: bytes) -> torch.Tensor:
    """Preprocess image for PyTorch models"""
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return transform(image).unsqueeze(0).to(DEVICE)

def preprocess_image_numpy(image_bytes: bytes) -> np.ndarray:
    """Preprocess image to numpy array for sklearn models"""
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize((224, 224))
    return np.array(image)

# ============================================================================
# AUDIO PREPROCESSING
# ============================================================================

def extract_audio_features(audio_bytes: bytes) -> np.ndarray:
    """Extract MFCC features from audio"""
    try:
        # Load audio
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050)
        
        # Extract MFCCs (matching the 22 features from training)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=22)
        mfccs_mean = np.mean(mfccs.T, axis=0)
        
        return mfccs_mean.reshape(1, -1)
    except Exception as e:
        logger.error(f"Error extracting audio features: {e}")
        raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")

# ============================================================================
# XAI FUNCTIONS
# ============================================================================

def generate_gradcam(model, input_tensor: torch.Tensor, target_class: int = 1) -> str:
    """Generate GradCAM heatmap and return as base64"""
    try:
        # Determine the target layer based on model type
        if 'resnet' in str(type(model)).lower():
            target_layer = model.layer4[-1]
        elif 'densenet' in str(type(model)).lower():
            target_layer = model.features[-1]
        elif 'efficientnet' in str(type(model)).lower():
            # For timm models
            target_layer = model.blocks[-1][-1]
        else:
            raise ValueError("Unsupported model type for GradCAM")
        
        # Create GradCAM
        gradcam = GradCAM(model, target_layer)
        
        # Generate attribution
        attributions = gradcam.attribute(input_tensor, target=target_class)
        
        # Convert to heatmap
        attr_np = attributions.squeeze().cpu().detach().numpy()
        attr_np = np.maximum(attr_np, 0)
        attr_np = attr_np / (attr_np.max() + 1e-8)
        
        # Resize to original image size
        heatmap = cv2.resize(attr_np, (224, 224))
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        # Convert original image
        orig_img = input_tensor.squeeze().cpu().detach().numpy()
        orig_img = np.transpose(orig_img, (1, 2, 0))
        orig_img = (orig_img * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])) * 255
        orig_img = np.uint8(np.clip(orig_img, 0, 255))
        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_RGB2BGR)
        
        # Overlay
        overlay = cv2.addWeighted(orig_img, 0.6, heatmap, 0.4, 0)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', overlay)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
    
    except Exception as e:
        logger.error(f"GradCAM generation error: {e}")
        return None

def generate_lime_explanation(image_np: np.ndarray, predict_fn) -> str:
    """Generate LIME explanation and return as base64"""
    try:
        explainer = lime_image.LimeImageExplainer()
        
        explanation = explainer.explain_instance(
            image_np,
            predict_fn,
            top_labels=2,
            hide_color=0,
            num_samples=100
        )
        
        # Get image and mask
        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0],
            positive_only=True,
            num_features=10,
            hide_rest=False
        )
        
        # Create visualization
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        ax.imshow(temp)
        ax.axis('off')
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    
    except Exception as e:
        logger.error(f"LIME generation error: {e}")
        return None

# ============================================================================
# PDF REPORT GENERATION
# ============================================================================

def generate_pdf_report(
    patient_name: str,
    diagnosis: str,
    confidence: float,
    individual_preds: Dict,
    summary: str,
    modality: str,
    gradcam_base64: Optional[str] = None,
    lime_base64: Optional[str] = None,
    chart_base64: Optional[str] = None
) -> str:
    """Generate PDF report and return as base64"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Medical Analysis Report", title_style))
        story.append(Paragraph(f"Parkinson's Disease Detection - {modality}", styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", heading_style))
        patient_data = [
            ['Patient Name:', patient_name],
            ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Modality:', modality]
        ]
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analysis Results
        story.append(Paragraph("Analysis Results", heading_style))
        results_data = [
            ['Diagnosis:', diagnosis],
            ['Confidence:', f"{confidence:.2%}"],
            ['Recommendation:', 'Consult neurologist for further evaluation' if diagnosis == "Parkinson's" else 'Continue regular monitoring']
        ]
        results_table = Table(results_data, colWidths=[2*inch, 4*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(results_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Ensemble Analysis
        story.append(Paragraph("Ensemble Model Analysis", heading_style))
        ensemble_data = [['Model', 'Prediction', 'Confidence']]
        for model_name, pred_info in individual_preds.items():
            ensemble_data.append([
                model_name,
                pred_info.get('prediction', 'N/A'),
                f"{pred_info.get('confidence', 0):.2%}"
            ])
        
        ensemble_table = Table(ensemble_data, colWidths=[2*inch, 2*inch, 2*inch])
        ensemble_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(ensemble_table)
        story.append(Spacer(1, 0.3*inch))
        
        # XAI Visualizations (if available)
        if gradcam_base64 or lime_base64:
            story.append(PageBreak())
            story.append(Paragraph("XAI Visualizations", heading_style))
            
            if gradcam_base64:
                # Save GradCAM image temporarily
                gradcam_data = base64.b64decode(gradcam_base64.split(',')[1])
                gradcam_img = RLImage(io.BytesIO(gradcam_data), width=4*inch, height=4*inch)
                story.append(Paragraph("GradCAM Heatmap", styles['Heading4']))
                story.append(gradcam_img)
                story.append(Spacer(1, 0.2*inch))
            
            if lime_base64:
                lime_data = base64.b64decode(lime_base64.split(',')[1])
                lime_img = RLImage(io.BytesIO(lime_data), width=4*inch, height=4*inch)
                story.append(Paragraph("LIME Feature Importance", styles['Heading4']))
                story.append(lime_img)
                story.append(Spacer(1, 0.2*inch))
        
        # Chart (if available)
        if chart_base64:
            chart_data = base64.b64decode(chart_base64.split(',')[1])
            chart_img = RLImage(io.BytesIO(chart_data), width=5*inch, height=3*inch)
            story.append(Paragraph("Feature Analysis Chart", styles['Heading4']))
            story.append(chart_img)
            story.append(Spacer(1, 0.2*inch))
        
        # Summary
        story.append(PageBreak())
        story.append(Paragraph("Analysis Summary", heading_style))
        story.append(Paragraph(summary, styles['BodyText']))
        
        # Build PDF
        doc.build(story)
        
        # Convert to base64
        buffer.seek(0)
        pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return pdf_base64
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.post("/predict/mri")
async def predict_mri(
    file: UploadFile = File(...),
    patient_name: str = Form("Anonymous")
):
    """MRI/CT Scan prediction with ensemble models and XAI"""
    try:
        # Read image
        image_bytes = await file.read()
        
        # Preprocess
        input_tensor = preprocess_image_pytorch(image_bytes)
        image_np = preprocess_image_numpy(image_bytes)
        
        # Ensemble prediction
        all_probs = []
        individual_preds = {}
        
        with torch.no_grad():
            for model_name, model in MRI_MODELS.items():
                output = model(input_tensor)
                probs = torch.softmax(output, dim=1).cpu().numpy()[0]
                pred_class = np.argmax(probs)
                
                all_probs.append(probs)
                individual_preds[model_name] = {
                    'prediction': CLASS_NAMES[pred_class],
                    'confidence': float(probs[pred_class]),
                    'probabilities': {CLASS_NAMES[i]: float(probs[i]) for i in range(len(probs))}
                }
        
        # Ensemble: Average probabilities
        ensemble_probs = np.mean(all_probs, axis=0)
        ensemble_class = np.argmax(ensemble_probs)
        diagnosis = CLASS_NAMES[ensemble_class]
        confidence = float(ensemble_probs[ensemble_class])
        
        # Generate XAI
        gradcam_base64 = generate_gradcam(
            list(MRI_MODELS.values())[0],  # Use first model for GradCAM
            input_tensor,
            target_class=ensemble_class
        )
        
        # LIME (simplified for speed)
        lime_base64 = None  # Can be enabled if needed
        
        # Generate summary
        summary = f"The MRI analysis indicates patterns {'consistent with' if diagnosis == 'Parkinsons' else 'not consistent with'} Parkinson's disease with {confidence:.1%} confidence. "
        summary += f"The ensemble of {len(MRI_MODELS)} deep learning models analyzed the brain imaging data. "
        if diagnosis == "Parkinson's":
            summary += "Recommend consultation with a neurologist for comprehensive clinical evaluation and confirmation."
        else:
            summary += "Continue regular health monitoring and follow-up as recommended by your healthcare provider."
        
        # Generate PDF report
        pdf_base64 = generate_pdf_report(
            patient_name=patient_name,
            diagnosis=diagnosis,
            confidence=confidence,
            individual_preds=individual_preds,
            summary=summary,
            modality="MRI/CT Scan",
            gradcam_base64=gradcam_base64,
            lime_base64=lime_base64
        )
        
        return JSONResponse(content={
            'diagnosis': diagnosis,
            'confidence': confidence,
            'individual_predictions': individual_preds,
            'ensemble_info': {
                'num_models': len(MRI_MODELS),
                'ensemble_probabilities': {CLASS_NAMES[i]: float(ensemble_probs[i]) for i in range(len(ensemble_probs))},
                'std_dev': float(np.std(all_probs, axis=0)[ensemble_class])
            },
            'summary': summary,
            'xai_images': {
                'gradcam_base64': gradcam_base64,
                'lime_base64': lime_base64
            },
            'report_pdf_base64': pdf_base64
        })
    
    except Exception as e:
        logger.error(f"MRI prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/handwriting")
async def predict_handwriting(
    file: UploadFile = File(...),
    patient_name: str = Form("Anonymous")
):
    """Handwriting analysis prediction"""
    try:
        # Read and preprocess image
        image_bytes = await file.read()
        image_np = preprocess_image_numpy(image_bytes)
        
        # Feature extraction (simplified - actual models may need specific features)
        # For demonstration, we'll flatten the image
        features = image_np.flatten().reshape(1, -1)
        
        # Ensemble prediction
        individual_preds = {}
        all_preds = []
        
        for model_name, model in HANDWRITING_MODELS.items():
            try:
                pred = model.predict(features)[0]
                prob = model.predict_proba(features)[0] if hasattr(model, 'predict_proba') else [0.5, 0.5]
                
                # Handle open-set (-1 = unknown)
                if pred == -1:
                    pred_class = 2  # Unknown
                else:
                    pred_class = int(pred)
                
                all_preds.append(pred_class)
                individual_preds[model_name] = {
                    'prediction': CLASS_NAMES.get(pred_class, 'Unknown'),
                    'confidence': float(max(prob)) if hasattr(prob, '__iter__') else 0.5
                }
            except Exception as e:
                logger.warning(f"Model {model_name} prediction failed: {e}")
                continue
        
        # Ensemble: Majority voting
        if all_preds:
            ensemble_class = max(set(all_preds), key=all_preds.count)
            diagnosis = CLASS_NAMES.get(ensemble_class, 'Unknown')
            confidence = all_preds.count(ensemble_class) / len(all_preds)
        else:
            diagnosis = "Unknown"
            confidence = 0.0
        
        summary = f"Handwriting analysis {'suggests' if diagnosis == 'Parkinsons' else 'does not suggest'} Parkinson's disease patterns with {confidence:.1%} agreement among models."
        
        # Generate PDF
        pdf_base64 = generate_pdf_report(
            patient_name=patient_name,
            diagnosis=diagnosis,
            confidence=confidence,
            individual_preds=individual_preds,
            summary=summary,
            modality="Handwriting Analysis"
        )
        
        return JSONResponse(content={
            'diagnosis': diagnosis,
            'confidence': confidence,
            'individual_predictions': individual_preds,
            'summary': summary,
            'report_pdf_base64': pdf_base64
        })
    
    except Exception as e:
        logger.error(f"Handwriting prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/voice")
async def predict_voice(
    file: UploadFile = File(...),
    patient_name: str = Form("Anonymous")
):
    """Voice audio analysis prediction"""
    try:
        # Read audio
        audio_bytes = await file.read()
        
        # Extract features
        features = extract_audio_features(audio_bytes)
        
        # Ensemble prediction
        individual_preds = {}
        all_preds = []
        all_probs = []
        
        for model_name, model in VOICE_MODELS.items():
            try:
                pred = model.predict(features)[0]
                prob = model.predict_proba(features)[0] if hasattr(model, 'predict_proba') else [0.5, 0.5]
                
                all_preds.append(int(pred))
                all_probs.append(prob)
                
                individual_preds[model_name] = {
                    'prediction': BINARY_CLASS_NAMES[int(pred)],
                    'confidence': float(max(prob)) if hasattr(prob, '__iter__') else 0.5
                }
            except Exception as e:
                logger.warning(f"Model {model_name} prediction failed: {e}")
                continue
        
        # Ensemble: Average probabilities
        if all_probs:
            ensemble_probs = np.mean(all_probs, axis=0)
            ensemble_class = np.argmax(ensemble_probs)
            diagnosis = BINARY_CLASS_NAMES[ensemble_class]
            confidence = float(ensemble_probs[ensemble_class])
        else:
            diagnosis = "Unknown"
            confidence = 0.0
        
        summary = f"Voice analysis indicates {'patterns consistent with' if diagnosis == 'Parkinsons' else 'no significant patterns of'} Parkinson's disease with {confidence:.1%} confidence."
        
        # Generate PDF
        pdf_base64 = generate_pdf_report(
            patient_name=patient_name,
            diagnosis=diagnosis,
            confidence=confidence,
            individual_preds=individual_preds,
            summary=summary,
            modality="Voice Analysis"
        )
        
        return JSONResponse(content={
            'diagnosis': diagnosis,
            'confidence': confidence,
            'individual_predictions': individual_preds,
            'summary': summary,
            'report_pdf_base64': pdf_base64
        })
    
    except Exception as e:
        logger.error(f"Voice prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/csv")
async def predict_csv(request: CSVPredictionRequest):
    """CSV feature-based prediction"""
    try:
        # Validate features
        missing_features = [f for f in CSV_FEATURES if f not in request.features]
        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Missing features: {missing_features}"
            )
        
        # Prepare feature vector
        feature_vector = np.array([[request.features[f] for f in CSV_FEATURES]])
        
        # Prediction
        pred = CSV_MODEL.predict(feature_vector)[0]
        prob = CSV_MODEL.predict_proba(feature_vector)[0]
        
        diagnosis = BINARY_CLASS_NAMES[int(pred)]
        confidence = float(prob[int(pred)])
        
        # Create feature importance chart
        try:
            feature_importance = CSV_MODEL.feature_importances_
            top_features_idx = np.argsort(feature_importance)[-10:][::-1]
            
            plt.figure(figsize=(10, 6))
            plt.barh([CSV_FEATURES[i] for i in top_features_idx], 
                    feature_importance[top_features_idx])
            plt.xlabel('Importance')
            plt.title('Top 10 Feature Importance')
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            chart_base64 = f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
        except:
            chart_base64 = None
        
        summary = f"Clinical feature analysis indicates {diagnosis} with {confidence:.1%} confidence based on voice biomarker measurements."
        
        # Generate PDF
        pdf_base64 = generate_pdf_report(
            patient_name=request.patient_name,
            diagnosis=diagnosis,
            confidence=confidence,
            individual_preds={'XGBoost': {'prediction': diagnosis, 'confidence': confidence}},
            summary=summary,
            modality="Clinical Features (CSV)",
            chart_base64=chart_base64
        )
        
        return JSONResponse(content={
            'diagnosis': diagnosis,
            'confidence': confidence,
            'probabilities': {BINARY_CLASS_NAMES[i]: float(prob[i]) for i in range(len(prob))},
            'summary': summary,
            'chart_base64': chart_base64,
            'report_pdf_base64': pdf_base64
        })
    
    except Exception as e:
        logger.error(f"CSV prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHATBOT ENDPOINT
# ============================================================================

@app.post("/chat")
async def chat(request: ChatRequest):
    """Gemini AI chatbot for Parkinson's disease information"""
    try:
        if not GEMINI_MODEL:
            raise HTTPException(
                status_code=503,
                detail="Gemini AI not initialized. Please set GEMINI_API_KEY environment variable."
            )
        
        # Build conversation context
        context = "You are a medical AI assistant specializing in Parkinson's disease. Provide helpful, accurate information while reminding users to consult healthcare professionals for medical advice.\n\n"
        
        if request.history:
            for msg in request.history:
                context += f"{msg['role']}: {msg['content']}\n"
        
        context += f"User: {request.message}\nAssistant:"
        
        # Generate response
        response = GEMINI_MODEL.generate_content(context)
        
        return JSONResponse(content={
            'response': response.text,
            'model': 'gemini-1.5-flash'
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'Parkinsons Disease Detection API',
        'version': '2.0.0',
        'models_loaded': {
            'mri': len(MRI_MODELS),
            'handwriting': len(HANDWRITING_MODELS),
            'voice': len(VOICE_MODELS),
            'csv': 1 if CSV_MODEL else 0
        },
        'device': str(DEVICE),
        'gemini_available': GEMINI_MODEL is not None
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return await root()

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
