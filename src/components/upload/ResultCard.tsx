import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, ArrowRight, Download, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card, { CardHeader, CardBody, CardFooter } from '../ui/Card';
import Button from '../ui/Button';

export interface PredictionResult {
  diagnosis: 'Normal' | 'Parkinson\'s';
  confidence: number;
  gradCamUrl?: string;
  spectrogramUrl?: string;
  reportId: string;
  ensembleInfo?: {
    num_models: number;
    consensus_probability: number;
    ensemble_confidence: number;
    std_dev: number;
    individual_predictions: Record<string, number>;
  };
  gradcam?: {
    available: boolean;
    image_base64?: string;
    layer_used?: string;
  };
}

interface ResultCardProps {
  result: PredictionResult | null;
  fileType: string;
  isLoading?: boolean;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, fileType, isLoading = false }) => {
  if (isLoading) {
    return (
      <Card>
        <CardBody className="py-16">
          <div className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4"></div>
            <h3 className="text-xl font-medium text-gray-600">
              Analyzing...
            </h3>
            <p className="text-gray-500 mt-2">
              This may take a few moments
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card>
        <CardBody className="py-16 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
            <ArrowRight className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-medium text-gray-400 mb-2">
            No Analysis Yet
          </h3>
          <p className="text-gray-500 max-w-xs">
            Upload a file and submit it for analysis to see results here
          </p>
        </CardBody>
      </Card>
    );
  }

  const isParkinsons = result.diagnosis === 'Parkinson\'s';
  const confidencePercent = (result.confidence * 100).toFixed(1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader
          title="Analysis Results"
          subtitle={`Based on ${fileType} analysis`}
        />

        <CardBody>
          <div className="flex flex-col items-center mb-6">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${
              isParkinsons ? 'bg-warning/10' : 'bg-success/10'
            }`}>
              {isParkinsons ? (
                <AlertTriangle size={36} className="text-warning" />
              ) : (
                <CheckCircle size={36} className="text-success" />
              )}
            </div>
            
            <h3 className={`text-2xl font-bold mb-1 ${
              isParkinsons ? 'text-warning' : 'text-success'
            }`}>
              {result.diagnosis}
            </h3>
            
            <div className="w-full max-w-xs bg-gray-100 rounded-full h-2.5 mb-2 mt-4">
              <div 
                className={`h-2.5 rounded-full ${
                  isParkinsons ? 'bg-warning' : 'bg-success'
                }`}
                style={{ width: `${confidencePercent}%` }}
              ></div>
            </div>
            
            <p className="text-sm text-gray-600">
              Confidence: <span className="font-medium">{confidencePercent}%</span>
            </p>
          </div>

          {/* Ensemble Information */}
          {result.ensembleInfo && (
            <div className="mt-6 border rounded-xl p-4 bg-blue-50">
              <h4 className="text-sm font-semibold mb-3 text-blue-900">
                🎯 Ensemble Prediction
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Models Used:</span>
                  <span className="font-medium">{result.ensembleInfo.num_models} models</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Ensemble Confidence:</span>
                  <span className="font-medium">
                    {(result.ensembleInfo.ensemble_confidence * 100).toFixed(1)}%
                  </span>
                </div>
                {Object.keys(result.ensembleInfo.individual_predictions).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-blue-200">
                    <p className="text-xs text-gray-600 mb-2">Individual Model Predictions:</p>
                    <div className="space-y-1">
                      {Object.entries(result.ensembleInfo.individual_predictions).map(([model, prob]) => (
                        <div key={model} className="flex justify-between text-xs">
                          <span className="text-gray-600">{model}:</span>
                          <span className="font-medium">{(prob * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* GradCAM Visualization */}
          {(result.gradcam?.image_base64 || result.gradCamUrl || result.spectrogramUrl) && (
            <div className="mt-6 border rounded-xl p-3">
              <h4 className="text-sm font-medium mb-2">
                {result.gradcam?.available ? '🔍 GradCAM Heatmap' : 
                 fileType === 'Audio' ? 'Spectrogram Analysis' : 'Visual Analysis'}
              </h4>
              {result.gradcam?.layer_used && (
                <p className="text-xs text-gray-500 mb-2">
                  Layer: {result.gradcam.layer_used}
                </p>
              )}
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img 
                  src={result.gradcam?.image_base64 || result.gradCamUrl || result.spectrogramUrl} 
                  alt="GradCAM heatmap visualization"
                  className="w-full h-full object-cover"
                />
              </div>
              {result.gradcam?.available && (
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Red/yellow areas indicate regions the AI focused on for prediction
                </p>
              )}
            </div>
          )}
        </CardBody>

        <CardFooter className="flex flex-col sm:flex-row gap-3">
          <Link to="/hologram" className="w-full sm:w-auto">
            <Button fullWidth variant="outline" icon={<ArrowRight size={16} />}>
              View Hologram
            </Button>
          </Link>
          <Link to="/report" className="w-full sm:w-auto">
            <Button fullWidth icon={<Download size={16} />}>
              Generate Report
            </Button>
          </Link>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default ResultCard;