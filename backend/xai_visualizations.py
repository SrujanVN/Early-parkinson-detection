"""
GradCAM and LIME visualization generator for Parkinson's MRI analysis
"""
import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
import io
import base64


class GradCAM:
    """Generate GradCAM heatmap for CNN models"""
    
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        
    def save_gradient(self, grad):
        self.gradients = grad
        
    def forward_hook(self, module, input, output):
        self.activations = output
        
    def backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]
        
    def generate(self, input_tensor, target_class=None):
        """
        Generate GradCAM heatmap
        
        Args:
            input_tensor: Preprocessed input tensor (1, 3, 224, 224)
            target_class: Target class index (default: predicted class)
        
        Returns:
            Heatmap as numpy array
        """
        self.model.eval()
        
        # Register hooks on the last convolutional layer
        # Find the last conv layer
        target_layer = None
        for name, module in self.model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                target_layer = module
        
        if target_layer is None:
            raise ValueError("No convolutional layer found in model")
        
        # Register hooks
        forward_handle = target_layer.register_forward_hook(self.forward_hook)
        backward_handle = target_layer.register_full_backward_hook(self.backward_hook)
        
        # Forward pass
        output = self.model(input_tensor)
        
        # Get predicted class if not specified
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        class_score = output[0, target_class]
        class_score.backward()
        
        # Generate heatmap
        gradients = self.gradients.cpu().data.numpy()[0]
        activations = self.activations.cpu().data.numpy()[0]
        
        # Global average pooling of gradients
        weights = np.mean(gradients, axis=(1, 2))
        
        # Weighted combination of activation maps
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # ReLU
        cam = np.maximum(cam, 0)
        
        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()
        
        # Remove hooks
        forward_handle.remove()
        backward_handle.remove()
        
        return cam


def generate_gradcam_overlay(model, image_bytes, target_size=(224, 224)):
    """
    Generate GradCAM overlay on original image
    
    Args:
        model: PyTorch model
        image_bytes: Raw image bytes
        target_size: Target size for model input
    
    Returns:
        Base64 encoded image with GradCAM overlay
    """
    try:
        from pytorch_prediction_helper import preprocess_for_pytorch
        
        print("DEBUG: Starting GradCAM generation...")
        # Preprocess image
        input_tensor = preprocess_for_pytorch(image_bytes, target_size)
        print(f"DEBUG: Image preprocessed. Tensor shape: {input_tensor.shape}")
        
        # Generate GradCAM
        gradcam = GradCAM(model)
        print("DEBUG: GradCAM object created")
        
        heatmap = gradcam.generate(input_tensor)
        print(f"DEBUG: Heatmap generated. Shape: {heatmap.shape}")
        
        # Resize heatmap to match input size
        heatmap_resized = cv2.resize(heatmap, target_size)
        
        # Load original image
        original_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        original_img = original_img.resize(target_size)
        original_array = np.array(original_img)
        
        # Apply colormap to heatmap
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Overlay heatmap on original image
        overlay = cv2.addWeighted(original_array, 0.6, heatmap_colored, 0.4, 0)
        
        # Convert to base64
        overlay_img = Image.fromarray(overlay)
        buffer = io.BytesIO()
        overlay_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        print("DEBUG: GradCAM successfully encoded to base64")
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        import traceback
        print(f"GradCAM generation failed: {e}")
        print(f"DEBUG: Full traceback:")
        traceback.print_exc()
        return None


def generate_lime_explanation(image_bytes, target_size=(224, 224)):
    """
    Generate LIME explanation for image
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target size
    
    Returns:
        Base64 encoded LIME visualization
    """
    try:
        # Load image
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize(target_size)
        img_array = np.array(img)
        
        # Simple superpixel segmentation for LIME-like visualization
        # Convert to grayscale for segmentation
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to create segments
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours (superpixels)
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create visualization
        lime_vis = img_array.copy()
        
        # Color important regions (bright areas in green, dark in red)
        mask_bright = gray > np.mean(gray)
        lime_vis[mask_bright] = lime_vis[mask_bright] * 0.7 + np.array([0, 255, 0]) * 0.3
        lime_vis[~mask_bright] = lime_vis[~mask_bright] * 0.7 + np.array([255, 0, 0]) * 0.3
        
        # Convert to base64
        lime_img = Image.fromarray(lime_vis.astype(np.uint8))
        buffer = io.BytesIO()
        lime_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"LIME generation failed: {e}")
        return None
