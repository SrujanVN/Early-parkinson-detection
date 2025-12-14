// API client for the NeuroAid application
// Connects to the Flask backend API

import { ModelPrediction } from './modelService';

const API_BASE = 'http://127.0.0.1:5000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Store the latest prediction result
let latestPrediction: (ModelPrediction & { reportId: string }) | null = null;

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

  const endpoint = USE_MOCK ? `${API_BASE}/api/mock/predict` : `${API_BASE}/predict`;
  const response = await fetch(endpoint, {
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

  const endpoint = USE_MOCK ? `${API_BASE}/api/mock/predict/xray` : `${API_BASE}/api/predict/xray`;
  const response = await fetch(endpoint, {
    method: 'POST',
    credentials: 'include',
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
    ensembleInfo: data.ensemble_info,
    gradcam: data.gradcam,
    gradCamUrl: data.gradcam?.image_base64, // For backward compatibility
  };

  return prediction;
};

// Function to store the latest prediction
export const storePrediction = (prediction: ModelPrediction) => {
  latestPrediction = {
    ...prediction,
    reportId: `R${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
  };
  return latestPrediction;
};

// Function to get the latest prediction
export const getLatestPrediction = () => {
  return latestPrediction;
};

// Function to generate a report
export const generateReport = async (): Promise<Blob> => {
  // TODO: Implement actual PDF generation endpoint
  // For now, simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));
  
  // In a real application, this would call an API to generate a PDF
  return new Blob(['Mock PDF report content'], { type: 'application/pdf' });
};

// Function to send a report by email
export const sendReportByEmail = async (email: string): Promise<boolean> => {
  // TODO: Implement actual email sending endpoint
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));
  
  // In a real application, this would call an API to send an email
  return true;
};