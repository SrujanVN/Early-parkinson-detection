import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, Activity, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import FileUploader from '../components/upload/FileUploader';
import ResultCard, { PredictionResult } from '../components/upload/ResultCard'; // MRI Only
import HandwritingResultCard from '../components/upload/HandwritingResultCard';
import CSVResultCard from '../components/upload/CSVResultCard';
import AudioResultCard from '../components/upload/AudioResultCard';
import CSVResultVisuals from '../components/upload/CSVResultVisuals';
import Button from '../components/ui/Button';
import { uploadFileForPrediction, uploadXrayForEnsemblePrediction, storePrediction, predictCSVFeatures, FileType } from '../utils/api';
import { useImage } from '../contexts/ImageContext';


const UploadPage: React.FC = () => {
  const [selectedFileType, setSelectedFileType] = useState<FileType>('MRI');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setUploadedImage, uploadedImage } = useImage();

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      if (uploadedImage.previewUrl && uploadedImage.previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(uploadedImage.previewUrl);
      }
    };
  }, [uploadedImage.previewUrl]);

  // Convert file to base64 for storage
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };

  const handleFileUpload = async (file: File, type: FileType) => {
    setSelectedFileType(type);
    setIsAnalyzing(true);
    setError(null);

    try {
      // Store the uploaded image for hologram view
      const previewUrl = URL.createObjectURL(file);
      let originalUrl: string | null = null;

      // Convert image and audio files to base64 for storage/persistence
      if (file.type.startsWith('image/') || file.type.startsWith('audio/')) {
        try {
          originalUrl = await fileToBase64(file);
        } catch (e) {
          console.error('Error converting file to base64:', e);
          originalUrl = previewUrl; // Fallback to blob URL
        }
      } else {
        originalUrl = previewUrl;
      }

      let prediction;
      let gradcamUrl: string | null = null;

      // Use ensemble endpoint for X-ray/CT images (MRI type)
      if (type === 'MRI') {
        try {
          // Try ensemble endpoint first for X-ray images
          prediction = await uploadXrayForEnsemblePrediction(file);
          // Store GradCAM image if available
          if (prediction.gradcam?.image_base64) {
            gradcamUrl = prediction.gradcam.image_base64;
          }
        } catch (ensembleError) {
          // Fallback to regular endpoint if ensemble fails
          console.log('Ensemble prediction failed, using regular endpoint:', ensembleError);
          prediction = await uploadFileForPrediction(file, type);
        }
      } else {
        // Use regular endpoint for other file types
        prediction = await uploadFileForPrediction(file, type);
        if (prediction.gradCamUrl) {
          gradcamUrl = prediction.gradCamUrl;
        }
      }


      setUploadedImage({
        file: file,
        previewUrl: previewUrl,
        originalUrl: originalUrl, // Store as base64 for persistence
        gradcamUrl: gradcamUrl,
      });

      // Cleanup: Don't revoke previewUrl immediately as it might be needed
      // It will be cleaned up when component unmounts or new image is uploaded

      // Store prediction with all data including GradCAM and LIME
      console.log('API Response data:', prediction);
      const resultWithId = storePrediction(prediction);
      console.log('Stored prediction object:', resultWithId);
      setResult(resultWithId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze the file. Please try again.';
      setError(`Analysis Error: ${errorMessage}`);
      console.error('Detailed Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCSVFeatureSubmit = async (features: Record<string, number>) => {
    setSelectedFileType('CSV');
    setIsAnalyzing(true);
    setError(null);

    try {
      const prediction = await predictCSVFeatures(features);
      console.log('CSV Prediction results:', prediction);

      const resultWithId = storePrediction(prediction);
      setResult(resultWithId);

      // Clear uploaded image for CSV as it's feature-based
      setUploadedImage({
        file: null,
        previewUrl: null,
        originalUrl: null,
        gradcamUrl: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze features.';
      setError(`Analysis Error: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="py-12"
    >
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary">
              <Brain size={24} />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Upload & Analyze</h1>
          <p className="text-text/60 max-w-2xl mx-auto">
            Upload your medical data or enter clinical features for powered analysis to detect potential
            Parkinson's disease markers with high accuracy.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Clinical Data Input</h2>
              <FileUploader
                onFileUpload={handleFileUpload}
                onCSVFeatureSubmit={handleCSVFeatureSubmit}
                isLoading={isAnalyzing}
              />
              {error && (
                <div className="mt-4 p-4 bg-error/10 text-error rounded-xl">
                  {error}
                </div>
              )}
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>


              {selectedFileType === 'Handwriting' ? (
                <HandwritingResultCard
                  result={result}
                  isLoading={isAnalyzing}
                />
              ) : selectedFileType === 'CSV' ? (
                <CSVResultCard
                  result={result}
                  isLoading={isAnalyzing}
                />
              ) : selectedFileType === 'Audio' ? (
                <AudioResultCard
                  result={result}
                  isLoading={isAnalyzing}
                />
              ) : (
                /* MRI (Default) */
                <ResultCard
                  result={result}
                  fileType={selectedFileType}
                  isLoading={isAnalyzing}
                />
              )}

              {/* Inline Visuals & Details for CSV Analysis */}
              {!isAnalyzing && result && selectedFileType === 'CSV' && (
                <div className="mt-8 space-y-8 animate-in fade-in duration-700">
                  <div>
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <Activity size={20} className="text-primary" />
                      Visual Clinical Insights
                    </h3>
                    <CSVResultVisuals predictionData={result} />
                  </div>

                </div>
              )}

              {/* Inline Visuals & Details for Handwriting Analysis */}
              {!isAnalyzing && result && selectedFileType === 'Handwriting' && (
                <div className="mt-8 space-y-8 animate-in fade-in duration-700">
                  {/* Dedicated card handles navigation now */}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div >
  );
};

export default UploadPage;