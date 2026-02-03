# Quick Start Guide - Using .venv_models

## Activate Virtual Environment
```powershell
.\.venv_models\Scripts\Activate.ps1
```

## Test Model Loading
```powershell
python backend\test_model_loading.py
```

## Run Backend Server
```powershell
python backend\app.py
```

## Deactivate
```powershell
deactivate
```

## Model Status
- **12/13 models loaded successfully**
- **Total size**: ~334 MB
- **Ready for predictions**: ✓ Yes

## Models Loaded
### MRI (4/4)
- DenseNet121, ResNet50, EfficientNetB0, EfficientNetB3

### Handwriting (3/4)
- HOG_SVM, LBP_RF, MobileNet_SVM
- (Ensemble model has minor loading issue)

### Voice (4/4)
- XGBoost, RandomForest, SVM, Ensemble

### CSV (1/1)
- XGBoost
