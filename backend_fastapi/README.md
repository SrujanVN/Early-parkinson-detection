# FastAPI Backend for Parkinson's Disease Detection

Comprehensive multi-modal AI system for early Parkinson's disease detection using MRI images, handwriting analysis, voice biomarkers, and clinical features.

## Features

- **Multi-Modal Analysis**: MRI/CT scans, handwriting images, voice audio, CSV clinical features
- **Ensemble Learning**: Multiple deep learning and ML models for robust predictions
- **Explainable AI (XAI)**: GradCAM heatmaps and LIME feature importance
- **PDF Reports**: Professional medical reports with visualizations
- **AI Chatbot**: Gemini-powered assistant for Parkinson's information
- **CORS Enabled**: Ready for React frontend integration

## Quick Start

### 1. Install Dependencies

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### 2. Set Up Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Copy Models

Ensure models are in the correct directory structure:
```
backend_fastapi/
├── models/
│   ├── Parkinson_mri/
│   │   ├── best_resnet50.pth
│   │   ├── best_densenet121.pth
│   │   ├── best_efficientnet_b0.pth
│   │   └── best_efficientnet_b3.pth
│   ├── Parkinson_handwriting/
│   │   ├── parkinson_ensemble_open_set.pkl
│   │   ├── hog_svm_open_set.pkl
│   │   ├── lbp_rf_open_set.pkl
│   │   └── mobilenet_svm_open_set.pkl
│   ├── parkinsons_voice/
│   │   ├── ensemble_parkinson_voice.pkl
│   │   ├── random_forest_parkinson_voice.pkl
│   │   ├── svm_parkinson_voice.pkl
│   │   └── xgboost_parkinson_voice.pkl
│   └── parkinsions_csv/
│       └── parkinson_xgboost.pkl
```

**Copy from existing backend:**
```bash
cp -r ../backend/models ./
```

### 4. Run Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /
GET /health
```

### MRI/CT Scan Prediction
```bash
POST /predict/mri
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPEG, PNG)
- patient_name: string (optional)

Response:
{
  "diagnosis": "Parkinson's" | "Normal" | "Unknown",
  "confidence": 0.95,
  "individual_predictions": {...},
  "ensemble_info": {...},
  "summary": "...",
  "xai_images": {
    "gradcam_base64": "data:image/png;base64,...",
    "lime_base64": "data:image/png;base64,..."
  },
  "report_pdf_base64": "..."
}
```

### Handwriting Analysis
```bash
POST /predict/handwriting
Content-Type: multipart/form-data

Parameters:
- file: Image file
- patient_name: string (optional)
```

### Voice Analysis
```bash
POST /predict/voice
Content-Type: multipart/form-data

Parameters:
- file: Audio file (WAV, MP3)
- patient_name: string (optional)
```

### CSV Feature Prediction
```bash
POST /predict/csv
Content-Type: application/json

Body:
{
  "features": {
    "MDVP:Fo(Hz)": 119.992,
    "MDVP:Fhi(Hz)": 157.302,
    ...
  },
  "patient_name": "John Doe"
}
```

### Chatbot
```bash
POST /chat
Content-Type: application/json

Body:
{
  "message": "What are early signs of Parkinson's?",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Frontend Integration

### React Example

```typescript
// MRI Prediction
const predictMRI = async (file: File, patientName: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_name', patientName);
  
  const response = await fetch('http://localhost:8000/predict/mri', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// CSV Prediction
const predictCSV = async (features: Record<string, number>) => {
  const response = await fetch('http://localhost:8000/predict/csv', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features, patient_name: 'Patient' })
  });
  
  return await response.json();
};

// Display base64 image
<img src={result.xai_images.gradcam_base64} alt="GradCAM" />

// Download PDF report
const downloadPDF = (base64: string) => {
  const link = document.createElement('a');
  link.href = `data:application/pdf;base64,${base64}`;
  link.download = 'medical_report.pdf';
  link.click();
};
```

### CSV Input Form

```tsx
const CSVForm = () => {
  const [features, setFeatures] = useState({});
  
  const featureFields = [
    { name: "MDVP:Fo(Hz)", label: "Fundamental Frequency", unit: "Hz" },
    { name: "MDVP:Jitter(%)", label: "Jitter", unit: "%" },
    // ... add all 22 features
  ];
  
  return (
    <div className="grid grid-cols-2 gap-4">
      {featureFields.map(field => (
        <div key={field.name} className="card">
          <label>{field.label} ({field.unit})</label>
          <input
            type="number"
            step="0.001"
            onChange={(e) => setFeatures({
              ...features,
              [field.name]: parseFloat(e.target.value)
            })}
          />
        </div>
      ))}
      <button onClick={() => predictCSV(features)}>
        Analyze
      </button>
    </div>
  );
};
```

## Docker Deployment

### Build Image
```bash
docker build -t parkinsons-api .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -e GEMINI_API_KEY=your_key \
  --name parkinsons-api \
  parkinsons-api
```

## Model Information

### MRI Models (PyTorch)
- **ResNet50**: Deep residual network
- **DenseNet121**: Densely connected network
- **EfficientNet-B0**: Efficient scaling
- **EfficientNet-B3**: Larger efficient network

All models output 3 classes: Normal (0), Parkinson's (1), Unknown (2)

### Handwriting Models (Sklearn/XGBoost)
- **Ensemble**: Combined predictions
- **HOG + SVM**: Histogram of Oriented Gradients
- **LBP + Random Forest**: Local Binary Patterns
- **MobileNet + SVM**: Deep features

Open-set classification: -1 = unknown, 0 = normal, 1 = Parkinson's

### Voice Models (Sklearn/XGBoost)
- **Ensemble**: Combined predictions
- **Random Forest**: Tree-based ensemble
- **SVM**: Support Vector Machine
- **XGBoost**: Gradient boosting

Binary classification: 0 = normal, 1 = Parkinson's

### CSV Model (XGBoost)
Single XGBoost model trained on 22 voice biomarker features

## Troubleshooting

### CUDA/GPU Issues
If CUDA is not available, models will automatically use CPU. For GPU:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Memory Issues
Large models may require significant RAM. Consider:
- Reducing batch size
- Loading models on-demand
- Using model quantization

### CORS Errors
Update allowed origins in `app.py`:
```python
allow_origins=["http://your-frontend-url:port"]
```

## Performance Tips

1. **Model Caching**: Models are loaded once at startup
2. **Async Processing**: Use FastAPI's async capabilities
3. **Image Preprocessing**: Resize images before upload
4. **PDF Generation**: Can be moved to background tasks

## Security Notes

- **No Authentication**: Currently public API (as per requirements)
- **Input Validation**: Basic validation implemented
- **File Size Limits**: Consider adding limits for production
- **Rate Limiting**: Implement for production deployment

## License

Medical AI System - Use responsibly with proper medical oversight

## Support

For issues or questions, consult the API documentation at `/docs` (FastAPI auto-generated)
