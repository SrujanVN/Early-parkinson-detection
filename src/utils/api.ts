// API client for the NeuroAid application
// Connects to the Flask backend API

import { ModelPrediction } from './modelService';

const API_BASE = 'http://127.0.0.1:5000';

// Store the latest prediction result
let latestPrediction: any = null;

export type FileType = 'MRI' | 'Handwriting' | 'Audio' | 'CSV';

// Helper function to make authenticated API requests
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Include cookies for session management
    headers: {
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Function to upload file and get prediction (legacy endpoint)
export const uploadFileForPrediction = async (
  file: File,
  fileType: FileType
): Promise<ModelPrediction> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('fileType', fileType);

  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Prediction failed' }));
    throw new Error(error.error || 'Prediction failed');
  }

  const data = await response.json();

  const prediction: ModelPrediction = {
    diagnosis: data.diagnosis,
    confidence: data.confidence,
    timestamp: new Date().toISOString(),
  };

  return prediction;
};

// Function to upload X-ray/CT image for ensemble prediction with GradCAM
export const uploadXrayForEnsemblePrediction = async (
  file: File
): Promise<import('./modelService').EnsemblePrediction> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('fileType', 'MRI');

  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Prediction failed' }));
    throw new Error(error.error || 'Ensemble prediction failed');
  }

  const data = await response.json();

  const prediction: import('./modelService').EnsemblePrediction = {
    diagnosis: data.diagnosis,
    confidence: data.confidence,
    timestamp: new Date().toISOString(),
    class_probabilities: data.class_probabilities,
    individual_predictions: data.individual_predictions,
    ensemble_info: data.ensemble_info,
    gradcam: data.gradcam,
    lime: data.lime,
    gradCamUrl: data.gradcam?.image_base64, // For backward compatibility
  };

  return prediction;
};

// Function to store the latest prediction
export const storePrediction = (prediction: any) => {
  latestPrediction = {
    ...prediction,
    reportId: `R${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
  };
  console.log('Storing prediction with LIME:', latestPrediction.lime);
  return latestPrediction;
};

// Function to get the latest prediction
export const getLatestPrediction = () => {
  return latestPrediction;
};

// Function to generate a report
export const generateReport = async (predictionData?: any): Promise<Blob> => {
  const dataToSend = predictionData || latestPrediction;

  if (!dataToSend) {
    throw new Error('No prediction data available for report generation');
  }

  const response = await fetch(`${API_BASE}/api/generate-report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      patientName: 'You',
      includeXAI: true,
      predictionData: dataToSend
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Report generation failed' }));
    throw new Error(error.error || 'Failed to generate report');
  }

  return await response.blob();
};

// Function to send a report by email
export const sendReportByEmail = async (email: string): Promise<boolean> => {
  // TODO: Implement actual email sending endpoint
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));

  // In a real application, this would call an API to send an email
  return true;
};