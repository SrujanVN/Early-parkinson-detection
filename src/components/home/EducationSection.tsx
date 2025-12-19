import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Microscope, Clock } from 'lucide-react';
import Card, { CardBody } from '../ui/Card';

const educationCards = [
  {
    icon: <Brain size={24} />,
    title: "What is Parkinson's?",
    description: "Parkinson's is a neurodegenerative disorder affecting movement. It occurs when neurons in the brain gradually break down or die, causing tremors, stiffness, and difficulty with balance.",
    color: "bg-primary/10 text-primary"
  },
  {
    icon: <Microscope size={24} />,
    title: "Enhanced Clinical Support",
    description: "assists neurologists with decision-making by offering evidence-based insights drawn from large datasets of Parkinson’s cases..",
    color: "bg-secondary/10 text-secondary"
  },
  {
    icon: <Clock size={24} />,
    title: "Why Early Detection Matters",
    description: "Early detection of Parkinson's can significantly improve quality of life, slow progression, and allow for more effective symptom management before significant neurological damage occurs.",
    color: "bg-accent/10 text-accent"
  }
];

const EducationSection: React.FC = () => {
  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Understanding Parkinson's Disease</h2>
          <p className="text-text/60 max-w-2xl mx-auto">
            Knowledge is power. Learn about Parkinson's disease, its symptoms, and how early
            detection can make a significant difference.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {educationCards.map((card, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardBody>
                  <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 ${card.color}`}>
                    {card.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{card.title}</h3>
                  <p className="text-text/60">{card.description}</p>
                </CardBody>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default EducationSection;