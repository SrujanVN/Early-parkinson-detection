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
            model_type: 'tensorflow' or 'pytorch'
        """
        try:
            if model_type == 'tensorflow' and TF_AVAILABLE:
                model = tf.keras.models.load_model(model_path)
                model.trainable = False  # Set to evaluation mode
                self.models[name] = model
                self.model_types[name] = 'tensorflow'
                print(f"[OK] Loaded {name} (TensorFlow) from {model_path}")
                
            elif model_type == 'pytorch' and TORCH_AVAILABLE:
                model = torch.load(model_path, map_location='cpu')
                model.eval()  # Set to evaluation mode
                self.models[name] = model
                self.model_types[name] = 'pytorch'
                print(f"[OK] Loaded {name} (PyTorch) from {model_path}")
                
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
                with torch.no_grad():
                    if isinstance(preprocessed_input, np.ndarray):
                        preprocessed_input = torch.from_numpy(preprocessed_input)
                    output = model(preprocessed_input)
                    # Apply sigmoid if needed
                    if output.dim() > 1:
                        prob = torch.sigmoid(output[0][0]).item()
                    else:
                        prob = torch.sigmoid(output[0]).item()
                    return prob
                    
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
    
    # For now, use the existing model
    # Later, this will load: EfficientNetB3, DenseNet121, InceptionV3, ResNet50
    model_configs = [
        {
            'name': 'CurrentModel',
            'path': 'final_parkinsons_model_complete.h5',
            'type': 'tensorflow'
        }
        # TODO: Add these when models are provided:
        # {
        #     'name': 'EfficientNetB3',
        #     'path': 'models/efficientnetb3.pth',
        #     'type': 'pytorch'
        # },
        # {
        #     'name': 'DenseNet121',
        #     'path': 'models/densenet121.pth',
        #     'type': 'pytorch'
        # },
        # {
        #     'name': 'InceptionV3',
        #     'path': 'models/inceptionv3.pth',
        #     'type': 'pytorch'
        # },
        # {
        #     'name': 'ResNet50',
        #     'path': 'models/resnet50.pth',
        #     'type': 'pytorch'
        # }
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
