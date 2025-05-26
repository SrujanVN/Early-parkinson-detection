import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';
import FileUploader from '../components/upload/FileUploader';
import ResultCard, { PredictionResult } from '../components/upload/ResultCard';
import { predictWithModel } from '../utils/modelService';
import { storePrediction } from '../utils/api';

type FileType = 'MRI' | 'Handwriting' | 'Audio' | 'CSV';

const UploadPage: React.FC = () => {
  const [selectedFileType, setSelectedFileType] = useState<FileType>('MRI');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (file: File, type: FileType) => {
    setSelectedFileType(type);
    setIsAnalyzing(true);
    setError(null);

    try {
      const prediction = await predictWithModel(file, type);
      const resultWithId = storePrediction(prediction);
      setResult(resultWithId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze the file. Please try again.';
      setError(errorMessage);
      console.error('Analysis error:', err);
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
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload your medical data for powered analysis to detect potential 
            Parkinson's disease markers with high accuracy.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">File Upload</h2>
              <FileUploader onFileUpload={handleFileUpload} />
              {error && (
                <div className="mt-4 p-4 bg-error/10 text-error rounded-xl">
                  {error}
                </div>
              )}
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
              <ResultCard 
                result={result}
                fileType={selectedFileType}
                isLoading={isAnalyzing}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default UploadPage;