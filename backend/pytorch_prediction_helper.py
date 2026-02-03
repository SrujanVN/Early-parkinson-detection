"""
Image preprocessing for PyTorch models
Matches the exact preprocessing used during training
"""
import torch
import numpy as np
from PIL import Image
import io


def preprocess_for_pytorch(image_bytes, target_size=(224, 224)):
    """
    Preprocess image for PyTorch models using ImageNet normalization
    Matches the validation transform from training code
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target size (height, width)
    
    Returns:
        Preprocessed tensor ready for model input
    """
    # Open image
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Resize to target size
    img = img.resize(target_size, Image.BILINEAR)
    
    # Convert to numpy array
    img_array = np.array(img, dtype=np.float32)
    
    # Normalize to [0, 1]
    img_array = img_array / 255.0
    
    # Apply ImageNet normalization (CRITICAL - must match training!)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    img_array = (img_array - mean) / std
    
    # Convert to tensor and transpose to (C, H, W)
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)
    
    # Add batch dimension (1, C, H, W)
    img_tensor = img_tensor.unsqueeze(0)
    
    return img_tensor


def predict_pytorch_3class(model, image_bytes):
    """
    Make prediction with PyTorch model that outputs 3 classes
    Uses advanced preprocessing for noisy medical images
    
    Args:
        model: PyTorch model
        image_bytes: Raw image bytes
    
    Returns:
        Dictionary with class probabilities {0: normal, 1: parkinsons, 2: unknown}
    """
    try:
        from medical_image_preprocessing import preprocess_for_pytorch_with_denoising
        img_tensor = preprocess_for_pytorch_with_denoising(image_bytes)
    except Exception as e:
        print(f"Advanced preprocessing failed, using standard: {e}")
        # Fallback to standard preprocessing
        img_tensor = preprocess_for_pytorch(image_bytes)
    
    # Set model to eval mode
    model.eval()
    
    with torch.no_grad():
        # Forward pass
        output = model(img_tensor)
        
        # Apply softmax for 3-class output
        probabilities = torch.nn.functional.softmax(output, dim=1)
        
        # Return as dict: {0: normal_prob, 1: parkinsons_prob, 2: unknown_prob}
        probs_dict = {}
        for i in range(probabilities.shape[1]):
            probs_dict[i] = float(probabilities[0][i].item())
        
        return probs_dict
