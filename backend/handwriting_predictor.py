import os
import joblib
import numpy as np
import cv2
from PIL import Image
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from skimage.feature import hog, local_binary_pattern

class HandwritingPredictor:
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.models_dir = os.path.join(self.backend_dir, "models", "Parkinson_handwriting")
        self.models = {}
        self.is_ready = False
        
        # Class names
        self.class_names = {0: "Normal", 1: "Parkinson's", 2: "Unknown"}
        
        # Device for MobileNet feature extraction
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize MobileNet model for feature extraction
        # MobileNetV2's classifier input is 1280
        self.mobilenet_extractor = models.mobilenet_v2(pretrained=True)
        self.mobilenet_extractor.classifier = nn.Identity() # Remove the classifier head
        self.mobilenet_extractor.to(self.device)
        self.mobilenet_extractor.eval()
        
        self.mobilenet_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_models(self):
        """Load all handwriting models"""
        model_configs = [
            {"name": "hog_svm", "file": "hog_svm_open_set.pkl"},
            {"name": "lbp_rf", "file": "lbp_rf_open_set.pkl"},
            {"name": "mobilenet_svm", "file": "mobilenet_svm_open_set.pkl"}
        ]
        
        loaded_count = 0
        for config in model_configs:
            path = os.path.join(self.models_dir, config["file"])
            if os.path.exists(path):
                try:
                    self.models[config["name"]] = joblib.load(path)
                    loaded_count += 1
                    print(f"[OK] Handwriting model loaded: {config['name']}")
                except Exception as e:
                    print(f"[ERROR] Failed to load handwriting model {config['name']}: {e}")
            else:
                print(f"[WARNING] Handwriting model file not found: {path}")
        
        # Try to load the ensemble if possible, otherwise we will use voting
        ensemble_path = os.path.join(self.models_dir, "parkinson_ensemble_open_set.pkl")
        if os.path.exists(ensemble_path):
            try:
                # Note: This might fail if the class definition is missing, which we saw earlier
                self.models["ensemble"] = joblib.load(ensemble_path)
                print("[OK] Handwriting ensemble loaded")
            except Exception:
                print("[INFO] Dedicated ensemble object failed to load. Will use majority voting instead.")
        
        self.is_ready = len(self.models) > 0
        return self.is_ready

    def extract_hog_features(self, image):
        """Extract 8100 HOG features (128x128 input)"""
        # Resize to 128x128 for 8100 features
        img_resized = cv2.resize(image, (128, 128))
        if len(img_resized.shape) == 3:
            img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img_resized
            
        features = hog(img_gray, orientations=9, pixels_per_cell=(8, 8),
                      cells_per_block=(2, 2), visualize=False)
        return features.reshape(1, -1)

    def extract_lbp_features(self, image):
        """Extract 26 LBP features"""
        if len(image.shape) == 3:
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = image
            
        # P=24, R=3, uniform method gives 26 features
        lbp = local_binary_pattern(img_gray, P=24, R=3, method="uniform")
        (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, 24 + 3), range=(0, 24 + 2))
        
        # Normalize histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-7)
        
        return hist.reshape(1, -1)

    def extract_mobilenet_features(self, image_pil):
        """Extract 1280 MobileNet features"""
        img_tensor = self.mobilenet_transform(image_pil).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.mobilenet_extractor(img_tensor)
        return features.cpu().numpy().reshape(1, -1)

    def predict(self, image_bytes):
        """Perform ensemble prediction on handwriting image"""
        if not self.is_ready:
            if not self.load_models():
                return {"error": "Handwriting models not initialized"}

        # Load image once for all extractors
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        all_results = {}
        votes = []
        confidences = []
        
        # 1. HOG + SVM
        if "hog_svm" in self.models:
            hog_feats = self.extract_hog_features(img_cv2)
            pred = self.models["hog_svm"].predict(hog_feats)[0]
            prob = self.models["hog_svm"].predict_proba(hog_feats)[0] if hasattr(self.models["hog_svm"], "predict_proba") else None
            
            p_class = int(pred) if pred != -1 else 2
            all_results["hog_svm"] = {
                "prediction": self.class_names[p_class],
                "confidence": float(np.max(prob)) if prob is not None else 0.5
            }
            votes.append(p_class)
            if prob is not None: confidences.append(float(np.max(prob)))

        # 2. LBP + RF
        if "lbp_rf" in self.models:
            lbp_feats = self.extract_lbp_features(img_cv2)
            pred = self.models["lbp_rf"].predict(lbp_feats)[0]
            prob = self.models["lbp_rf"].predict_proba(lbp_feats)[0] if hasattr(self.models["lbp_rf"], "predict_proba") else None
            
            p_class = int(pred) if pred != -1 else 2
            all_results["lbp_rf"] = {
                "prediction": self.class_names[p_class],
                "confidence": float(np.max(prob)) if prob is not None else 0.5
            }
            votes.append(p_class)
            if prob is not None: confidences.append(float(np.max(prob)))

        # 3. MobileNet + SVM
        if "mobilenet_svm" in self.models:
            mnet_feats = self.extract_mobilenet_features(img_pil)
            pred = self.models["mobilenet_svm"].predict(mnet_feats)[0]
            prob = self.models["mobilenet_svm"].predict_proba(mnet_feats)[0] if hasattr(self.models["mobilenet_svm"], "predict_proba") else None
            
            p_class = int(pred) if pred != -1 else 2
            all_results["mobilenet_svm"] = {
                "prediction": self.class_names[p_class],
                "confidence": float(np.max(prob)) if prob is not None else 0.5
            }
            votes.append(p_class)
            if prob is not None: confidences.append(float(np.max(prob)))

        # Ensemble Logic
        if "ensemble" in self.models:
            # If we had the combined features, we could use the ensemble object
            # But since it failed to load locally, we use majority vote or weighted average
            pass
            
        # Majority voting for the final consensus
        if not votes:
            return {"error": "No predictions generated"}

        # Custom voting logic: If there's a 3-way tie, or low agreement, default to Unknown (2)
        # This helps filter out non-spiral/wave images that result in conflicting predictions
        counts = {cls: votes.count(cls) for cls in set(votes)}
        max_votes = max(counts.values())
        
        # Check for tie
        winners = [cls for cls, count in counts.items() if count == max_votes]
        
        if len(winners) > 1:
            # If tie, default to Unknown if present, otherwise Unknown (safe fallback)
            consensus_class = 2
        else:
            consensus_class = winners[0]
            
        consensus_prob = np.mean(confidences) if confidences else 0.5
        
        # Adjust confidence based on agreement
        agreement = votes.count(consensus_class) / len(votes)
        final_confidence = (consensus_prob + agreement) / 2

        return {
            "diagnosis": self.class_names[consensus_class],
            "confidence": float(final_confidence),
            "individual_predictions": all_results,
            "summary": f"Handwriting analysis shows high correlation with {self.class_names[consensus_class]} patterns. Ensemble agreement: {agreement:.1f}."
        }

# Global instance
handwriting_predictor = HandwritingPredictor()
