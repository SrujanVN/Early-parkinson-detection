from flask import request, jsonify
import os
import uuid
from handwriting_predictor import handwriting_predictor
from handwriting_report_generator import handwriting_report_gen

def register_handwriting_routes(app):
    @app.route('/api/predict/handwriting', methods=['POST'])
    def predict_handwriting():
        """Handwriting analysis endpoint"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            patient_name = request.form.get('patient_name', 'Anonymous')
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read image bytes
            image_bytes = file.read()
            
            # Predict
            result = handwriting_predictor.predict(image_bytes)
            
            if 'error' in result:
                return jsonify(result), 500
            
            # Add patient info and timestamp
            result['patient_name'] = patient_name
            result['timestamp'] = os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip()
            
            # Generate specialized handwriting report
            pdf_base64 = handwriting_report_gen.generate_report(result)
            result['report_pdf_base64'] = pdf_base64
            
            return jsonify(result)
        except Exception as e:
            print(f"Handwriting analysis error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/handwriting/initialize', methods=['GET'])
    def initialize_handwriting():
        """Initialize handwriting models if not already loaded"""
        success = handwriting_predictor.load_models()
        return jsonify({'status': 'initialized' if success else 'failed'})
