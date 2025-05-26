import React from 'react';
import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';
import ChatInterface from '../components/chatbot/ChatInterface';

const ChatbotPage: React.FC = () => {
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
              <MessageCircle size={24} />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4"> Assistant</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Chat with our specialized assistant to learn more about Parkinson's disease, 
            symptoms, treatments, and to better understand your analysis results.
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          <ChatInterface />
          
          <div className="mt-10 bg-white rounded-2xl p-6 shadow-neuro">
            <h2 className="text-xl font-semibold mb-4">About the  Assistant</h2>
            <p className="text-gray-600 mb-4">
              The  Assistant is trained on medical literature and guidelines related 
              to Parkinson's disease. It can help you understand:
            </p>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start">
                <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">•</span>
                <span>Symptoms and progression of Parkinson's disease</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">•</span>
                <span>Treatment options and lifestyle adjustments</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">•</span>
                <span>Interpretation of your analysis results</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">•</span>
                <span>Latest research and advances in Parkinson's care</span>
              </li>
            </ul>
            <div className="mt-6 text-sm text-gray-500 p-3 bg-yellow-50 rounded-xl border border-yellow-100">
              <strong>Important:</strong> While our assistant provides valuable information, it should not replace professional medical advice. Always consult with a qualified healthcare provider for diagnosis and treatment.
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatbotPage;