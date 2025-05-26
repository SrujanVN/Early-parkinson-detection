// This is a mock API client for the NeuroAid application
// In a real application, this would connect to a backend API

import { ModelPrediction } from './modelService';

// Store the latest prediction result
let latestPrediction: (ModelPrediction & { reportId: string }) | null = null;

export type FileType = 'MRI' | 'Handwriting' | 'Audio' | 'CSV';

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

// Mock function to generate a report
export const generateReport = async (): Promise<Blob> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));
  
  // In a real application, this would call an API to generate a PDF
  return new Blob(['Mock PDF report content'], { type: 'application/pdf' });
};

// Mock function to send a report by email
export const sendReportByEmail = async (email: string): Promise<boolean> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));
  
  // In a real application, this would call an API to send an email
  return true;
};