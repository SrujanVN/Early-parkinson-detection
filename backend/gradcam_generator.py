"""
GradCAM (Gradient-weighted Class Activation Mapping) implementation
Generates visual heatmaps explaining model predictions
"""
import numpy as np
from PIL import Image
import io
import base64
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
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except (ImportError, AttributeError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    print(f"PyTorch not available (optional): {e}")


def generate_gradcam_tensorflow(model, img_array, layer_name=None, class_idx=0):
    """
    Generate GradCAM heatmap for TensorFlow/Keras model
    
    Args:
        model: TensorFlow/Keras model
        img_array: Preprocessed image array (batch dimension included)
        layer_name: Name of target layer (default: last convolutional layer)
        class_idx: Class index to generate heatmap for
    
    Returns:
        GradCAM heatmap as numpy array
    """
    if not TF_AVAILABLE:
        raise ImportError("TensorFlow not available")
    
    # Find the last convolutional layer if not specified
    if layer_name is None:
        for layer in reversed(model.layers):
            if 'conv' in layer.name.lower() or isinstance(layer, tf.keras.layers.Conv2D):
                layer_name = layer.name
                break
    
    if layer_name is None:
        raise ValueError("Could not find convolutional layer for GradCAM")
    
    # Create a model that outputs both the predictions and the conv layer output
    grad_model = tf.keras.models.Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(layer_name).output, model.output]
    )
    
    # Compute gradients
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        class_channel = predictions[:, class_idx]
    
    # Get gradients
    grads = tape.gradient(class_channel, conv_outputs)
    
    # Global average pooling of gradients
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    # Weight the feature maps by gradients
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    
    # Normalize heatmap
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    heatmap = heatmap.numpy()
    
    return heatmap, layer_name


def generate_gradcam_pytorch(model, img_tensor, target_layer, class_idx=0):
    """
    Generate GradCAM heatmap for PyTorch model
    
    Args:
        model: PyTorch model
        img_tensor: Preprocessed image tensor (batch dimension included)
        target_layer: Target layer (nn.Module)
        class_idx: Class index to generate heatmap for
    
    Returns:
        GradCAM heatmap as numpy array
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch not available")
    
    # Set model to eval mode
    model.eval()
    
    # Register hook to get gradients
    gradients = []
    activations = []
    
    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])
    
    def forward_hook(module, input, output):
        activations.append(output)
    
    # Register hooks
    handle_backward = target_layer.register_full_backward_hook(backward_hook)
    handle_forward = target_layer.register_forward_hook(forward_hook)
    
    # Forward pass
    output = model(img_tensor)
    
    # Backward pass
    model.zero_grad()
    if output.dim() > 1:
        output[0, class_idx].backward()
    else:
        output[0].backward()
    
    # Get gradients and activations
    grads = gradients[0]
    acts = activations[0]
    
    # Global average pooling of gradients
    pooled_grads = torch.mean(grads, dim=[2, 3], keepdim=True)
    
    # Weight the feature maps
    heatmap = torch.sum(acts * pooled_grads, dim=1).squeeze()
    
    # Normalize
    heatmap = F.relu(heatmap)
    heatmap = heatmap / torch.max(heatmap)
    heatmap = heatmap.detach().cpu().numpy()
    
    # Remove hooks
    handle_backward.remove()
    handle_forward.remove()
    
    return heatmap


def overlay_heatmap_on_image(original_img, heatmap, alpha=0.4):
    """
    Overlay GradCAM heatmap on original image
    
    Args:
        original_img: PIL Image object
        heatmap: GradCAM heatmap (numpy array)
        alpha: Transparency of heatmap overlay
    
    Returns:
        PIL Image with heatmap overlay
    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    # Resize heatmap to match image size
    heatmap_resized = np.array(Image.fromarray(heatmap).resize(
        original_img.size, Image.Resampling.BICUBIC
    ))
    
    # Normalize heatmap to [0, 1]
    if heatmap_resized.max() > 0:
        heatmap_resized = heatmap_resized / heatmap_resized.max()
    
    # Apply colormap
    cmap = cm.get_cmap('jet')
    heatmap_colored = cmap(heatmap_resized)[:, :, :3]  # Remove alpha channel
    heatmap_colored = (heatmap_colored * 255).astype(np.uint8)
    
    # Convert original image to array
    img_array = np.array(original_img)
    
    # Ensure same size
    if img_array.shape[:2] != heatmap_colored.shape[:2]:
        heatmap_colored = np.array(Image.fromarray(heatmap_colored).resize(
            (img_array.shape[1], img_array.shape[0]), Image.Resampling.BICUBIC
        ))
    
    # Overlay
    overlay = (alpha * heatmap_colored + (1 - alpha) * img_array).astype(np.uint8)
    
    return Image.fromarray(overlay)


def save_gradcam_image(overlay_img, filename_prefix='gradcam'):
    """
    Save GradCAM overlay image
    
    Args:
        overlay_img: PIL Image with heatmap overlay
        filename_prefix: Prefix for filename
    
    Returns:
        Path to saved image
    """
    import uuid
    
    # Create temp directory
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp_gradcam')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{filename_prefix}_{unique_id}.png"
    filepath = os.path.join(temp_dir, filename)
    
    # Save
    overlay_img.save(filepath, 'PNG')
    
    return filepath


def encode_image_to_base64(img):
    """
    Encode PIL Image to base64 string for API response
    
    Args:
        img: PIL Image object
    
    Returns:
        Base64 encoded string
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def generate_gradcam_for_model(model, preprocessed_input, original_img, 
                                model_type='tensorflow', layer_name=None):
    """
    Generate GradCAM heatmap for a model (wrapper function)
    
    Args:
        model: Model object
        preprocessed_input: Preprocessed image
        original_img: Original PIL Image
        model_type: 'tensorflow' or 'pytorch'
        layer_name: Target layer name (optional)
    
    Returns:
        Dict with:
            - heatmap_overlay: PIL Image with overlay
            - heatmap_raw: Raw heatmap array
            - layer_used: Name of layer used
    """
    try:
        if model_type == 'tensorflow' and TF_AVAILABLE:
            heatmap, layer_used = generate_gradcam_tensorflow(
                model, preprocessed_input, layer_name
            )
        elif model_type == 'pytorch' and TORCH_AVAILABLE:
            # For PyTorch, need to specify target layer
            # This is a simplified version - in production, specify the layer
            if layer_name is None:
                # Try to find last conv layer
                for name, module in model.named_modules():
                    if isinstance(module, torch.nn.Conv2d):
                        layer_name = name
                if layer_name is None:
                    raise ValueError("Could not find convolutional layer")
            
            target_layer = dict(model.named_modules())[layer_name]
            heatmap = generate_gradcam_pytorch(model, preprocessed_input, target_layer)
            layer_used = layer_name
        else:
            raise ValueError(f"Model type {model_type} not supported or not available")
        
        # Overlay on original image
        overlay_img = overlay_heatmap_on_image(original_img, heatmap)
        
        return {
            'heatmap_overlay': overlay_img,
            'heatmap_raw': heatmap,
            'layer_used': layer_used
        }
        
    except Exception as e:
        print(f"Error generating GradCAM: {e}")
        return None
