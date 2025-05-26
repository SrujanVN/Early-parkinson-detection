import React from 'react';
import { motion } from 'framer-motion';
import { FileText } from 'lucide-react';
import ReportGenerator from '../components/report/ReportGenerator';

const ReportPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="py-12"
    >
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary">
              <FileText size={24} />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Medical Report</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Download or share your comprehensive medical analysis report with detailed insights and recommendations.
          </p>
        </div>

        <ReportGenerator />
      </div>
    </motion.div>
  );
};

export default ReportPage;