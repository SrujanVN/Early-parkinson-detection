import { FileType } from './api';

export interface ModelPrediction {
  diagnosis: 'Normal' | 'Parkinson\'s';
  confidence: number;
  gradCamUrl?: string;
  spectrogramUrl?: string;
}

// Internal prediction logic based on file type
export async function predictWithModel(file: File, fileType: FileType): Promise<ModelPrediction> {
  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Generate prediction based on file type
  const predictions: Record<FileType, ModelPrediction> = {
    MRI: {
      diagnosis: Math.random() > 0.5 ? 'Parkinson\'s' : 'Normal',
      confidence: 0.75 + Math.random() * 0.2,
      gradCamUrl: 'https://images.pexels.com/photos/7659564/pexels-photo-7659564.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
    },
    Handwriting: {
      diagnosis: Math.random() > 0.4 ? 'Parkinson\'s' : 'Normal',
      confidence: 0.8 + Math.random() * 0.15,
      gradCamUrl: 'https://images.pexels.com/photos/4226140/pexels-photo-4226140.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
    },
    Audio: {
      diagnosis: Math.random() > 0.3 ? 'Parkinson\'s' : 'Normal',
      confidence: 0.7 + Math.random() * 0.25,
      spectrogramUrl: 'https://images.pexels.com/photos/6969346/pexels-photo-6969346.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
    },
    CSV: {
      diagnosis: Math.random() > 0.45 ? 'Parkinson\'s' : 'Normal',
      confidence: 0.85 + Math.random() * 0.1
    }
  };

  return predictions[fileType];
}