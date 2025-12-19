import { FileType } from './api';

export interface ModelPrediction {
  diagnosis: 'Normal' | 'Parkinson\'s' | 'Unknown';
  confidence: number;
  gradCamUrl?: string;
  spectrogramUrl?: string;
  timestamp?: string;
}

export interface EnsemblePrediction extends ModelPrediction {
  class_probabilities?: {
    Normal: number;
    Parkinsons: number;
    Unknown: number;
  };
  individual_predictions?: Record<string, {
    prediction: string;
    confidence: number;
    probabilities: {
      Normal: number;
      Parkinsons: number;
      Unknown: number;
    };
  }>;
  ensemble_info?: {
    models_used: string[];
    num_models: number;
    ensemble_confidence: number;
    threshold_applied: number;
  };
  gradcam?: {
    available: boolean;
    image_base64?: string;
    layer_used?: string;
  };
  lime?: {
    available: boolean;
    image_base64?: string;
  };
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