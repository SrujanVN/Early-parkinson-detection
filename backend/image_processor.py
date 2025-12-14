"""
Image preprocessing utilities for ensemble deep learning models
Supports both TensorFlow/Keras and PyTorch models
"""
import numpy as np
from PIL import Image
import io

# Try to import TensorFlow
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Try to import PyTorch
try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except (ImportError, AttributeError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    transforms = None


def preprocess_image_for_tensorflow(file, target_size=(224, 224)):
    """
    Preprocess image for TensorFlow/Keras models
    
    Args:
        file: File object or bytes
        target_size: Tuple of (height, width)
    
    Returns:
        Preprocessed image array ready for model input
    """
    # Read image
    if isinstance(file, bytes):
        img = Image.open(io.BytesIO(file))
    else:
        img = Image.open(io.BytesIO(file.read()))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert to array and normalize
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array / 255.0  # Normalize to [0, 1]
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array, img  # Return both processed array and original PIL image


def preprocess_image_for_pytorch(file, target_size=(224, 224)):
    """
    Preprocess image for PyTorch models
    
    Args:
        file: File object or bytes
        target_size: Tuple of (height, width)
    
    Returns:
        Preprocessed tensor ready for model input
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is not available. Install torch and torchvision.")
    
    # Define transforms (ImageNet normalization)
    transform = transforms.Compose([
        transforms.Resize(target_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Read image
    if isinstance(file, bytes):
        img = Image.open(io.BytesIO(file))
    else:
        img = Image.open(io.BytesIO(file.read()))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Apply transforms
    img_tensor = transform(img)
    
    # Add batch dimension
    img_tensor = img_tensor.unsqueeze(0)
    
    return img_tensor, img  # Return both processed tensor and original PIL image


def save_image_temporarily(img, filename_prefix='temp_image'):
    """
    Save image temporarily for processing
    
    Args:
        img: PIL Image object
        filename_prefix: Prefix for temporary filename
    
    Returns:
        Path to saved image
    """
    import os
    import tempfile
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{filename_prefix}_{unique_id}.png"
    filepath = os.path.join(temp_dir, filename)
    
    # Save image
    img.save(filepath, 'PNG')
    
    return filepath


def cleanup_temp_file(filepath):
    """
    Clean up temporary file
    
    Args:
        filepath: Path to file to delete
    """
    import os
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not delete temp file {filepath}: {e}")


def validate_image_file(file):
    """
    Validate uploaded image file
    
    Args:
        file: File object
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Read first few bytes to check file signature
        file.seek(0)
        header = file.read(12)
        file.seek(0)
        
        # Check for common image formats
        valid_signatures = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'GIF87a',  # GIF
            b'GIF89a',  # GIF
            b'RIFF',  # WebP (starts with RIFF)
        ]
        
        is_valid = any(header.startswith(sig) for sig in valid_signatures)
        
        if not is_valid:
            return False, "Invalid image format. Supported: JPEG, PNG, GIF, WebP"
        
        # Check file size (max 10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return False, "Image file too large. Maximum size: 10MB"
        
        if file_size < 100:  # Too small
            return False, "Image file too small or corrupted"
        
        return True, None
        
    except Exception as e:
        return False, f"Error validating image: {str(e)}"
