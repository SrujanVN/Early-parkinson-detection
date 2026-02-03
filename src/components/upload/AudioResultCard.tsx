import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card, { CardHeader, CardBody, CardFooter } from '../ui/Card';
import Button from '../ui/Button';

interface AudioResultCardProps {
    result: any;
    isLoading?: boolean;
}

const AudioResultCard: React.FC<AudioResultCardProps> = ({ result, isLoading = false }) => {
    if (isLoading) {
        return (
            <Card>
                <CardBody className="py-16">
                    <div className="flex flex-col items-center justify-center">
                        <div className="w-16 h-16 rounded-full border-4 border-secondary border-t-transparent animate-spin mb-4"></div>
                        <h3 className="text-xl font-medium text-text/80">Analyzing Audio...</h3>
                        <p className="text-text/60 mt-2">Processing voice biomarkers</p>
                    </div>
                </CardBody>
            </Card>
        );
    }

    if (!result) return null;

    const isParkinsons = result.diagnosis === "Parkinson's";
    const confidencePercent = (result.confidence * 100).toFixed(1);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Card>
                <CardHeader
                    title="Voice Analysis Result"
                    subtitle="Based on acoustic vocal features"
                />

                <CardBody>
                    <div className="flex flex-col items-center mb-6">
                        <div className={`relative w-24 h-24 rounded-full flex items-center justify-center mb-4 shadow-sm ${isParkinsons ? 'bg-red-50 border-2 border-red-100' : 'bg-green-50 border-2 border-green-100'
                            }`}>
                            {isParkinsons ? (
                                <AlertTriangle size={40} className="text-red-500" />
                            ) : (
                                <CheckCircle size={40} className="text-green-500" />
                            )}
                        </div>

                        <h3 className={`text-2xl font-bold mb-1 ${isParkinsons ? 'text-red-600' : 'text-green-600'}`}>
                            {result.diagnosis}
                        </h3>

                        {result.stability_score !== undefined && (
                            <div className={`mt-2 px-3 py-1 rounded-full text-xs font-semibold ${result.is_stable ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                }`}>
                                Vocal Stability Level: {(result.stability_score * 100).toFixed(0)}%
                            </div>
                        )}

                        <div className="w-full max-w-xs bg-gray-100 rounded-full h-2 mb-2 mt-4 overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${isParkinsons ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${confidencePercent}%` }}
                            ></div>
                        </div>

                        <p className="text-sm text-text/60">
                            Confidence Score: <span className="font-bold text-text"> {confidencePercent}%</span>
                        </p>

                        {/* 4-Model Breakdown Mini Table */}
                        {result.model_metrics && (
                            <div className="mt-6 w-full bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <p className="text-[10px] uppercase font-bold opacity-50 mb-2 tracking-wider">4-Model Ensemble Breakdown</p>
                                <div className="space-y-2">
                                    {result.model_metrics.slice(0, 4).map((model: any, idx: number) => (
                                        <div key={idx} className="flex justify-between items-center text-xs">
                                            <span className="font-medium text-text/70">{model.name}</span>
                                            <div className="flex items-center gap-2">
                                                <span className={`font-bold ${model.diagnosis === "Parkinson's" ? 'text-red-500' : 'text-green-500'}`}>
                                                    {model.diagnosis === "Parkinson's" ? 'PD' : 'Normal'}
                                                </span>
                                                <span className="opacity-40 text-[10px]">{(model.probability * 100).toFixed(0)}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Show spectrogram if available */}
                        {result.spectrogramUrl && (
                            <div className="mt-4 w-full">
                                <p className="text-xs text-center text-text/60 mb-1">Spectrogram Analysis</p>
                                <div className="aspect-video bg-gray-100 rounded overflow-hidden border">
                                    <img src={result.spectrogramUrl} alt="Spectrogram" className="w-full h-full object-cover" />
                                </div>
                            </div>
                        )}
                    </div>
                </CardBody>

                <CardFooter>
                    <Link to="/audio-report" state={{ predictionData: result }} className="w-full">
                        <Button fullWidth variant="outline" icon={<FileText size={16} />}>
                            View Voice Report
                        </Button>
                    </Link>
                </CardFooter>
            </Card>
        </motion.div>
    );
};

export default AudioResultCard;
