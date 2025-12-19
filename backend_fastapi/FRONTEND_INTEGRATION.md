# Frontend Integration Guide

Complete guide for integrating your React frontend with the new FastAPI backend.

## Quick Reference

**Backend URL:** `http://localhost:8000`
**Frontend URL:** `http://localhost:5173` (Vite) or `http://localhost:3000` (CRA)

## Step 1: Update API Base URL

Create or update `src/utils/api.ts`:

```typescript
// Update the API base URL
const API_BASE = 'http://127.0.0.1:8000';  // Changed from 5000 to 8000

// Remove credentials: 'include' since we removed authentication
// All fetch calls should NOT include credentials
```

## Step 2: Update Prediction Functions

### MRI/X-ray Prediction

```typescript
// src/utils/api.ts
export const uploadXrayForEnsemblePrediction = async (
  file: File,
  patientName: string = "Anonymous"
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_name', patientName);

  const response = await fetch(`${API_BASE}/predict/mri`, {
    method: 'POST',
    body: formData,
    // NO credentials needed
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Prediction failed' }));
    throw new Error(error.error || 'MRI prediction failed');
  }

  return await response.json();
};
```

### CSV Prediction (NEW)

```typescript
// src/utils/api.ts
export const uploadCSVForPrediction = async (
  features: Record<string, number>,
  patientName: string = "Anonymous"
): Promise<any> => {
  const response = await fetch(`${API_BASE}/predict/csv`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      features,
      patient_name: patientName
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Prediction failed' }));
    throw new Error(error.error || 'CSV prediction failed');
  }

  return await response.json();
};
```

## Step 3: Create CSV Input Page

Create `src/pages/CSVUploadPage.tsx`:

```typescript
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { uploadCSVForPrediction } from '../utils/api';

const CSV_FEATURES = [
  { name: "MDVP:Fo(Hz)", label: "Fundamental Frequency (Hz)", min: 80, max: 300, default: 150 },
  { name: "MDVP:Fhi(Hz)", label: "Maximum Frequency (Hz)", min: 100, max: 600, default: 200 },
  { name: "MDVP:Flo(Hz)", label: "Minimum Frequency (Hz)", min: 60, max: 250, default: 100 },
  { name: "MDVP:Jitter(%)", label: "Jitter (%)", min: 0, max: 5, default: 0.5, step: 0.001 },
  { name: "MDVP:Jitter(Abs)", label: "Absolute Jitter", min: 0, max: 0.01, default: 0.0001, step: 0.00001 },
  { name: "MDVP:RAP", label: "RAP", min: 0, max: 0.05, default: 0.002, step: 0.0001 },
  { name: "MDVP:PPQ", label: "PPQ", min: 0, max: 0.05, default: 0.002, step: 0.0001 },
  { name: "Jitter:DDP", label: "DDP", min: 0, max: 0.1, default: 0.005, step: 0.001 },
  { name: "MDVP:Shimmer", label: "Shimmer", min: 0, max: 0.2, default: 0.03, step: 0.001 },
  { name: "MDVP:Shimmer(dB)", label: "Shimmer (dB)", min: 0, max: 2, default: 0.3, step: 0.01 },
  { name: "Shimmer:APQ3", label: "APQ3", min: 0, max: 0.1, default: 0.015, step: 0.001 },
  { name: "Shimmer:APQ5", label: "APQ5", min: 0, max: 0.1, default: 0.02, step: 0.001 },
  { name: "MDVP:APQ", label: "APQ", min: 0, max: 0.15, default: 0.025, step: 0.001 },
  { name: "Shimmer:DDA", label: "DDA", min: 0, max: 0.3, default: 0.045, step: 0.001 },
  { name: "NHR", label: "Noise-to-Harmonics Ratio", min: 0, max: 0.5, default: 0.02, step: 0.001 },
  { name: "HNR", label: "Harmonics-to-Noise Ratio", min: 0, max: 40, default: 22, step: 0.1 },
  { name: "RPDE", label: "RPDE", min: 0, max: 1, default: 0.5, step: 0.001 },
  { name: "DFA", label: "DFA", min: 0, max: 1, default: 0.7, step: 0.001 },
  { name: "spread1", label: "Spread 1", min: -10, max: 0, default: -5, step: 0.1 },
  { name: "spread2", label: "Spread 2", min: 0, max: 1, default: 0.2, step: 0.001 },
  { name: "D2", label: "D2", min: 0, max: 5, default: 2, step: 0.01 },
  { name: "PPE", label: "PPE", min: 0, max: 1, default: 0.2, step: 0.001 }
];

const CSVUploadPage: React.FC = () => {
  const [features, setFeatures] = useState<Record<string, number>>({});
  const [patientName, setPatientName] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFeatureChange = (featureName: string, value: string) => {
    setFeatures({
      ...features,
      [featureName]: parseFloat(value) || 0
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setError(null);

    try {
      const prediction = await uploadCSVForPrediction(features, patientName);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadPDF = () => {
    if (result?.report_pdf_base64) {
      const link = document.createElement('a');
      link.href = `data:application/pdf;base64,${result.report_pdf_base64}`;
      link.download = `parkinson_report_${Date.now()}.pdf`;
      link.click();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="py-12"
    >
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8 text-center">
          Clinical Feature Analysis
        </h1>

        <div className="max-w-6xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Patient Name */}
            <div className="bg-white p-6 rounded-lg shadow">
              <label className="block text-sm font-medium mb-2">
                Patient Name (Optional)
              </label>
              <input
                type="text"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
                placeholder="Enter patient name"
              />
            </div>

            {/* Feature Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {CSV_FEATURES.map((feature) => (
                <div key={feature.name} className="bg-white p-4 rounded-lg shadow">
                  <label className="block text-sm font-medium mb-2">
                    {feature.label}
                  </label>
                  <input
                    type="number"
                    step={feature.step || 0.001}
                    min={feature.min}
                    max={feature.max}
                    defaultValue={feature.default}
                    onChange={(e) => handleFeatureChange(feature.name, e.target.value)}
                    className="w-full px-3 py-2 border rounded"
                    required
                  />
                  <span className="text-xs text-gray-500 mt-1 block">
                    Range: {feature.min} - {feature.max}
                  </span>
                </div>
              ))}
            </div>

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={isAnalyzing}
                className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Features'}
              </button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {/* Results Display */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 bg-white p-6 rounded-lg shadow"
            >
              <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
              
              <div className="space-y-4">
                <div>
                  <span className="font-semibold">Diagnosis:</span>{' '}
                  <span className={result.diagnosis === "Parkinson's" ? 'text-red-600' : 'text-green-600'}>
                    {result.diagnosis}
                  </span>
                </div>
                
                <div>
                  <span className="font-semibold">Confidence:</span>{' '}
                  {(result.confidence * 100).toFixed(1)}%
                </div>

                {/* Feature Importance Chart */}
                {result.chart_base64 && (
                  <div className="mt-4">
                    <h3 className="font-semibold mb-2">Feature Importance</h3>
                    <img 
                      src={result.chart_base64} 
                      alt="Feature Importance"
                      className="w-full rounded-lg"
                    />
                  </div>
                )}

                {/* Download PDF */}
                <button
                  onClick={downloadPDF}
                  className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Download PDF Report
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default CSVUploadPage;
```

## Step 4: Update App.tsx Routes

```typescript
// src/App.tsx
import CSVUploadPage from './pages/CSVUploadPage';

// Add route
<Route path="/csv-analysis" element={<CSVUploadPage />} />
```

## Step 5: Update Navbar

```typescript
// src/components/layout/Navbar.tsx
const navLinks = [
  { name: 'Home', path: '/' },
  { name: 'MRI Analysis', path: '/upload' },
  { name: 'CSV Analysis', path: '/csv-analysis' },  // NEW
  { name: 'Hologram', path: '/hologram' },
  { name: 'Reports', path: '/report' },
  { name: 'Assistant', path: '/chatbot' },
];
```

## Step 6: Update Result Display

Update your `ResultCard` component to handle new response format:

```typescript
// src/components/upload/ResultCard.tsx
interface ResultCardProps {
  result: {
    diagnosis: string;
    confidence: number;
    individual_predictions?: Record<string, any>;
    ensemble_info?: {
      num_models: number;
      ensemble_probabilities: Record<string, number>;
    };
    xai_images?: {
      gradcam_base64?: string;
      lime_base64?: string;
    };
    summary?: string;
    report_pdf_base64?: string;
  } | null;
  // ... other props
}

// In component:
{result.xai_images?.gradcam_base64 && (
  <div>
    <h3>GradCAM Heatmap</h3>
    <img src={result.xai_images.gradcam_base64} alt="GradCAM" />
  </div>
)}

{result.ensemble_info && (
  <div>
    <h3>Ensemble Analysis</h3>
    <p>Models used: {result.ensemble_info.num_models}</p>
    {/* Display individual predictions */}
  </div>
)}
```

## Step 7: Test the Integration

1. **Start FastAPI backend:**
```bash
cd backend_fastapi
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

2. **Start React frontend:**
```bash
npm run dev
```

3. **Test endpoints:**
- Navigate to http://localhost:5173
- Try MRI upload
- Try CSV analysis
- Check console for errors

## Common Issues & Fixes

### CORS Errors
If you see CORS errors, update `backend_fastapi/app.py`:
```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

### Port Conflicts
- Backend: Port 8000 (FastAPI)
- Frontend: Port 5173 (Vite) or 3000 (CRA)
- Old Flask backend was on port 5000

### Base64 Image Display
```typescript
// Correct way to display base64 images
<img src={gradcamBase64} alt="GradCAM" />
// gradcamBase64 already includes "data:image/png;base64," prefix
```

### PDF Download
```typescript
const downloadPDF = (base64: string) => {
  const link = document.createElement('a');
  link.href = `data:application/pdf;base64,${base64}`;
  link.download = `report_${Date.now()}.pdf`;
  link.click();
};
```

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Update API base URL in frontend
3. ✅ Add CSV analysis page
4. ✅ Update routes and navigation
5. ✅ Test all endpoints
6. 🔄 Deploy to production (optional)

## Production Deployment

### Backend (FastAPI)
```bash
# Using Docker
docker build -t parkinsons-api ./backend_fastapi
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key parkinsons-api

# Or using Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (React)
```bash
npm run build
# Deploy dist/ folder to Netlify, Vercel, etc.
```

## Summary

- ✅ FastAPI backend on port 8000
- ✅ 4 modalities: MRI, Handwriting, Voice, CSV
- ✅ XAI visualizations (GradCAM, LIME)
- ✅ PDF reports with charts
- ✅ AI chatbot
- ✅ No authentication required
- ✅ CORS enabled for frontend

Your application is now ready for multi-modal Parkinson's detection!
