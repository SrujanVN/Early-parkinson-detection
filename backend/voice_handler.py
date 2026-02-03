from flask import request, jsonify
import os
import uuid
from voice_predictor import voice_predictor
from voice_report_generator import voice_report_gen

def register_voice_routes(app):
    @app.route('/api/predict/voice', methods=['POST'])
    def predict_voice():
        """Isolated Voice analysis endpoint"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No audio file uploaded'}), 400
            
            file = request.files['file']
            patient_name = request.form.get('patient_name', 'Patient')
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read audio bytes
            audio_bytes = file.read()
            
            # Predict using isolated system
            result = voice_predictor.predict(audio_bytes)
            
            if 'error' in result:
                return jsonify(result), 500
            
            # Add metadata
            result['patient_name'] = patient_name
            result['timestamp'] = os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip()
            
            # Generate specialized voice report
            pdf_base64 = voice_report_gen.generate_report(result)
            result['report_pdf_base64'] = pdf_base64
            
            return jsonify(result)
        except Exception as e:
            print(f"Voice analysis error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/voice/initialize', methods=['GET'])
    def initialize_voice():
        """Initialize voice models"""
        voice_predictor.load_model()
        return jsonify({'status': 'initialized'})
