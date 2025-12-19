"""
Advanced Medical Image Preprocessing for Parkinson's Detection
Handles noisy diffusion-weighted MRI images with forensic-level analysis
"""
import cv2
import numpy as np
from PIL import Image
import io


def forensic_image_analysis(image_bytes, filename="uploaded_image"):
    """
    Perform forensic-level analysis on medical MRI image
    
    Args:
        image_bytes: Raw image bytes
        filename: Name of the file for reporting
    
    Returns:
        Dictionary with detailed analysis results
    """
    # Load image
    img = Image.open(io.BytesIO(image_bytes)).convert('L')  # Grayscale
    img_array = np.array(img, dtype=np.uint8)
    
    analysis = {
        'filename': filename,
        'dimensions': img_array.shape,
        'dtype': str(img_array.dtype),
    }
    
    # Intensity statistics
    analysis['intensity'] = {
        'min': int(np.min(img_array)),
        'max': int(np.max(img_array)),
        'mean': float(np.mean(img_array)),
        'std': float(np.std(img_array))
    }
    
    # Histogram analysis
    hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
    peak_intensity = int(np.argmax(hist))
    bright_pixels = np.sum(img_array > 127)
    
    analysis['histogram'] = {
        'peak_intensity': peak_intensity,
        'bright_pixel_count': int(bright_pixels),
        'bright_pixel_percentage': float(bright_pixels / img_array.size * 100)
    }
    
    # Circle detection (for midbrain structures)
    circles = cv2.HoughCircles(
        img_array, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=20,
        param1=50, 
        param2=30, 
        minRadius=10, 
        maxRadius=100
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        analysis['circles'] = [
            {'center': (int(c[0]), int(c[1])), 'radius': int(c[2])}
            for c in circles[0, :]
        ]
    else:
        analysis['circles'] = []
    
    # Contour analysis
    _, binary = cv2.threshold(img_array, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        analysis['largest_contour'] = {
            'area': int(cv2.contourArea(largest_contour)),
            'perimeter': float(cv2.arcLength(largest_contour, True))
        }
    else:
        analysis['largest_contour'] = {'area': 0, 'perimeter': 0}
    
    # Edge detection
    edges = cv2.Canny(img_array, 50, 150)
    edge_pixel_count = np.sum(edges > 0)
    
    analysis['edges'] = {
        'canny_edge_pixels': int(edge_pixel_count),
        'edge_density': float(edge_pixel_count / img_array.size * 100)
    }
    
    # Centrality and symmetry
    moments = cv2.moments(img_array)
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        analysis['centrality'] = {
            'center_x': cx,
            'center_y': cy,
            'center_offset_from_image_center': float(
                np.sqrt((cx - img_array.shape[1]/2)**2 + (cy - img_array.shape[0]/2)**2)
            )
        }
    
    return analysis


def denoise_medical_image(img_array):
    """
    Apply advanced denoising to medical MRI image
    
    Args:
        img_array: Grayscale image array
    
    Returns:
        Denoised image array
    """
    # Non-local means denoising (best for medical images)
    denoised = cv2.fastNlMeansDenoising(img_array, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Bilateral filter to preserve edges while reducing noise
    denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
    
    return denoised


def enhance_contrast(img_array):
    """
    Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    
    Args:
        img_array: Grayscale image array
    
    Returns:
        Contrast-enhanced image array
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_array)
    return enhanced


def extract_brain_region(img_array):
    """
    Extract brain region and remove background noise
    
    Args:
        img_array: Grayscale image array
    
    Returns:
        Masked image with background removed
    """
    # Otsu's thresholding to separate brain from background
    _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Find largest connected component (brain)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
    
    if num_labels > 1:
        # Get largest component (excluding background)
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        brain_mask = (labels == largest_label).astype(np.uint8) * 255
        
        # Apply mask
        masked = cv2.bitwise_and(img_array, img_array, mask=brain_mask)
    else:
        masked = img_array
    
    return masked


def preprocess_noisy_mri(image_bytes, target_size=(224, 224)):
    """
    Complete preprocessing pipeline for noisy MRI images
    Optimized for Parkinson's detection
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target size for model input
    
    Returns:
        Preprocessed image ready for model (numpy array)
    """
    # Load as grayscale
    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    img_array = np.array(img, dtype=np.uint8)
    
    # Step 1: Denoise
    denoised = denoise_medical_image(img_array)
    
    # Step 2: Extract brain region (remove background noise)
    brain_only = extract_brain_region(denoised)
    
    # Step 3: Enhance contrast
    enhanced = enhance_contrast(brain_only)
    
    # Step 4: Resize to target size
    resized = cv2.resize(enhanced, target_size, interpolation=cv2.INTER_CUBIC)
    
    # Step 5: Convert back to RGB for model compatibility
    rgb_image = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
    
    return rgb_image


def preprocess_for_pytorch_with_denoising(image_bytes, target_size=(224, 224)):
    """
    Preprocess noisy MRI image for PyTorch models
    Includes advanced denoising and feature enhancement
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target size (height, width)
    
    Returns:
        Preprocessed tensor ready for model input
    """
    import torch
    
    # Apply advanced preprocessing
    rgb_array = preprocess_noisy_mri(image_bytes, target_size)
    
    # Convert to float32 and normalize to [0, 1]
    img_array = rgb_array.astype(np.float32) / 255.0
    
    # Apply ImageNet normalization (CRITICAL - must match training!)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    img_array = (img_array - mean) / std
    
    # Convert to tensor and transpose to (C, H, W)
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)
    
    # Add batch dimension (1, C, H, W)
    img_tensor = img_tensor.unsqueeze(0)
    
    return img_tensor
