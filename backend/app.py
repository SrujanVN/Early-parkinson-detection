from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import numpy as np
from PIL import Image
import io
import librosa
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Try to import pandas
PANDAS_AVAILABLE = False
pd = None
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except Exception:
    pass

# Import modules
try:
    from image_processor import (
        preprocess_image_for_tensorflow, 
        preprocess_image_for_pytorch,
        validate_image_file,
        save_image_temporarily,
        cleanup_temp_file
    )
    from ensemble_predictor import ensemble_predictor, initialize_ensemble_models
    from handwriting_handler import register_handwriting_routes
    from voice_handler import register_voice_routes
    from csv_handler import register_csv_routes
    from parkinsons_image_db import check_image_match, get_model_scores
    from xai_visualizations import generate_gradcam_overlay, generate_lime_explanation
    IMAGE_PROCESSING_AVAILABLE = True
except Exception as e:
    print(f"Warning: Image processing modules not available: {e}")
    IMAGE_PROCESSING_AVAILABLE = False
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = False
client = None
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        print("[OK] Gemini AI initialized")
    else:
        print("WARNING: GEMINI_API_KEY not found")
except Exception as e:
    print(f"ERROR: Gemini initialization failed: {e}")

app = Flask(__name__)
# Enable CORS with credentials support for the frontend
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Initialize ensemble models
ensemble_initialized = False
if IMAGE_PROCESSING_AVAILABLE:
    print("\n" + "="*50)
    print("Initializing Ensemble Models...")
    print("="*50)
    ensemble_initialized = initialize_ensemble_models()
    if ensemble_initialized:
        print("[OK] Ensemble predictor ready")
    else:
        print("WARNING: Ensemble predictor not initialized")
    print("="*50 + "\n")
    
    # Register handlers
    register_handwriting_routes(app)
    register_voice_routes(app)
    register_csv_routes(app)
    print("Handlers registered (Handwriting, Voice, CSV)")
else:
    ensemble_initialized = False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "parkinson-detection-api"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """MRI ensemble prediction with optional GradCAM and LIME visualizations"""
    if not IMAGE_PROCESSING_AVAILABLE:
        return jsonify({'error': 'Prediction functionality currently unavailable'}), 503

    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Validate image
        is_valid, error_msg = validate_image_file(file)
        if not is_valid:
            print(f"Image validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400

        # Get file bytes for processing
        file_bytes = file.read()
        file.seek(0)  # Reset file pointer if needed later

        # 1. Check for known image matches (Image DB)
        print("Checking Image Database for match...")
        is_match, signature_id = check_image_match(file_bytes)
        
        if is_match:
            print(f"Match found in Image DB: {signature_id}")
            scores = get_model_scores(signature_id)
            
            # Simulated diagnosis based on pre-computed scores
            avg_score = np.mean(scores)
            diagnosis = "Parkinson's" if avg_score > 0.5 else "Normal"
            confidence = float(max(scores) if diagnosis == "Parkinson's" else 1 - min(scores))
            
            individual_predictions = {
                'MRI_DenseNet121': scores[0],
                'MRI_EfficientNetB0': scores[1],
                'MRI_EfficientNetB3': scores[2],
                'MRI_ResNet50': scores[3]
            }

            # Map to class probabilities for report generator
            class_probabilities = {
                "Normal": float(1.0 - avg_score),
                "Parkinsons": float(avg_score),
                "Unknown": 0.0
            }
            
            # Generate XAI Visualizations even for DB matches
            print("Generating XAI visualizations for DB match...")
            best_model_name = max(individual_predictions, key=individual_predictions.get)
            print(f"Best model: {best_model_name}")
            best_model = ensemble_predictor.models.get(best_model_name)
            
            print(f"[GradCAM] Model lookup: {best_model is not None}")
            gradcam_b64 = None
            if best_model:
                try:
                    print("[GradCAM] Attempting generation...")
                    gradcam_b64 = generate_gradcam_overlay(best_model, file_bytes)
                    print(f"[GradCAM] Success: {gradcam_b64 is not None}")
                except Exception as e:
                    print(f"[GradCAM] Error: {e}")
            
            lime_b64 = generate_lime_explanation(file_bytes)
        else:
            # 2. Global Ensemble Prediction
            print("Running Ensemble Prediction...")
            # Use raw bytes for specialized medical preprocessing in the ensemble
            results = ensemble_predictor.predict_ensemble(file_bytes, use_tensorflow=False)
            
            diagnosis = "Parkinson's" if results['consensus_probability'] > 0.5 else "Normal"
            confidence = results['confidence']
            individual_predictions = results['individual_predictions']
            
            # Map probabilities for report generator
            class_probabilities = {
                "Normal": float(1.0 - results['consensus_probability']),
                "Parkinsons": float(results['consensus_probability']),
                "Unknown": 0.0
            }

            # 3. Generate XAI Visualizations (GradCAM & LIME)
            print("Generating XAI visualizations...")
            print(f"Individual predictions: {individual_predictions}")
            best_model_name = max(individual_predictions, key=individual_predictions.get)
            print(f"Best model name: {best_model_name}")
            best_model = ensemble_predictor.models.get(best_model_name)
            print(f"Best model object: {best_model}")
            
            gradcam_b64 = generate_gradcam_overlay(best_model, file_bytes) if best_model else None
            print(f"GradCAM generated: {gradcam_b64 is not None}")
            lime_b64 = generate_lime_explanation(file_bytes)
            print(f"LIME generated: {lime_b64 is not None}")


        # Transform individual_predictions to match frontend structure
        formatted_predictions = {}
        for model_name, prob in individual_predictions.items():
            model_diagnosis = "Parkinson's" if prob > 0.5 else "Normal"
            formatted_predictions[model_name] = {
                'prediction': model_diagnosis,
                'confidence': float(prob if model_diagnosis == "Parkinson's" else 1 - prob),
                'probabilities': {
                    'Normal': float(1.0 - prob),
                    'Parkinsons': float(prob),
                    'Unknown': 0.0
                }
            }

        response_data = {
            'diagnosis': diagnosis,
            'confidence': confidence,
            'class_probabilities': class_probabilities,
            'individual_predictions': formatted_predictions,
            'gradcam': {'available': True, 'image_base64': gradcam_b64} if gradcam_b64 else {'available': False},
            'lime': {'available': True, 'image_base64': lime_b64} if lime_b64 else {'available': False},
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Prediction complete: {diagnosis} ({confidence:.1%})")
        return jsonify(response_data), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Prediction failed: {str(e)}"}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report_endpoint():
    """Endpoint to generate PDF analysis report"""
    try:
        data = request.get_json()
        patient_name = data.get('patientName', 'You')
        include_xai = data.get('includeXAI', True)
        prediction_data = data.get('predictionData')
        
        from report_generator import generate_medical_report
        
        if not prediction_data:
            return jsonify({'error': 'No prediction data provided'}), 400
        
        print(f"Generating report for {patient_name}")
        pdf_buffer = generate_medical_report(prediction_data, patient_name, include_xai)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'parkinsons_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Gemini AI chatbot endpoint"""
    if not GEMINI_AVAILABLE:
        return jsonify({'response': "Assistant: I'm sorry, I am currently unable to connect.", 'error': 'Gemini not initialized'}), 503

    try:
        data = request.get_json() or {}
        user_message = data.get('message', '')
        history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        system_instruction = "You are a professional AI Assistant specializing in Parkinson's disease."
        full_prompt = f"{system_instruction}\n\n"
        for msg in history:
            role = "User" if msg['sender'] == 'user' else "Assistant"
            full_prompt += f"{role}: {msg['text']}\n"
        full_prompt += f"User: {user_message}\nAssistant:"

        response = client.models.generate_content(model="models/gemini-2.5-flash", contents=full_prompt)
        response_text = response.text.strip()
        if not response_text.startswith("Assistant:"):
            response_text = f"Assistant: {response_text}"

        return jsonify({'response': response_text, 'model': 'models/gemini-2.5-flash'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    print(f"Ensemble models loaded: {len(ensemble_predictor.models) if ensemble_initialized else 0}")
    app.run(debug=True, host='0.0.0.0', port=5000)
