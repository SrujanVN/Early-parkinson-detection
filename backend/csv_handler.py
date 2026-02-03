from flask import request, jsonify
import numpy as np
import os
from ensemble_predictor import ensemble_predictor

def register_csv_routes(app):
    @app.route('/api/predict/csv-features', methods=['POST'])
    def predict_csv_features():
        """CSV feature prediction endpoint - accepts 22 voice/clinical features as JSON"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Expected feature names (22 features)
            expected_features = [
                'MDVP_Fo_Hz', 'MDVP_Fhi_Hz', 'MDVP_Flo_Hz', 'MDVP_Jitter_Percent',
                'MDVP_Jitter_Abs', 'MDVP_RAP', 'MDVP_PPQ', 'Jitter_DDP',
                'MDVP_Shimmer', 'MDVP_Shimmer_dB', 'Shimmer_APQ3', 'Shimmer_APQ5',
                'MDVP_APQ', 'Shimmer_DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
                'spread1', 'spread2', 'D2', 'PPE'
            ]
            
            # Extract and validate features
            features = []
            missing_features = []
            
            for feature_name in expected_features:
                if feature_name in data:
                    try:
                        value = float(data[feature_name])
                        features.append(value)
                    except (ValueError, TypeError):
                        return jsonify({'error': f'Invalid value for {feature_name}'}), 400
                else:
                    missing_features.append(feature_name)
            
            if missing_features:
                return jsonify({
                    'error': 'Missing features',
                    'missing': missing_features
                }), 400
            
            # Convert to numpy array and reshape for model
            features_array = np.array(features).reshape(1, -1)
            
            # Get CSV_XGBoost model
            csv_model_name = 'CSV_XGBoost'
            if csv_model_name not in ensemble_predictor.models:
                return jsonify({'error': 'CSV model not loaded'}), 500
            
            csv_model = ensemble_predictor.models[csv_model_name]
            
            # Make prediction
            if hasattr(csv_model, 'predict_proba'):
                prediction_proba = csv_model.predict_proba(features_array)[0]
                parkinsons_probability = float(prediction_proba[1])  # Class 1 = Parkinson's
            else:
                prediction = csv_model.predict(features_array)[0]
                parkinsons_probability = float(prediction)
            
            # Determine diagnosis
            diagnosis = "Parkinson's" if parkinsons_probability > 0.5 else 'Normal'
            confidence = parkinsons_probability if parkinsons_probability > 0.5 else (1 - parkinsons_probability)
            
            # Get feature importance if available
            feature_importance = {}
            if hasattr(csv_model, 'feature_importances_'):
                importances = csv_model.feature_importances_
                # Get top 10 most important features
                importance_pairs = list(zip(expected_features, importances))
                importance_pairs.sort(key=lambda x: x[1], reverse=True)
                feature_importance = {
                    name: float(importance) 
                    for name, importance in importance_pairs[:10]
                }
            
            # Calculate risk level based on confidence
            if confidence >= 0.8:
                risk_level = 'High' if diagnosis == "Parkinson's" else 'Low'
            elif confidence >= 0.6:
                risk_level = 'Moderate'
            else:
                risk_level = 'Uncertain'
            
            return jsonify({
                'diagnosis': diagnosis,
                'confidence': confidence,
                'parkinsons_probability': parkinsons_probability,
                'normal_probability': 1 - parkinsons_probability,
                'risk_level': risk_level,
                'feature_importance': feature_importance,
                'features_analyzed': expected_features,
                'model_used': csv_model_name
            }), 200
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'CSV prediction failed: {str(e)}'}), 500
