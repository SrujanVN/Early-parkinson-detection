import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Zap, FileText } from 'lucide-react';
import Card, { CardBody } from '../ui/Card';

const steps = [
  {
    icon: <Upload size={24} />,
    title: "Upload Files",
    description: "Upload MRI scans, handwriting samples, audio recordings, or CSV data for analysis.",
    color: "bg-primary/10 text-primary"
  },
  {
    icon: <Zap size={24} />,
    title: "Analysis",
    description: "Our advanced approach analyzes your data to detect potential Parkinson's markers.",
    color: "bg-secondary/10 text-secondary"
  },
  {
    icon: <FileText size={24} />,
    title: "Get Report",
    description: "Receive a comprehensive report with visualizations and personalized insights.",
    color: "bg-accent/10 text-accent"
  }
];

const StepsSection: React.FC = () => {
  return (
    <section className="py-20 bg-card/50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">How Early Parkinson's Detection  Works</h2>
          <p className="text-text/60 max-w-2xl mx-auto">
            Our platform uses state-of-the-art Of Early Parkinson's Detection  to analyze clinical data for early detection
            of Parkinson's symptoms, providing accessible insights.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <Card isHoverable className="h-full">
                <CardBody>
                  <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 ${step.color}`}>
                    {step.icon}
                  </div>
                  <div className="relative">
                    <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                    <p className="text-text/60">{step.description}</p>
                  </div>
                </CardBody>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Connection line */}
        <div className="hidden md:block relative h-0">
          <div className="absolute top-[-120px] left-1/6 right-1/6 h-0.5 bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
        </div>
      </div>
    </section>
  );
};

export default StepsSection;