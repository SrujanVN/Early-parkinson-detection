📌 Early Parkinson's Detection using MRI and Deep Learning

📖 Introduction  
Parkinson’s disease (PD) is a progressive neurodegenerative disorder that affects movement and motor control. Early detection is essential for timely intervention and better disease management. This project leverages **MRI imaging data** and **EfficientNet-based deep learning models** to detect early signs of Parkinson’s Disease.

⚠ Disclaimer: This model achieves up to **84% validation accuracy** but should not be used as a substitute for professional medical advice. Always consult a neurologist or certified healthcare provider.

📂 Project Structure  
Early-parkinson-detection/  
│-- train_model.py                             # Model training pipeline  
│-- evaluate_model.py                          # Model evaluation script  
│-- gradcam_visualizer.py                      # Grad-CAM visualization for model explainability  
│-- lime_explainer.py                          # LIME-based local explainability  
│-- shap_explainer.py                          # SHAP-based feature explanation  
│-- models/                                     # Trained models (H5 files)  
│   │-- best_parkinsons_model_auto.h5  
│-- data/                                       # Dataset folder (MRI scans)  
│-- plots/                                      # Training history visualizations  
│   │-- training_history.png  
│-- requirements.txt                            # Python package dependencies  
│-- README.md                                   # Project documentation  

🚀 How to Run the Project  

**Prerequisites**  
- Python >= 3.7  
- TensorFlow >= 2.9  
- scikit-learn  
- OpenCV  
- SHAP, LIME, Matplotlib

  ## 🎯 Live Demo  
🔗 <a href=["https://breast-cancer-early-detection.netlify.app](https://early-parkinsons-detection.netlify.app/)">** Early Parkinson's Detection **</a>


**Steps**  

1. Clone the repository  
```bash
git clone https://github.com/SrujanVN/Early-parkinson-detection.git  
cd Early-parkinson-detection  
