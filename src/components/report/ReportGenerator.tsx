import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Mail, ClipboardCheck, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';
import Card, { CardBody, CardFooter } from '../ui/Card';
import { getLatestPrediction, generateReport, sendReportByEmail } from '../../utils/api';

const ReportGenerator: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);

  // Get the latest prediction result
  const predictionResult = getLatestPrediction();

  // If no prediction is available, show a message
  if (!predictionResult) {
    return (
      <Card>
        <CardBody className="py-16 text-center">
          <h3 className="text-xl font-semibold mb-4">No Analysis Results Available</h3>
          <p className="text-text/60">
            Please complete an analysis first to generate a report.
          </p>
        </CardBody>
      </Card>
    );
  }

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    try {
      const blob = await generateReport(predictionResult);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `parkinsons_report_${new Date().getTime()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      alert('Report downloaded successfully!');
    } catch (error) {
      alert('Failed to generate report: ' + (error as Error).message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendEmail = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSending(true);
    sendReportByEmail(email).then(() => {
      setIsSending(false);
      setEmailSent(true);
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardBody>
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold">Medical Analysis Report</h2>
            <p className="text-text/40">
              Generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Patient Information</h3>
              <table className="w-full">
                <tbody>
                  <tr>
                    <td className="py-2 text-text/60">Patient Name:</td>
                    <td className="py-2 font-medium">You</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-text/60">Analysis Date:</td>
                    <td className="py-2 font-medium">{new Date().toLocaleDateString()}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Analysis Results</h3>
              <table className="w-full">
                <tbody>
                  <tr>
                    <td className="py-2 text-text/60">Diagnosis:</td>
                    <td className={`py-2 font-medium ${predictionResult.diagnosis === 'Parkinson\'s'
                      ? 'text-warning'
                      : 'text-success'
                      }`}>
                      {predictionResult.diagnosis}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 text-text/60">Confidence:</td>
                    <td className="py-2 font-medium">
                      {(predictionResult.confidence * 100).toFixed(1)}%
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 text-text/60">Recommendation:</td>
                    <td className="py-2 font-medium">
                      {predictionResult.diagnosis === 'Parkinson\'s'
                        ? 'Consult Neurologist'
                        : 'Regular Checkup'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {(predictionResult.gradcam?.available || predictionResult.lime?.available || predictionResult.gradCamUrl || predictionResult.spectrogramUrl) && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Visual Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {predictionResult.gradcam?.available && predictionResult.gradcam?.image_base64 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-text/40">GradCAM Heatmap</p>
                    <div className="rounded-xl overflow-hidden border border-divider aspect-square">
                      <img
                        src={predictionResult.gradcam.image_base64}
                        alt="GradCAM"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                )}
                {predictionResult.lime?.available && predictionResult.lime?.image_base64 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-text/40">LIME Feature Importance</p>
                    <div className="rounded-xl overflow-hidden border border-divider aspect-square">
                      <img
                        src={predictionResult.lime.image_base64}
                        alt="LIME"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                )}
                {!predictionResult.gradcam?.available && !predictionResult.lime?.available && (predictionResult.gradCamUrl || predictionResult.spectrogramUrl) && (
                  <div className="rounded-xl overflow-hidden border border-divider h-64 col-span-2">
                    <img
                      src={predictionResult.gradCamUrl || predictionResult.spectrogramUrl}
                      alt="Analysis visualization"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold mb-4">Analysis Summary</h3>
            <div className="bg-divider/5 p-4 rounded-xl border border-divider">
              <p className="text-text/80 leading-relaxed">
                {predictionResult.diagnosis === "Parkinson's" ? (
                  <div className="space-y-4">
                    <p><b>Diagnosis:</b> The ensemble AI model has detected patterns consistent with Parkinson's disease with {(predictionResult.confidence * 100).toFixed(1)}% confidence.</p>
                    <p><b>Model Analysis:</b> All four state-of-the-art deep learning models (DenseNet121, EfficientNet-B0, EfficientNet-B3, and ResNet50) were employed in this analysis. Each model independently analyzed the MRI scan and contributed to the final ensemble prediction.</p>
                    <p><b>XAI Insights:</b> The GradCAM heatmap visualization highlights the specific brain regions that the AI models focused on. Red and yellow areas indicate regions of high importance. The LIME feature importance map shows features that supported (green) or opposed (red) the diagnosis.</p>
                    <p><b>Recommendations:</b> Consult with a movement disorder specialist or neurologist for comprehensive clinical evaluation. Early intervention may help manage symptoms and slow disease progression.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p><b>Diagnosis:</b> The ensemble AI model indicates normal brain imaging patterns with {(predictionResult.confidence * 100).toFixed(1)}% confidence.</p>
                    <p><b>Model Analysis:</b> No significant patterns associated with Parkinson's disease were detected by the ensemble of deep learning models.</p>
                    <p><b>Clinical Significance:</b> The brain structure appears normal with no visible signs of dopaminergic neuron loss or other Parkinson's-related changes.</p>
                    <p><b>Recommendations:</b> Continue regular health monitoring as part of preventive care. Maintain a healthy lifestyle with regular exercise and balanced diet.</p>
                  </div>
                )}
              </p>
              <div className="flex items-center mt-4 text-sm text-text/40">
                <ClipboardCheck size={16} className="mr-2" />
                Generated by Assistant
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-divider">
            <h3 className="text-lg font-semibold mb-4">Disclaimer</h3>
            <p className="text-sm text-text/40">
              This report is generated by an  system and is intended for informational purposes only.
              It is not a substitute for professional medical advice, diagnosis, or treatment.
              Always seek the advice of a qualified healthcare provider with any questions regarding
              medical conditions.
            </p>
          </div>
        </CardBody>

        <CardFooter className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="primary"
            icon={<Download size={16} />}
            onClick={handleGenerateReport}
            isLoading={isGenerating}
            fullWidth
          >
            Download PDF Report
          </Button>

          {!emailSent ? (
            <form onSubmit={handleSendEmail} className="flex-1 flex flex-col sm:flex-row gap-2">
              <input
                type="email"
                placeholder="Enter email address"
                className="flex-1 rounded-xl px-4 py-2 border border-divider bg-card text-text focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none placeholder:text-text/20"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button
                type="submit"
                variant="outline"
                icon={<Mail size={16} />}
                isLoading={isSending}
              >
                Email Report
              </Button>
            </form>
          ) : (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="flex-1 text-success border border-success/20 bg-success/5 rounded-xl px-4 py-2 flex items-center justify-center"
            >
              <CheckCircle size={16} className="mr-2" />
              Report sent successfully!
            </motion.div>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};

export default ReportGenerator