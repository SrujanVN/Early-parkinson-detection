from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import librosa
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load the model
model = tf.keras.models.load_model('models/final_parkinsons_model_complete.h5')

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
    df = pd.read_csv(file)
    # Process according to your model's requirements
    features = df.values
    return features

@app.route('/predict', methods=['POST'])
def predict():
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
    app.run(debug=True)