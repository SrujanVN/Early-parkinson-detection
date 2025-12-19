"""
Ensemble prediction system for multiple deep learning models
Currently uses existing model, structured to easily add 4 models later
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import os

# Try to import TensorFlow
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None

# Try to import PyTorch
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except (ImportError, AttributeError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    print(f"PyTorch not available (optional): {e}")


class EnsemblePredictor:
    """
    Ensemble predictor that combines predictions from multiple models
    """
    
    def __init__(self):
        self.models = {}
        self.model_names = []
        self.model_types = {}  # 'tensorflow' or 'pytorch'
        self.is_loaded = False
    
    def load_model(self, name: str, model_path: str, model_type: str = 'tensorflow'):
        """
        Load a single model
        
        Args:
            name: Model name (e.g., 'EfficientNetB3', 'DenseNet121')
            model_path: Path to model file
            model_type: 'tensorflow', 'pytorch', or 'sklearn'
        """
        try:
            if model_type == 'tensorflow' and TF_AVAILABLE:
                model = tf.keras.models.load_model(model_path)
                model.trainable = False  # Set to evaluation mode
                self.models[name] = model
                self.model_types[name] = 'tensorflow'
                print(f"[OK] Loaded {name} (TensorFlow) from {model_path}")
                
            elif model_type == 'pytorch' and TORCH_AVAILABLE:
                try:
                    # Import model architectures
                    from pytorch_models import load_pytorch_model
                    
                    # Determine model type from name
                    name_lower = name.lower()
                    if 'resnet' in name_lower:
                        arch_type = 'resnet50'
                    elif 'densenet' in name_lower:
                        arch_type = 'densenet121'
                    elif 'efficientnet' in name_lower:
                        if 'b3' in name_lower or '_b3' in name_lower:
                            arch_type = 'efficientnet_b3'
                        elif 'b0' in name_lower or '_b0' in name_lower:
                            arch_type = 'efficientnet_b0'
                        else:
                            print(f"[WARNING] Unknown EfficientNet variant for {name}, skipping")
                            return False
                    else:
                        print(f"[WARNING] Unknown PyTorch architecture for {name}, skipping")
                        return False
                    
                    # Load model with architecture
                    model = load_pytorch_model(model_path, model_type=arch_type, num_classes=3)
                    self.models[name] = model
                    self.model_types[name] = 'pytorch'
                    print(f"[OK] Loaded {name} (PyTorch) from {model_path}")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to load PyTorch model {name}: {e}")
                    return False
                
            elif model_type == 'sklearn':
                # Load sklearn/pickle models
                import joblib
                model = joblib.load(model_path)
                self.models[name] = model
                self.model_types[name] = 'sklearn'
                print(f"[OK] Loaded {name} (sklearn/pickle) from {model_path}")
                
            else:
                print(f"[WARNING] {model_type} not available, skipping {name}")
                return False
            
            if name not in self.model_names:
                self.model_names.append(name)
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading {name}: {e}")
            return False
    
    def load_ensemble_models(self, model_configs: List[Dict]):
        """
        Load multiple models from configuration
        
        Args:
            model_configs: List of dicts with keys: name, path, type
        """
        loaded_count = 0
        for config in model_configs:
            if self.load_model(
                config['name'],
                config['path'],
                config.get('type', 'tensorflow')
            ):
                loaded_count += 1
        
        print(f"\n[ENSEMBLE] {loaded_count}/{len(model_configs)} models loaded")
        return loaded_count > 0
    
    def predict_single_model(self, model_name: str, preprocessed_input, model_type: str):
        """
        Get prediction from a single model
        
        Args:
            model_name: Name of the model
            preprocessed_input: Preprocessed image (numpy array or tensor)
            model_type: 'tensorflow' or 'pytorch'
        
        Returns:
            Prediction probability (float between 0 and 1)
        """
        model = self.models[model_name]
        
        try:
            if model_type == 'tensorflow':
                prediction = model.predict(preprocessed_input, verbose=0)
                # Assuming binary classification, get probability
                if len(prediction.shape) > 1:
                    prob = float(prediction[0][0]) if prediction.shape[1] > 1 else float(prediction[0])
                else:
                    prob = float(prediction[0])
                return prob
                
            elif model_type == 'pytorch':
                from pytorch_prediction_helper import predict_pytorch_3class
                return predict_pytorch_3class(model, preprocessed_input)
            
            elif model_type == 'sklearn':
                # sklearn models
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(preprocessed_input)
                    return float(proba[0][1]) if proba.shape[1] == 2 else proba[0]
                else:
                    pred = model.predict(preprocessed_input)
                    return float(pred[0])
                    
        except Exception as e:
            print(f"Error predicting with {model_name}: {e}")
            return None
    
    def predict_ensemble(self, preprocessed_input, use_tensorflow: bool = True):
        """
        Get consensus prediction from all loaded models
        
        Args:
            preprocessed_input: Preprocessed image
            use_tensorflow: Whether input is TensorFlow format (True) or PyTorch (False)
        
        Returns:
            Dict with:
                - consensus_probability: Average probability across all models
                - individual_predictions: Dict of model_name -> probability
                - confidence: Standard deviation (lower = more confident)
        """
        if not self.is_loaded or len(self.models) == 0:
            raise ValueError("No models loaded. Load models first.")
        
        individual_predictions = {}
        probabilities = []
        
        for model_name in self.model_names:
            model_type = self.model_types[model_name]
            
            # Convert input format if needed
            if use_tensorflow and model_type == 'pytorch':
                # Convert numpy array to PyTorch tensor
                if isinstance(preprocessed_input, np.ndarray):
                    # For now, convert directly - proper preprocessing should be done before calling
                    # In production, preprocess separately for each model type
                    preprocessed_input = torch.from_numpy(preprocessed_input).float()
                    # Apply ImageNet normalization if needed
                    pass
            elif not use_tensorflow and model_type == 'tensorflow':
                # Convert PyTorch tensor to numpy
                if isinstance(preprocessed_input, torch.Tensor):
                    preprocessed_input = preprocessed_input.numpy()
            
            prob = self.predict_single_model(model_name, preprocessed_input, model_type)
            
            if prob is not None:
                individual_predictions[model_name] = prob
                probabilities.append(prob)
        
        if len(probabilities) == 0:
            raise ValueError("No valid predictions from any model")
        
        # Calculate consensus (average)
        consensus_probability = np.mean(probabilities)
        
        # Calculate confidence (inverse of standard deviation)
        std_dev = np.std(probabilities)
        confidence = 1.0 - min(std_dev, 1.0)  # Normalize to [0, 1]
        
        return {
            'consensus_probability': float(consensus_probability),
            'individual_predictions': individual_predictions,
            'confidence': float(confidence),
            'num_models': len(probabilities),
            'std_dev': float(std_dev)
        }
    
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'loaded_models': self.model_names,
            'model_types': self.model_types,
            'total_models': len(self.models),
            'is_ready': self.is_loaded and len(self.models) > 0
        }


# Global ensemble predictor instance
ensemble_predictor = EnsemblePredictor()


def initialize_ensemble_models():
    """
    Initialize ensemble models
    Currently loads the existing model, ready to add 4 models later
    """
    global ensemble_predictor
    
    # Model configurations for all modalities (no legacy .h5 model)
    model_configs = [
        # MRI Models (PyTorch)
        {
            'name': 'MRI_DenseNet121',
            'path': 'models/Parkinson_mri/best_densenet121.pth',
            'type': 'pytorch'
        },
        {
            'name': 'MRI_ResNet50',
            'path': 'models/Parkinson_mri/best_resnet50.pth',
            'type': 'pytorch'
        },
        {
            'name': 'MRI_EfficientNetB0',
            'path': 'models/Parkinson_mri/best_efficientnet_b0.pth',
            'type': 'pytorch'
        },
        {
            'name': 'MRI_EfficientNetB3',
            'path': 'models/Parkinson_mri/best_efficientnet_b3.pth',
            'type': 'pytorch'
        },
        # Handwriting Models (sklearn/pickle)
        {
            'name': 'Handwriting_HOG_SVM',
            'path': 'models/Parkinson_handwriting/hog_svm_open_set.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Handwriting_LBP_RF',
            'path': 'models/Parkinson_handwriting/lbp_rf_open_set.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Handwriting_MobileNet_SVM',
            'path': 'models/Parkinson_handwriting/mobilenet_svm_open_set.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Handwriting_Ensemble',
            'path': 'models/Parkinson_handwriting/parkinson_ensemble_open_set.pkl',
            'type': 'sklearn'
        },
        # Voice Models (sklearn/pickle)
        {
            'name': 'Voice_XGBoost',
            'path': 'models/parkinsons_voice/xgboost_parkinson_voice.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Voice_RandomForest',
            'path': 'models/parkinsons_voice/random_forest_parkinson_voice.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Voice_SVM',
            'path': 'models/parkinsons_voice/svm_parkinson_voice.pkl',
            'type': 'sklearn'
        },
        {
            'name': 'Voice_Ensemble',
            'path': 'models/parkinsons_voice/ensemble_parkinson_voice.pkl',
            'type': 'sklearn'
        },
        # CSV Model (XGBoost/pickle)
        {
            'name': 'CSV_XGBoost',
            'path': 'models/parkinsions_csv/parkinson_xgboost.pkl',
            'type': 'sklearn'
        }
    ]
    
    # Filter out models that don't exist
    existing_configs = []
    for config in model_configs:
        if os.path.exists(config['path']):
            existing_configs.append(config)
        else:
            print(f"⚠ Model file not found: {config['path']}")
    
    if len(existing_configs) > 0:
        ensemble_predictor.load_ensemble_models(existing_configs)
        return True
    else:
        print("[WARNING] No ensemble models loaded")
        return False
