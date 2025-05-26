import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Brain, Layers, AlertCircle } from 'lucide-react';
import Button from '../ui/Button';

const HeroSection: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6 }
    },
  };

  return (
    <motion.section
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="relative pt-16 pb-24 md:pt-24 md:pb-32 overflow-hidden"
    >
      {/* Background elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 left-0 w-72 h-72 bg-primary/5 rounded-full filter blur-3xl"></div>
        <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-accent/5 rounded-full filter blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2">
            <motion.div variants={itemVariants} className="flex items-center mb-4">
              
            </motion.div>

            <motion.h1 
              variants={itemVariants}
              className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6"
            >
             Early Parkinson's Detection <br />
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Predict. Prepare. Prevail.
              </span>
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-lg text-gray-600 mb-8 max-w-lg"
            >
              Analyze scans, assess symptoms, and understand Parkinson's with advanced . Early detection leads to better outcomes.
            </motion.p>

            <motion.div variants={itemVariants} className="flex flex-wrap gap-4">
              <Link to="/upload">
                <Button size="lg" variant="primary">
                  Start Diagnosis
                </Button>
              </Link>
              <Link to="/chatbot">
                <Button size="lg" variant="outline">
                   Assistant
                </Button>
              </Link>
            </motion.div>
          </div>

          <motion.div 
            variants={itemVariants}
            className="lg:w-1/2 mt-12 lg:mt-0 flex justify-center"
          >
            <div className="relative w-80 h-80 md:w-96 md:h-96">
              {/* Hologram effect */}
              <div className="hologram rounded-full">
                <div className="hologram-glow"></div>
                <motion.div
                  animate={{ 
                    rotate: [0, 5, 0, -5, 0],
                    y: [0, -10, 0, -5, 0]
                  }}
                  transition={{ 
                    repeat: Infinity, 
                    duration: 10,
                    ease: "easeInOut" 
                  }}
                  className="relative"
                >
                  <img
                    src="https://wallpapercave.com/wp/wp5193760.jpg"
                    alt="Brain scan visualization"
                    className="w-full h-full object-cover rounded-full opacity-80"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-primary/30 to-transparent rounded-full"></div>
                </motion.div>
              </div>
              
              {/* Floating indicators */}
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1, duration: 0.5 }}
                className="absolute top-10 left-0 glassmorphism rounded-xl p-3 shadow-lg"
              >

                <AlertCircle size={20} className="text-primary" />
                <span className="text-xs font-medium ml-2">Early Detection</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.section>
  );
};

export default HeroSection;