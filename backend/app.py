from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3
import os
import numpy as np
from PIL import Image
import io
import librosa
from functools import wraps
import secrets
import uuid
from werkzeug.utils import secure_filename

# Try to import pandas (optional, only for CSV processing)
PANDAS_AVAILABLE = False
pd = None
try:
    # Suppress warnings during import
    import warnings
    warnings.filterwarnings('ignore')
    import pandas as pd
    PANDAS_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError, Exception) as e:
    # Pandas/pyarrow has NumPy compatibility issues - disable for now
    PANDAS_AVAILABLE = False
    pd = None
    # Don't print error - just silently disable
    pass

# Import ensemble and GradCAM modules
try:
    from image_processor import (
        preprocess_image_for_tensorflow, 
        preprocess_image_for_pytorch,
        validate_image_file,
        save_image_temporarily,
        cleanup_temp_file
    )
    from ensemble_predictor import ensemble_predictor, initialize_ensemble_models
    from gradcam_generator import (
        generate_gradcam_for_model,
        encode_image_to_base64,
        save_gradcam_image
    )
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Image processing modules not available: {e}")
    IMAGE_PROCESSING_AVAILABLE = False

# Try to import TensorFlow
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TensorFlow not available: {e}")
    print("Server will start but predictions will not work until TensorFlow is installed.")
    TF_AVAILABLE = False
    tf = None

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Generate a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'parkinsons:'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Session
Session(app)

CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"])

# Database configuration
DB_NAME = 'lungvision.db'

def init_db():
    """Initialize the SQLite database with user table"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Patient', 'Researcher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully!")

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows column access by name
    return conn

# Initialize database on startup
init_db()

# Load the model (legacy, for backward compatibility)
model = None
if TF_AVAILABLE:
    try:
        print("Loading legacy model...")
        model = tf.keras.models.load_model('final_parkinsons_model_complete.h5')
        print("Legacy model loaded successfully!")
    except Exception as e:
        print(f"Error loading legacy model: {e}")
        model = None
else:
    print("TensorFlow not available - model cannot be loaded.")

# Initialize ensemble models
if IMAGE_PROCESSING_AVAILABLE:
    print("\n" + "="*50)
    print("Initializing Ensemble Models...")
    print("="*50)
    ensemble_initialized = initialize_ensemble_models()
    if ensemble_initialized:
        print("[OK] Ensemble predictor ready")
        print(f"  Models loaded: {ensemble_predictor.get_model_info()}")
    else:
        print("⚠ Ensemble predictor not initialized")
    print("="*50 + "\n")
else:
    ensemble_initialized = False

# Authentication decorator
def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorator to protect routes that require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            if session.get('role') != required_role:
                return jsonify({'error': f'{required_role} role required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        role = data.get('role', 'Patient')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Password confirmation check
        if password_confirm and password != password_confirm:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Enhanced password validation
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        if len(password) > 128:
            return jsonify({'error': 'Password must be less than 128 characters'}), 400
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'password123']
        if password.lower() in weak_passwords:
            return jsonify({'error': 'Password is too weak. Please choose a stronger password'}), 400
        
        if role not in ['Patient', 'Researcher']:
            return jsonify({'error': 'Role must be either "Patient" or "Researcher"'}), 400
        
        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password securely
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
        # Insert new user
        cursor = conn.execute(
            'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
            (email, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'email': email,
            'role': role
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user and create session - Verifies password matches the stored hash"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user from database
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, email, password_hash, role FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        
        # Always return the same error message to prevent user enumeration
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # CRITICAL: Verify password matches the stored hash
        # This ensures the user must use the EXACT same password they registered with
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Password verified successfully - create session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user information"""
    return jsonify({
        'user': {
            'id': session.get('user_id'),
            'email': session.get('email'),
            'role': session.get('role')
        }
    }), 200

# Existing prediction routes (keeping for backward compatibility)
def process_image(file):
    # Read and preprocess image
    img = Image.open(io.BytesIO(file.read()))
    img = img.resize((224, 224))  # Adjust size according to your model's input
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def process_audio(file):
    # Process audio file using librosa
    y, sr = librosa.load(io.BytesIO(file.read()))
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfccs_scaled = np.mean(mfccs.T, axis=0)
    return np.expand_dims(mfccs_scaled, axis=0)

def process_csv(file):
    # Read and process CSV data
    if not PANDAS_AVAILABLE:
        raise ImportError("Pandas is required for CSV processing but is not available")
    df = pd.read_csv(file)
    # Process according to your model's requirements
    features = df.values
    return features

@app.route('/api/predict/xray', methods=['POST'])
@login_required
def predict_xray_ensemble():
    """
    X-ray/CT Scan prediction endpoint with ensemble models and GradCAM
    Accepts X-ray or CT scan images, runs ensemble prediction, and generates GradCAM heatmaps
    """
    if not IMAGE_PROCESSING_AVAILABLE:
        return jsonify({'error': 'Image processing modules not available'}), 500
    
    if not ensemble_initialized:
        return jsonify({'error': 'Ensemble models not initialized'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Validate file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate image file
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    temp_file_path = None
    try:
        # Reset file pointer
        file.seek(0)
        
        # Save file temporarily for processing
        file_bytes = file.read()
        file.seek(0)
        
        # Validate again with bytes
        is_valid, error_msg = validate_image_file(io.BytesIO(file_bytes))
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Preprocess image for TensorFlow (using existing model format)
        preprocessed_img, original_img = preprocess_image_for_tensorflow(
            file_bytes, 
            target_size=(224, 224)
        )
        
        # Get ensemble prediction
        ensemble_result = ensemble_predictor.predict_ensemble(
            preprocessed_img, 
            use_tensorflow=True
        )
        
        # Determine diagnosis
        consensus_prob = ensemble_result['consensus_probability']
        diagnosis = 'Parkinson\'s' if consensus_prob > 0.5 else 'Normal'
        
        # Generate GradCAM heatmap for the first available model
        gradcam_result = None
        gradcam_base64 = None
        
        if len(ensemble_predictor.models) > 0:
            # Use the first model for GradCAM
            first_model_name = ensemble_predictor.model_names[0]
            first_model = ensemble_predictor.models[first_model_name]
            model_type = ensemble_predictor.model_types[first_model_name]
            
            try:
                gradcam_result = generate_gradcam_for_model(
                    first_model,
                    preprocessed_img,
                    original_img,
                    model_type=model_type
                )
                
                if gradcam_result:
                    # Encode GradCAM overlay as base64
                    gradcam_base64 = encode_image_to_base64(
                        gradcam_result['heatmap_overlay']
                    )
                    
                    # Optionally save to disk
                    temp_file_path = save_gradcam_image(
                        gradcam_result['heatmap_overlay'],
                        filename_prefix='xray_gradcam'
                    )
            except Exception as e:
                print(f"GradCAM generation error: {e}")
                # Continue without GradCAM if it fails
        
        # Prepare response
        response = {
            'diagnosis': diagnosis,
            'confidence': consensus_prob,
            'ensemble_info': {
                'num_models': ensemble_result['num_models'],
                'consensus_probability': consensus_prob,
                'ensemble_confidence': ensemble_result['confidence'],
                'std_dev': ensemble_result['std_dev'],
                'individual_predictions': ensemble_result['individual_predictions']
            },
            'gradcam': {
                'available': gradcam_result is not None,
                'image_base64': gradcam_base64,
                'layer_used': gradcam_result['layer_used'] if gradcam_result else None
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in X-ray prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500
        
    finally:
        # Cleanup temporary files
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """Protected prediction endpoint"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    file_type = request.form.get('fileType', 'MRI')
    
    try:
        # Process file based on type
        if file_type in ['MRI', 'Handwriting']:
            processed_data = process_image(file)
        elif file_type == 'Audio':
            processed_data = process_audio(file)
        elif file_type == 'CSV':
            processed_data = process_csv(file)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

        # Make prediction
        prediction = model.predict(processed_data)
        
        # Process prediction result
        confidence = float(prediction[0][0])
        diagnosis = 'Parkinson\'s' if confidence > 0.5 else 'Normal'
        
        return jsonify({
            'diagnosis': diagnosis,
            'confidence': confidence,
            # Add gradCam or spectrogram URLs if implemented
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if model is None:
        print("WARNING: Model not loaded. Server will start but predictions will fail.")
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Database initialized: lungvision.db")
    app.run(debug=True, host='127.0.0.1', port=5000)
