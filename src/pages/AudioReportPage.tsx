import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Mic, Download, AlertCircle } from 'lucide-react';
import Button from '../components/ui/Button';

interface PredictionData {
    diagnosis: string;
    confidence: number;
    parkinsons_probability?: number;
    normal_probability?: number;
    risk_level?: string;
    feature_importance?: Record<string, number>;
    model_used?: string;
    spectrogramUrl?: string;
    stability_score?: number;
    is_stable?: boolean;
    model_metrics?: Array<{
        name: string;
        accuracy: number;
        latency: number;
        status: string;
    }>;
    probabilities?: {
        Parkinsons: number;
        Normal: number;
    };
}

const AudioReportPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { predictionData } = location.state || {};

    if (!predictionData) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">No Audio Analysis Available</h2>
                    <p className="mb-4">Please upload an audio file for analysis first</p>
                    <button
                        onClick={() => navigate('/upload')}
                        className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                    >
                        Go to Upload
                    </button>
                </div>
            </div>
        );
    }

    const data: PredictionData = predictionData;

    // Use probabilities if available, otherwise estimate from confidence
    const parkinsonsProb = data.probabilities?.Parkinsons ?? data.parkinsons_probability ?? (data.diagnosis === "Parkinson's" ? data.confidence : 1 - data.confidence);
    const normalProb = data.probabilities?.Normal ?? data.normal_probability ?? (data.diagnosis === "Normal" ? data.confidence : 1 - data.confidence);

    const probabilityData = [
        { name: "Parkinson's", value: parkinsonsProb * 100, color: '#ef4444' },
        { name: 'Normal', value: normalProb * 100, color: '#10b981' },
    ];

    const riskLevel = data.risk_level || (data.diagnosis === "Parkinson's" ? 'High' : 'Low');
    const riskColor = riskLevel === 'High' ? 'text-red-500' : riskLevel === 'Low' ? 'text-green-500' : 'text-yellow-500';
    const riskBg = riskLevel === 'High' ? 'bg-red-500/10 border-red-500' : riskLevel === 'Low' ? 'bg-green-500/10 border-green-500' : 'bg-yellow-500/10 border-yellow-500';

    const handleDownloadReport = () => {
        const reportContent = `
VOICE BIOMARKER ANALYSIS REPORT
===============================

DIAGNOSIS: ${data.diagnosis.toUpperCase()}
CONFIDENCE: ${(data.confidence * 100).toFixed(2)}%
RISK LEVEL: ${riskLevel}

ANALYSIS DETAILS:
- Parkinson's Probability: ${(parkinsonsProb * 100).toFixed(2)}%
- Normal Probability: ${(normalProb * 100).toFixed(2)}%

METHOD: Voice Feature Analysis (Ensemble/XGBoost)
DATE: ${new Date().toLocaleString()}

===============================
This report is for informational purposes only.
Please consult a healthcare professional.
`;
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voice_analysis_report_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-background py-8 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                        <Mic className="w-10 h-10 text-primary" />
                        Voice Analysis Report
                    </h1>
                    <p className="text-lg opacity-80">
                        Acoustic biomarker analysis results
                    </p>
                </div>

                <div className="bg-card border rounded-lg p-8 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Diagnosis</h3>
                            <p className={`text-3xl font-bold ${data.diagnosis === "Parkinson's" ? 'text-red-500' : 'text-green-500'}`}>
                                {data.diagnosis}
                            </p>
                        </div>
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Confidence</h3>
                            <p className="text-3xl font-bold text-primary">
                                {(data.confidence * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Risk Assessment</h3>
                            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border ${riskBg}`}>
                                <span className={`text-xl font-bold ${riskColor}`}>
                                    {riskLevel} Risk
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Row 1: Stability & Probability Chart */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    {data.stability_score !== undefined && (
                        <div className="bg-card border rounded-lg p-6">
                            <h2 className="text-xl font-bold mb-4">Vocal Stability Assessment</h2>
                            <div className="flex items-center justify-between mb-4 p-4 bg-primary/5 rounded-xl border border-primary/10">
                                <div>
                                    <div className="text-sm opacity-60">Stability Score</div>
                                    <div className="text-3xl font-bold text-primary">{(data.stability_score * 100).toFixed(1)}%</div>
                                </div>
                                <div className={`px-4 py-2 rounded-lg font-bold ${data.is_stable ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                    {data.is_stable ? 'Stable (Normal)' : 'Irregular Patterns'}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="bg-card border rounded-lg p-6">
                        <h2 className="text-xl font-bold mb-4">Probability Distribution</h2>
                        <div className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={probabilityData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {probabilityData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Row 2: Biomarkers */}
                <div className="max-w-2xl mx-auto mb-8">
                    {data.feature_importance && (
                        <div className="bg-card border rounded-lg p-6">
                            <h2 className="text-xl font-bold mb-4">Acoustic Biomarkers</h2>
                            <div className="space-y-4">
                                {[
                                    { label: 'Avg Pitch (Fo)', key: 'MDVP_Fo_Hz', unit: 'Hz' },
                                    { label: 'Jitter (Relative)', key: 'MDVP_Jitter_Percent', unit: '%' },
                                    { label: 'Shimmer (dB)', key: 'MDVP_Shimmer_dB', unit: 'dB' },
                                    { label: 'HNR', key: 'HNR', unit: '' }
                                ].map(feat => (
                                    <div key={feat.key} className="flex justify-between items-center border-b pb-2 last:border-0 border-dashed">
                                        <span className="text-sm font-medium">{feat.label}</span>
                                        <span className="font-mono bg-gray-50 px-2 py-1 rounded text-sm font-bold text-primary">
                                            {data.feature_importance![feat.key]?.toFixed(3)}{feat.unit}
                                        </span>
                                    </div>
                                ))}
                            </div>
                            <p className="text-xs text-text/50 mt-4 italic text-center">Note: These features are extracted using digital signal processing from raw audio samples.</p>
                        </div>
                    )}
                </div>

                {data.model_metrics && (
                    <div className="bg-card border rounded-lg p-6 mb-8">
                        <h2 className="text-xl font-bold mb-4">Model Execution Metrics</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {data.model_metrics.map((model, idx) => (
                                <div key={idx} className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="font-bold text-primary">{model.name}</div>
                                        <div className="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded uppercase">
                                            {model.status}
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 mt-3">
                                        <div>
                                            <div className="text-[10px] uppercase opacity-50 font-bold">Accuracy</div>
                                            <div className="text-lg font-mono font-bold text-gray-800">{model.accuracy}%</div>
                                        </div>
                                        <div>
                                            <div className="text-[10px] uppercase opacity-50 font-bold">Latency</div>
                                            <div className="text-lg font-mono font-bold text-gray-800">{model.latency}s</div>
                                        </div>
                                    </div>
                                    <div className="mt-3 w-full bg-gray-200 rounded-full h-1">
                                        <div
                                            className="bg-primary h-1 rounded-full"
                                            style={{ width: `${model.accuracy}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="flex justify-center">
                    <Button onClick={handleDownloadReport} icon={<Download size={20} />}>
                        Download Full Clinical Report
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default AudioReportPage;
