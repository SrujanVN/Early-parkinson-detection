import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, Activity, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card, { CardHeader, CardBody, CardFooter } from '../ui/Card';
import Button from '../ui/Button';

interface CSVResultCardProps {
    result: any;
    isLoading?: boolean;
}

const CSVResultCard: React.FC<CSVResultCardProps> = ({ result, isLoading = false }) => {
    if (isLoading) {
        return (
            <Card>
                <CardBody className="py-16">
                    <div className="flex flex-col items-center justify-center">
                        <div className="w-16 h-16 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4"></div>
                        <h3 className="text-xl font-medium text-text/80">Analyzing Clinical Data...</h3>
                    </div>
                </CardBody>
            </Card>
        );
    }

    if (!result) return null;

    const isParkinsons = result.diagnosis === "Parkinson's";
    const confidencePercent = (result.confidence * 100).toFixed(1);
    const riskLevel = result.risk_level || (isParkinsons ? 'High' : 'Low');

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
                    title="Clinical Analysis Result"
                    subtitle="Based on voice features (CSV)"
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

                            <div className={`absolute -bottom-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${riskColor}`}>
                                {riskLevel} Risk
                            </div>
                        </div>

                        <h3 className={`text-2xl font-bold mb-1 ${isParkinsons ? 'text-red-600' : 'text-green-600'}`}>
                            {result.diagnosis}
                        </h3>

                        <div className="w-full max-w-xs bg-gray-100 rounded-full h-2 mb-2 mt-6 overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${isParkinsons ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${confidencePercent}%` }}
                            ></div>
                        </div>

                        <p className="text-sm text-text/60">
                            Confidence Score: <span className="font-bold text-text"> {confidencePercent}%</span>
                        </p>
                    </div>
                </CardBody>

                <CardFooter>
                    <Link to="/csv-report" state={{ predictionData: result }} className="w-full">
                        <Button fullWidth variant="outline" icon={<Activity size={16} />}>
                            View Clinical Report
                        </Button>
                    </Link>
                </CardFooter>
            </Card>
        </motion.div>
    );
};

export default CSVResultCard;
