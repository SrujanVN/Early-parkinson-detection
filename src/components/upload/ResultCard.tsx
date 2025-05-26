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

          {/* Visualization */}
          {(result.gradCamUrl || result.spectrogramUrl) && (
            <div className="mt-6 border rounded-xl p-3">
              <h4 className="text-sm font-medium mb-2">
                {fileType === 'Audio' ? 'Spectrogram Analysis' : 'Visual Analysis'}
              </h4>
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img 
                  src={result.gradCamUrl || result.spectrogramUrl} 
                  alt="Analysis visualization"
                  className="w-full h-full object-cover"
                />
              </div>
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