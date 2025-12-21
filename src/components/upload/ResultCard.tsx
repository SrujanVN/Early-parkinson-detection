import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, ArrowRight, Download, HelpCircle, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card, { CardHeader, CardBody, CardFooter } from '../ui/Card';
import Button from '../ui/Button';

export interface PredictionResult {
  diagnosis: 'Normal' | 'Parkinson\'s' | 'Unknown';
  confidence: number;
  gradCamUrl?: string;
  spectrogramUrl?: string;
  reportId: string;
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
  // CSV specific fields
  parkinsons_probability?: number;
  normal_probability?: number;
  risk_level?: string;
  feature_importance?: Record<string, number>;
  features_analyzed?: string[];
}

interface ResultCardProps {
  result: PredictionResult | null;
  fileType: string;
  isLoading?: boolean;
  hideFooter?: boolean;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, fileType, isLoading = false, hideFooter = false }) => {
  if (isLoading) {
    return (
      <Card>
        <CardBody className="py-16">
          <div className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4"></div>
            <h3 className="text-xl font-medium text-text/80">
              Analyzing...
            </h3>
            <p className="text-text/60 mt-2">
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
          <div className="w-16 h-16 rounded-full bg-card flex items-center justify-center mb-4 border border-divider">
            <ArrowRight className="h-8 w-8 text-text/40" />
          </div>
          <h3 className="text-xl font-medium text-text/40 mb-2">
            No Analysis Yet
          </h3>
          <p className="text-text/50 max-w-xs">
            Upload a file and submit it for analysis to see results here
          </p>
        </CardBody>
      </Card>
    );
  }

  const isParkinsons = result.diagnosis === 'Parkinson\'s';
  const isUnknown = result.diagnosis === 'Unknown';
  const confidencePercent = (result.confidence * 100).toFixed(1);

  // Extract risk level if available (sent by CSV backend)
  const riskLevel = (result as any).risk_level || (isParkinsons ? 'High' : 'Low');
  const riskColor = riskLevel === 'High' ? 'text-red-500 bg-red-50' :
    riskLevel === 'Low' ? 'text-green-500 bg-green-50' :
      'text-yellow-500 bg-yellow-50';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader
          title="Diagnostic Summary"
          subtitle={`Analysis based on ${fileType} data`}
        />

        <CardBody>
          <div className="flex flex-col items-center mb-6">
            <div className={`relative w-24 h-24 rounded-full flex items-center justify-center mb-4 shadow-sm ${isParkinsons ? 'bg-warning/10 border-2 border-warning/20' : isUnknown ? 'bg-card border border-divider' : 'bg-success/10 border-2 border-success/20'
              }`}>
              {isParkinsons ? (
                <AlertTriangle size={40} className="text-warning" />
              ) : isUnknown ? (
                <HelpCircle size={40} className="text-text/40" />
              ) : (
                <CheckCircle size={40} className="text-success" />
              )}

              {/* Risk Level Badge */}
              {!isUnknown && (
                <div className={`absolute -bottom-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${riskColor}`}>
                  {riskLevel} Risk
                </div>
              )}
            </div>

            <h3 className={`text-2xl font-bold mb-1 ${isParkinsons ? 'text-warning' : isUnknown ? 'text-text/40' : 'text-success'
              }`}>
              {result.diagnosis}
            </h3>

            <div className="w-full max-w-xs bg-divider/20 rounded-full h-2 mb-2 mt-6 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${isParkinsons ? 'bg-warning' : isUnknown ? 'bg-gray-400' : 'bg-success'
                  }`}
                style={{ width: `${confidencePercent}%` }}
              ></div>
            </div>

            <p className="text-sm text-text/60">
              Confidence Score: <span className="font-bold text-text"> {confidencePercent}%</span>
            </p>
          </div>

          {/* Class Probabilities */}
          {result.class_probabilities && (
            <div className="mt-6 border border-divider rounded-xl p-4 bg-primary/5">
              <h4 className="text-sm font-semibold mb-3 text-primary">
                📊 Class Probabilities
              </h4>
              <div className="space-y-2">
                {Object.entries(result.class_probabilities).map(([className, prob]) => (
                  <div key={className} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{className}:</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-divider/20 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${className === 'Parkinsons' ? 'bg-warning' :
                            className === 'Normal' ? 'bg-success' : 'bg-gray-400'
                            }`}
                          style={{ width: `${prob * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-12 text-right">
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ensemble Information */}
          {result.ensemble_info && (
            <div className="mt-6 border border-divider rounded-xl p-4 bg-secondary/5">
              <h4 className="text-sm font-semibold mb-3 text-secondary">
                🎯 Ensemble Model Analysis
              </h4>
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="text-center p-3 bg-card border border-divider rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {result.ensemble_info.num_models}
                  </div>
                  <div className="text-xs text-text/60 mt-1">Models Used</div>
                </div>
                <div className="text-center p-3 bg-card border border-divider rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {(result.ensemble_info.ensemble_confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-text/60 mt-1">Ensemble Confidence</div>
                </div>
              </div>

              {/* Individual Model Predictions */}
              {result.individual_predictions && Object.keys(result.individual_predictions).length > 0 && (
                <div className="mt-3 pt-3 border-t border-divider">
                  <p className="text-xs font-semibold text-text/80 mb-2">Individual Model Predictions:</p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(result.individual_predictions).map(([model, pred]) => {
                      const modelShort = model.replace('MRI_', '');
                      return (
                        <div key={model} className="bg-card border border-divider rounded-lg p-2 text-xs">
                          <div className="font-medium text-text/70">{modelShort}:</div>
                          <div className={`font-bold ${pred.prediction === "Parkinson's" ? 'text-warning' :
                            pred.prediction === 'Normal' ? 'text-success' : 'text-text/50'
                            }`}>
                            {pred.prediction} ({(pred.confidence * 100).toFixed(1)}%)
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* GradCAM Visualization */}
          {(result.gradcam?.image_base64 || result.gradCamUrl || result.spectrogramUrl) && (
            <div className="mt-6 border border-divider rounded-xl p-3">
              <h4 className="text-sm font-semibold mb-2 text-text">
                {result.gradcam?.available ? '🔍 GradCAM Heatmap' :
                  fileType === 'Audio' ? 'Spectrogram Analysis' : 'Visual Analysis'}
              </h4>
              {result.gradcam?.layer_used && (
                <p className="text-xs text-text/40 mb-2">
                  Layer: {result.gradcam.layer_used}
                </p>
              )}
              <div className="aspect-video bg-card border border-divider rounded-lg overflow-hidden">
                <img
                  src={result.gradcam?.image_base64 || result.gradCamUrl || result.spectrogramUrl}
                  alt="GradCAM heatmap visualization"
                  className="w-full h-full object-cover"
                />
              </div>
              {result.gradcam?.available && (
                <p className="text-xs text-text/60 mt-2 text-center">
                  Red/yellow areas indicate regions the AI focused on for prediction
                </p>
              )}
            </div>
          )}

          {/* LIME Visualization */}
          {result.lime?.available && result.lime?.image_base64 && (
            <div className="mt-6 border border-divider rounded-xl p-3">
              <h4 className="text-sm font-semibold mb-2 text-text">
                🎨 LIME Feature Importance
              </h4>
              <div className="aspect-video bg-card border border-divider rounded-lg overflow-hidden">
                <img
                  src={result.lime.image_base64}
                  alt="LIME feature importance visualization"
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-xs text-text/60 mt-2 text-center">
                Green areas support the diagnosis, red areas oppose it
              </p>
            </div>
          )}
        </CardBody>

        {!hideFooter && (
          <CardFooter className="flex flex-col sm:flex-row gap-3">
            {fileType === 'CSV' ? (
              <Link to="/csv-report" state={{ predictionData: result }} className="w-full sm:w-auto">
                <Button fullWidth icon={<Activity size={16} />}>
                  View Clinical Report
                </Button>
              </Link>
            ) : (
              <Link to="/report" className="w-full sm:w-auto">
                <Button fullWidth icon={<Download size={16} />}>
                  Generate Report
                </Button>
              </Link>
            )}
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
};

export default ResultCard;