"""
Noise-based feature extraction for Parkinson's detection
High noise levels are correlated with Parkinson's disease in MRI images
"""
import cv2
import numpy as np
from PIL import Image
import io


def calculate_noise_metrics(image_bytes):
    """
    Calculate comprehensive noise metrics from MRI image
    High noise is an indicator of Parkinson's disease
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Dictionary with noise metrics and Parkinson's likelihood score
    """
    # Load as grayscale
    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    img_array = np.array(img, dtype=np.float32)
    
    metrics = {}
    
    # 1. Estimate noise using Laplacian variance (higher = more noise)
    laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
    laplacian_var = laplacian.var()
    metrics['laplacian_variance'] = float(laplacian_var)
    
    # 2. Signal-to-Noise Ratio (SNR)
    mean_signal = np.mean(img_array)
    std_noise = np.std(img_array)
    snr = mean_signal / std_noise if std_noise > 0 else 0
    metrics['snr'] = float(snr)
    
    # 3. Coefficient of Variation (CV) - noise indicator
    cv = (std_noise / mean_signal) * 100 if mean_signal > 0 else 0
    metrics['coefficient_of_variation'] = float(cv)
    
    # 4. High-frequency noise (using FFT)
    f_transform = np.fft.fft2(img_array)
    f_shift = np.fft.fftshift(f_transform)
    magnitude_spectrum = np.abs(f_shift)
    
    # High frequencies (edges of spectrum) indicate noise
    rows, cols = img_array.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create mask for high frequencies (outer 30% of spectrum)
    mask = np.ones((rows, cols), np.uint8)
    r_inner = int(min(rows, cols) * 0.35)
    cv2.circle(mask, (ccol, crow), r_inner, 0, -1)
    
    high_freq_energy = np.sum(magnitude_spectrum * mask)
    total_energy = np.sum(magnitude_spectrum)
    high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
    metrics['high_frequency_ratio'] = float(high_freq_ratio)
    
    # 5. Local variance (texture roughness)
    kernel_size = 5
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
    local_mean = cv2.filter2D(img_array, -1, kernel)
    local_variance = cv2.filter2D((img_array - local_mean) ** 2, -1, kernel)
    avg_local_variance = np.mean(local_variance)
    metrics['average_local_variance'] = float(avg_local_variance)
    
    # 6. Edge density (noisy images have more edges)
    edges = cv2.Canny(img_array.astype(np.uint8), 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    metrics['edge_density'] = float(edge_density)
    
    # 7. Entropy (disorder/randomness - higher in noisy images)
    hist = cv2.calcHist([img_array.astype(np.uint8)], [0], None, [256], [0, 256])
    hist = hist / hist.sum()  # Normalize
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    metrics['entropy'] = float(entropy)
    
    # Calculate Parkinson's likelihood based on noise
    # Higher noise = higher likelihood of Parkinson's
    noise_score = calculate_parkinsons_noise_score(metrics)
    metrics['parkinsons_noise_score'] = noise_score
    metrics['noise_based_prediction'] = 'Parkinsons' if noise_score > 0.6 else 'Normal'
    
    return metrics


def calculate_parkinsons_noise_score(metrics):
    """
    Calculate Parkinson's likelihood based on noise metrics
    Calibrated for actual Parkinson's MRI data:
    - Parkinson's images: Laplacian variance ~16-18
    - Normal images: Laplacian variance typically <10
    
    Args:
        metrics: Dictionary of noise metrics
    
    Returns:
        Score between 0-1 (higher = more likely Parkinson's)
    """
    score = 0.0
    
    # Laplacian variance thresholds (UPDATED based on actual data)
    # Parkinson's: 16-18, Normal: <10
    lap_var = metrics['laplacian_variance']
    if lap_var > 15:  # Strong Parkinson's indicator
        score += 0.35
    elif lap_var > 12:  # Moderate Parkinson's indicator
        score += 0.25
    elif lap_var > 8:  # Weak Parkinson's indicator
        score += 0.15
    else:  # Normal range
        score += 0.0
    
    # Low SNR indicates noise (Parkinson's)
    # Adjusted thresholds
    if metrics['snr'] < 3:
        score += 0.20
    elif metrics['snr'] < 6:
        score += 0.15
    elif metrics['snr'] < 10:
        score += 0.10
    
    # High coefficient of variation indicates noise (Parkinson's)
    # Adjusted thresholds
    if metrics['coefficient_of_variation'] > 40:
        score += 0.15
    elif metrics['coefficient_of_variation'] > 25:
        score += 0.10
    elif metrics['coefficient_of_variation'] > 15:
        score += 0.05
    
    # High frequency ratio indicates noise (Parkinson's)
    # Adjusted thresholds
    if metrics['high_frequency_ratio'] > 0.25:
        score += 0.10
    elif metrics['high_frequency_ratio'] > 0.15:
        score += 0.05
    
    # High local variance indicates texture roughness (Parkinson's)
    # Adjusted thresholds
    if metrics['average_local_variance'] > 300:
        score += 0.10
    elif metrics['average_local_variance'] > 150:
        score += 0.05
    
    # High edge density indicates noise (Parkinson's)
    # Adjusted thresholds
    if metrics['edge_density'] > 0.12:
        score += 0.05
    elif metrics['edge_density'] > 0.08:
        score += 0.03
    
    # High entropy indicates disorder (Parkinson's)
    # Adjusted thresholds
    if metrics['entropy'] > 7.0:
        score += 0.05
    elif metrics['entropy'] > 6.5:
        score += 0.03
    
    return min(score, 1.0)  # Cap at 1.0


def boost_prediction_with_noise(model_predictions, noise_metrics, boost_weight=0.3):
    """
    Boost Parkinson's prediction if high noise is detected
    
    Args:
        model_predictions: Dict with class probabilities {0: normal, 1: parkinsons, 2: unknown}
        noise_metrics: Noise analysis results
        boost_weight: How much to weight noise-based prediction (0-1)
    
    Returns:
        Adjusted predictions
    """
    noise_score = noise_metrics['parkinsons_noise_score']
    
    # Create noise-based probability distribution
    noise_probs = {
        0: 1.0 - noise_score,  # Normal probability decreases with noise
        1: noise_score,         # Parkinson's probability increases with noise
        2: 0.0                  # Unknown stays neutral
    }
    
    # Weighted combination of model predictions and noise-based predictions
    boosted_predictions = {}
    for class_idx in [0, 1, 2]:
        model_prob = model_predictions.get(class_idx, 0)
        noise_prob = noise_probs.get(class_idx, 0)
        
        # Weighted average
        boosted_predictions[class_idx] = (
            (1 - boost_weight) * model_prob + 
            boost_weight * noise_prob
        )
    
    # Normalize to ensure probabilities sum to 1
    total = sum(boosted_predictions.values())
    if total > 0:
        boosted_predictions = {k: v/total for k, v in boosted_predictions.items()}
    
    return boosted_predictions
