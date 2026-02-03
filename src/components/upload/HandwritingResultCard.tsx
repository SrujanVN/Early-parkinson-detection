import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, HelpCircle, FileText } from 'lucide-react';
import Card, { CardHeader, CardBody, CardFooter } from '../ui/Card';
import Button from '../ui/Button';
import { Link } from 'react-router-dom';

interface HandwritingResultCardProps {
    result: any;
    isLoading?: boolean;
}

const HandwritingResultCard: React.FC<HandwritingResultCardProps> = ({ result, isLoading = false }) => {
    if (isLoading) {
        return (
            <Card>
                <CardBody className="py-16">
                    <div className="flex flex-col items-center justify-center">
                        <div className="w-16 h-16 rounded-full border-4 border-secondary border-t-transparent animate-spin mb-4"></div>
                        <h3 className="text-xl font-medium text-text/80">
                            Analyzing Handwriting...
                        </h3>
                        <p className="text-text/60 mt-2">
                            Processing spiral/wave patterns
                        </p>
                    </div>
                </CardBody>
            </Card>
        );
    }

    if (!result) {
        return null;
    }

    const isParkinsons = result.diagnosis === "Parkinson's";
    const isUnknown = result.diagnosis === "Unknown";
    const confidencePercent = (result.confidence * 100).toFixed(1);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Card>
                <CardHeader
                    title="Handwriting Analysis Result"
                    subtitle="based on HOG, LBP, and MobileNet models"
                />

                <CardBody>
                    <div className="flex flex-col items-center mb-6">
                        <div className={`relative w-24 h-24 rounded-full flex items-center justify-center mb-4 shadow-sm ${isParkinsons ? 'bg-red-50 border-2 border-red-100' :
                            isUnknown ? 'bg-gray-50 border border-gray-200' :
                                'bg-green-50 border-2 border-green-100'
                            }`}>
                            {isParkinsons ? (
                                <AlertTriangle size={40} className="text-red-500" />
                            ) : isUnknown ? (
                                <HelpCircle size={40} className="text-gray-400" />
                            ) : (
                                <CheckCircle size={40} className="text-green-500" />
                            )}
                        </div>

                        <h3 className={`text-2xl font-bold mb-1 ${isParkinsons ? 'text-red-600' : isUnknown ? 'text-gray-600' : 'text-green-600'
                            }`}>
                            {result.diagnosis}
                        </h3>

                        <div className="w-full max-w-xs bg-gray-100 rounded-full h-2 mb-2 mt-6 overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${isParkinsons ? 'bg-red-500' : isUnknown ? 'bg-gray-400' : 'bg-green-500'
                                    }`}
                                style={{ width: `${confidencePercent}%` }}
                            ></div>
                        </div>

                        <p className="text-sm text-text/60">
                            Confidence Score: <span className="font-bold text-text"> {confidencePercent}%</span>
                        </p>
                    </div>

                    {/* Individual Predictions */}
                    {result.individual_predictions && (
                        <div className="mt-6 border-t pt-4">
                            <h4 className="text-sm font-semibold mb-3 text-text/70 uppercase tracking-wider">
                                Individual Model Decisions
                            </h4>
                            <div className="grid grid-cols-1 gap-2">
                                {Object.entries(result.individual_predictions).map(([model, res]: [string, any]) => (
                                    <div key={model} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                                        <span className="font-medium text-sm text-text/80 capitalize">
                                            {model.replace('_', ' ').replace('svm', 'SVM').replace('rf', 'RF').replace('hog', 'HOG').replace('lbp', 'LBP')}
                                        </span>
                                        <div className="flex items-center gap-3">
                                            <span className={`text-sm font-bold ${res.prediction === "Parkinson's" ? 'text-red-500' :
                                                res.prediction === 'Normal' ? 'text-green-500' : 'text-gray-500'
                                                }`}>
                                                {res.prediction}
                                            </span>
                                            <span className="text-xs text-text/40 bg-white px-2 py-0.5 rounded border">
                                                {(res.confidence * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </CardBody>

                <CardFooter>
                    <Link to="/handwriting-report" state={{ predictionData: result }} className="w-full">
                        <Button
                            fullWidth
                            variant="primary"
                            icon={<FileText size={18} />}
                            className="bg-gradient-to-r from-secondary to-primary hover:opacity-90 transition-opacity shadow-md"
                        >
                            View Comprehensive Analysis
                        </Button>
                    </Link>
                </CardFooter>
            </Card>
        </motion.div>
    );
};

export default HandwritingResultCard;
