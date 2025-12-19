import React from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Sparkles } from 'lucide-react';
import ChatInterface from '../components/chatbot/ChatInterface';

const ChatbotPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="min-h-[calc(100vh-80px)] flex flex-col items-center justify-center py-8 bg-background"
    >
      <div className="container mx-auto px-4 w-full">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-card shadow-lg text-primary border border-divider">
              <MessageCircle size={28} />
            </div>
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold mb-4 text-text tracking-tight">
            Assistant
          </h1>
          <p className="text-lg text-text/60 max-w-2xl mx-auto font-medium">
            Dedicated support for Parkinson's insights and analysis interpretation.
          </p>
        </div>

        <div className="max-w-4xl mx-auto w-full flex flex-col items-center">
          <div className="w-full shadow-2xl rounded-3xl overflow-hidden border border-divider bg-card/40 backdrop-blur-xl">
            <ChatInterface />
          </div>

          <div className="mt-12 w-full grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-card/60 backdrop-blur-md rounded-3xl p-8 shadow-sm border border-divider">
              <h2 className="text-xl font-bold mb-4 text-text flex items-center">
                <Sparkles size={20} className="text-primary mr-2" />
                Specialized Knowledge
              </h2>
              <p className="text-text/60 leading-relaxed text-sm">
                Our Assistant is integrated with the latest medical research on Parkinson's disease,
                offering guidance on symptoms, treatments, and lifestyle adjustments.
              </p>
            </div>

            <div className="bg-card/60 backdrop-blur-md rounded-3xl p-8 shadow-sm border border-divider">
              <h2 className="text-xl font-bold mb-4 text-text flex items-center">
                <MessageCircle size={20} className="text-primary mr-2" />
                Interpreting Results
              </h2>
              <p className="text-text/60 leading-relaxed text-sm">
                Need help understanding your MRI or voice analysis? The Assistant can help
                break down technical metrics into clear, actionable insights.
              </p>
            </div>
          </div>

          <div className="mt-8 text-center text-xs text-text/40 max-w-xl italic">
            <strong>Professional Notice:</strong> Support provided is for informational purposes only.
            Always consult a neurospecialist for clinical diagnosis and medical decisions.
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatbotPage;