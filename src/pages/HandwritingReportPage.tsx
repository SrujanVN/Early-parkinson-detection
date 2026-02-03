import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Activity, Download, AlertCircle, CheckCircle, AlertTriangle, FileText } from 'lucide-react';


const HandwritingReportPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { predictionData: result } = location.state || {};

    if (!result) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">No Analysis Data Available</h2>
                    <p className="mb-4">Please upload a handwriting sample first</p>
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

    const isParkinsons = result.diagnosis === "Parkinson's";
    const isUnknown = result.diagnosis === "Unknown";

    const handleDownloadReport = () => {
        if (result.report_pdf_base64) {
            const link = document.createElement('a');
            link.href = `data:application/pdf;base64,${result.report_pdf_base64}`;
            link.download = `Handwriting_Analysis_Report_${new Date().getTime()}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert("PDF Report not available in result data.");
        }
    };

    return (
        <div className="min-h-screen bg-background py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8 border-b pb-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold mb-2 flex items-center gap-3">
                                <FileText className="w-10 h-10 text-secondary" />
                                Handwriting Analysis Report
                            </h1>
                            <p className="text-lg opacity-80">
                                Detailed clinical insights from handwriting pattern analysis
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={handleDownloadReport}
                                className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
                            >
                                <Download className="w-5 h-5" />
                                Download PDF Report
                            </button>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Image & Status */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Diagnosis Card */}
                        <div className="bg-card border rounded-xl p-6 shadow-sm">
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-text/50 mb-4">Diagnostic Result</h3>
                            <div className="flex flex-col items-center text-center">
                                {isParkinsons ? (
                                    <div className="w-20 h-20 rounded-full bg-red-100 flex items-center justify-center mb-4">
                                        <AlertTriangle size={40} className="text-red-500" />
                                    </div>
                                ) : isUnknown ? (
                                    <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                                        <AlertCircle size={40} className="text-gray-500" />
                                    </div>
                                ) : (
                                    <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-4">
                                        <CheckCircle size={40} className="text-green-500" />
                                    </div>
                                )}

                                <h2 className={`text-3xl font-bold mb-2 ${isParkinsons ? 'text-red-600' : isUnknown ? 'text-gray-600' : 'text-green-600'}`}>
                                    {result.diagnosis}
                                </h2>
                                <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary/10 text-primary font-medium text-sm">
                                    {(result.confidence * 100).toFixed(1)}% Confidence
                                </div>
                            </div>
                        </div>
                        {/* Analysis Image */}
                        {result.uploaded_image_url && (
                            <div className="bg-card border rounded-xl p-6 shadow-sm">
                                <h3 className="text-sm font-semibold uppercase tracking-wider text-text/50 mb-4">Analyzed Sample</h3>
                                <div className="aspect-square bg-gray-50 rounded-lg overflow-hidden border">
                                    <img
                                        src={result.uploaded_image_url}
                                        alt="Handwriting sample"
                                        className="w-full h-full object-contain"
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Column: Details & Visuals */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Summary Block */}
                        <div className="bg-card border rounded-xl p-6 shadow-sm">
                            <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-primary" />
                                Clinical Summary
                            </h3>
                            <p className="text-text/80 leading-relaxed">
                                {result.summary || "No summary available."}
                            </p>
                        </div>

                        {/* Model Breakdown */}
                        <div className="bg-card border rounded-xl p-6 shadow-sm">
                            <h3 className="text-lg font-bold mb-4">Model Predictions</h3>
                            <div className="space-y-3">
                                {Object.entries(result.individual_predictions || {}).map(([model, data]: [string, any]) => (
                                    <div key={model} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                                        <div>
                                            <div className="font-semibold text-sm capitalize">{model.replace('_', ' ')}</div>
                                            <div className="text-xs text-text/60">Algorithm</div>
                                        </div>
                                        <div className="text-right">
                                            <div className={`font-bold ${data.prediction === "Parkinson's" ? 'text-red-500' :
                                                data.prediction === 'Normal' ? 'text-green-500' : 'text-gray-500'
                                                }`}>
                                                {data.prediction}
                                            </div>
                                            <div className="text-xs text-text/50">{(data.confidence * 100).toFixed(0)}% Conf.</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Recommendations */}
                    <div className="bg-card border rounded-xl p-6 shadow-sm">
                        <h2 className="text-lg font-bold mb-4">Recommendations</h2>
                        <div className="space-y-3">
                            {isParkinsons ? (
                                <>
                                    <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg border border-red-100">
                                        <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                                        <p className="text-sm">
                                            <strong>Neurological Evaluation:</strong> The handwriting patterns (such as micrographia or tremors) detected suggest potential motor symptoms associated with Parkinson's. A formal neurological assessment is recommended.
                                        </p>
                                    </div>
                                    <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg border border-orange-100">
                                        <Activity className="w-5 h-5 text-orange-500 mt-0.5" />
                                        <p className="text-sm">
                                            <strong>Detailed Motor Testing:</strong> Consider performing standard UPDRS Part III motor examination tasks to correlate with these digital findings.
                                        </p>
                                    </div>
                                </>
                            ) : isUnknown ? (
                                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                                    <AlertTriangle className="w-5 h-5 text-gray-500 mt-0.5" />
                                    <p className="text-sm">
                                        <strong>Inconclusive Result:</strong> The analysis could not definitively classify the sample. Please ensure the image is clear, contains sufficient handwriting (spiral or sentence), and try again or use an alternative modality.
                                    </p>
                                </div>
                            ) : (
                                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-100">
                                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                                    <p className="text-sm">
                                        <strong>Normal Pattern:</strong> No significant Parkinsonian handwriting characteristics detected in this sample.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HandwritingReportPage;
