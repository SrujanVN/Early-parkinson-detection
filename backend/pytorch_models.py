"""
PyTorch Model Architectures for MRI Parkinson's Detection
Defines architectures for ResNet50, DenseNet121, EfficientNet-B0, and EfficientNet-B3
"""
import torch
import torch.nn as nn
try:
    import torchvision.models as models
    TORCHVISION_AVAILABLE = True
except ImportError:
    TORCHVISION_AVAILABLE = False
    models = None

try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False
    timm = None


def create_resnet50(num_classes=3, pretrained=False):
    """Create ResNet50 model for Parkinson's detection"""
    if not TORCHVISION_AVAILABLE:
        raise ImportError("torchvision is required for ResNet50")
    
    model = models.resnet50(pretrained=pretrained)
    # Modify final layer for num_classes
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def create_densenet121(num_classes=3, pretrained=False):
    """Create DenseNet121 model for Parkinson's detection"""
    if not TORCHVISION_AVAILABLE:
        raise ImportError("torchvision is required for DenseNet121")
    
    model = models.densenet121(pretrained=pretrained)
    # Modify final layer for num_classes
    model.classifier = nn.Linear(model.classifier.in_features, num_classes)
    return model


def create_efficientnet_b0(num_classes=3, pretrained=False):
    """Create EfficientNet-B0 model for Parkinson's detection"""
    if TIMM_AVAILABLE:
        # Use timm if available (preferred)
        model = timm.create_model('efficientnet_b0', pretrained=pretrained, num_classes=num_classes)
    elif TORCHVISION_AVAILABLE:
        # Fallback to torchvision
        model = models.efficientnet_b0(pretrained=pretrained)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    else:
        raise ImportError("Either timm or torchvision is required for EfficientNet-B0")
    
    return model


def create_efficientnet_b3(num_classes=3, pretrained=False):
    """Create EfficientNet-B3 model for Parkinson's detection"""
    if TIMM_AVAILABLE:
        # Use timm (preferred for B3)
        model = timm.create_model('efficientnet_b3', pretrained=pretrained, num_classes=num_classes)
    elif TORCHVISION_AVAILABLE:
        # Fallback to torchvision
        model = models.efficientnet_b3(pretrained=pretrained)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    else:
        raise ImportError("Either timm or torchvision is required for EfficientNet-B3")
    
    return model


def load_pytorch_model(model_path, model_type='resnet50', num_classes=3):
    """
    Load a PyTorch model with state_dict
    
    Args:
        model_path: Path to .pth file containing state_dict
        model_type: Type of model ('resnet50', 'densenet121', 'efficientnet_b0', 'efficientnet_b3')
        num_classes: Number of output classes
    
    Returns:
        Loaded model in eval mode
    """
    # Create model architecture
    if model_type == 'resnet50':
        model = create_resnet50(num_classes=num_classes, pretrained=False)
    elif model_type == 'densenet121':
        model = create_densenet121(num_classes=num_classes, pretrained=False)
    elif model_type == 'efficientnet_b0':
        model = create_efficientnet_b0(num_classes=num_classes, pretrained=False)
    elif model_type == 'efficientnet_b3':
        model = create_efficientnet_b3(num_classes=num_classes, pretrained=False)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Load state dict
    state_dict = torch.load(model_path, map_location='cpu')
    model.load_state_dict(state_dict)
    
    # Set to evaluation mode
    model.eval()
    
    return model
