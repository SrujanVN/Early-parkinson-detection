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
          <p className="text-gray-600">
            Please complete an analysis first to generate a report.
          </p>
        </CardBody>
      </Card>
    );
  }

  const handleGenerateReport = () => {
    setIsGenerating(true);
    generateReport().then(() => {
      setIsGenerating(false);
      alert('Report downloaded successfully!');
    });
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
            <p className="text-gray-500">
              Generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Patient Information</h3>
              <table className="w-full">
                <tbody>
                  <tr>
                    <td className="py-2 text-gray-600">Patient ID:</td>
                    <td className="py-2 font-medium">{predictionResult.reportId}</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Analysis Date:</td>
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
                    <td className="py-2 text-gray-600">Diagnosis:</td>
                    <td className={`py-2 font-medium ${
                      predictionResult.diagnosis === 'Parkinson\'s' 
                        ? 'text-warning' 
                        : 'text-success'
                    }`}>
                      {predictionResult.diagnosis}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Confidence:</td>
                    <td className="py-2 font-medium">
                      {(predictionResult.confidence * 100).toFixed(1)}%
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Recommendation:</td>
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

          {(predictionResult.gradCamUrl || predictionResult.spectrogramUrl) && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Visual Analysis</h3>
              <div className="rounded-xl overflow-hidden border border-gray-200">
                <img 
                  src={predictionResult.gradCamUrl || predictionResult.spectrogramUrl} 
                  alt="Analysis visualization" 
                  className="w-full h-64 object-cover"
                />
              </div>
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold mb-4">Analysis Summary</h3>
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
              <p className="text-gray-700 leading-relaxed">
                {predictionResult.diagnosis === 'Parkinson\'s'
                  ? "The analysis indicates patterns consistent with early-stage Parkinson's disease. The observed characteristics match known markers for neurodegeneration affecting dopamine-producing neurons. Early intervention and consultation with a neurologist is recommended."
                  : "The analysis shows patterns within normal ranges. No significant indicators of Parkinson's disease were detected. Continue with regular health check-ups as recommended by your healthcare provider."}
              </p>
              <div className="flex items-center mt-4 text-sm text-gray-500">
                <ClipboardCheck size={16} className="mr-2" />
                Generated by Assistant
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Disclaimer</h3>
            <p className="text-sm text-gray-500">
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
                className="flex-1 rounded-xl px-4 py-2 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
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