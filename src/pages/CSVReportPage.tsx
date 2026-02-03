import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Download, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

interface PredictionData {
    diagnosis: string;
    confidence: number;
    parkinsons_probability: number;
    normal_probability: number;
    risk_level: string;
    feature_importance: Record<string, number>;
    features_analyzed: string[];
    model_used: string;
}

const CSVReportPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    /*
    # Task Checklist: Integrated CSV Analysis & Chatbot Fix

## Phase 1: CSV Feature Analysis Integration [x]
- [x] Merge "Voice Analysis" into "Start Diagnosis" flow
- [x] Create sectionalized clinical input form for 22 voice features
- [x] Implement clinical sample loading (Normal vs PD)
- [x] Build clinical data visualizations using `recharts`
- [x] Optimize results layout for clinician reading path
- [x] Remove redundant navigation and disclaimers from report page

## Phase 2: Chatbot Connection Recovery [x]
- [x] Diagnose leaked/invalid API key issue
- [x] Securely migrate key to backend `.env` file
- [x] Fix `.env` loading logic for project-root execution
- [x] Standardize Gemini model naming to `models/gemini-2.5-flash`
- [x] Verify chatbot response functionality in browser
     */
    const { predictionData } = location.state || {};

    if (!predictionData) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">No Data Available</h2>
                    <p className="mb-4">Please complete the analysis first</p>
                    <button
                        onClick={() => navigate('/csv-input')}
                        className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                    >
                        Go to Analysis
                    </button>
                </div>
            </div>
        );
    }

    const data: PredictionData = predictionData;

    // Prepare feature importance chart data
    const featureImportanceData = Object.entries(data.feature_importance || {}).map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        importance: (value * 100).toFixed(2),
    }));

    // Prepare probability pie chart data
    const probabilityData = [
        { name: "Parkinson's", value: data.parkinsons_probability * 100, color: '#ef4444' },
        { name: 'Normal', value: data.normal_probability * 100, color: '#10b981' },
    ];

    // Risk level styling
    const getRiskStyle = (risk: string) => {
        switch (risk.toLowerCase()) {
            case 'high':
                return { bg: 'bg-red-500/10', border: 'border-red-500', text: 'text-red-500', icon: AlertTriangle };
            case 'moderate':
                return { bg: 'bg-yellow-500/10', border: 'border-yellow-500', text: 'text-yellow-500', icon: AlertCircle };
            case 'low':
                return { bg: 'bg-green-500/10', border: 'border-green-500', text: 'text-green-500', icon: CheckCircle };
            default:
                return { bg: 'bg-gray-500/10', border: 'border-gray-500', text: 'text-gray-500', icon: AlertCircle };
        }
    };

    const riskStyle = getRiskStyle(data.risk_level);
    const RiskIcon = riskStyle.icon;

    const handleDownloadReport = () => {
        // Create a simple text report
        const reportContent = `
PARKINSON'S DISEASE VOICE FEATURE ANALYSIS REPORT
================================================

DIAGNOSIS: ${data.diagnosis}
CONFIDENCE: ${(data.confidence * 100).toFixed(2)}%
RISK LEVEL: ${data.risk_level}

PROBABILITIES:
- Parkinson's: ${(data.parkinsons_probability * 100).toFixed(2)}%
- Normal: ${(data.normal_probability * 100).toFixed(2)}%

TOP IMPORTANT FEATURES:
${Object.entries(data.feature_importance || {})
                .map(([name, value]) => `- ${name}: ${(value * 100).toFixed(2)}%`)
                .join('\n')}

MODEL USED: ${data.model_used}
ANALYSIS DATE: ${new Date().toLocaleString()}

================================================
This report is for informational purposes only.
Please consult a healthcare professional for medical advice.
`;

        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `parkinsons_voice_analysis_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-background py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">

                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                        <Activity className="w-10 h-10 text-primary" />
                        Voice Feature Analysis Report
                    </h1>
                    <p className="text-lg opacity-80">
                        Clinical voice feature analysis results
                    </p>
                </div>

                {/* Main Results Card */}
                <div className="bg-card border rounded-lg p-8 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Diagnosis */}
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Diagnosis</h3>
                            <p className={`text-3xl font-bold ${data.diagnosis === "Parkinson's" ? 'text-red-500' : 'text-green-500'
                                }`}>
                                {data.diagnosis}
                            </p>
                        </div>

                        {/* Confidence */}
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Confidence</h3>
                            <p className="text-3xl font-bold text-primary">
                                {(data.confidence * 100).toFixed(1)}%
                            </p>
                        </div>

                        {/* Risk Level */}
                        <div className="text-center">
                            <h3 className="text-sm font-medium opacity-60 mb-2">Risk Level</h3>
                            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${riskStyle.bg} ${riskStyle.border} border`}>
                                <RiskIcon className={`w-5 h-5 ${riskStyle.text}`} />
                                <span className={`text-xl font-bold ${riskStyle.text}`}>
                                    {data.risk_level}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    {/* Probability Distribution */}
                    <div className="bg-card border rounded-lg p-6">
                        <h2 className="text-xl font-bold mb-4">Probability Distribution</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={probabilityData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {probabilityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={((value: any) => {
                                    if (value === undefined || value === null) return '0.00%';
                                    return `${Number(value).toFixed(2)}%`;
                                }) as any} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Feature Importance */}
                    <div className="bg-card border rounded-lg p-6">
                        <h2 className="text-xl font-bold mb-4">Top Important Features</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={featureImportanceData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 12 }} />
                                <Tooltip formatter={((value: any) => {
                                    if (value === undefined || value === null) return '0.00%';
                                    return `${Number(value).toFixed(2)}%`;
                                }) as any} />
                                <Bar dataKey="importance" fill="#3b82f6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="bg-card border rounded-lg p-6 mb-6">
                    <h2 className="text-xl font-bold mb-4">Recommendations</h2>
                    <div className="space-y-3">
                        {data.diagnosis === "Parkinson's" ? (
                            <>
                                <div className="flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                                    <p>
                                        <strong>Consult a Neurologist:</strong> The analysis suggests potential indicators of Parkinson's disease.
                                        Please schedule an appointment with a qualified neurologist for comprehensive evaluation.
                                    </p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                                    <p>
                                        <strong>Further Testing:</strong> Additional clinical tests and imaging studies may be recommended
                                        by your healthcare provider for accurate diagnosis.
                                    </p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                                    <p>
                                        <strong>Early Intervention:</strong> If confirmed, early detection allows for better management
                                        and treatment planning.
                                    </p>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                                    <p>
                                        <strong>Normal Results:</strong> The analysis indicates normal voice characteristics.
                                        However, this is not a definitive medical diagnosis.
                                    </p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                                    <p>
                                        <strong>Regular Monitoring:</strong> Continue with regular health check-ups and monitor
                                        for any changes in symptoms.
                                    </p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                                    <p>
                                        <strong>Healthy Lifestyle:</strong> Maintain a healthy lifestyle with regular exercise,
                                        balanced diet, and adequate sleep.
                                    </p>
                                </div>
                            </>
                        )}
                    </div>
                </div>



                {/* Action Buttons */}
                <div className="flex justify-center mt-8">
                    <button
                        onClick={handleDownloadReport}
                        className="px-8 py-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2 font-medium shadow-md"
                    >
                        <Download className="w-5 h-5" />
                        Download Report
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CSVReportPage;
