import React from 'react';
import { motion } from 'framer-motion';
import HeroSection from '../components/home/HeroSection';
import StepsSection from '../components/home/StepsSection';
import EducationSection from '../components/home/EducationSection';

const HomePage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <HeroSection />
      <StepsSection />
      <EducationSection />
    </motion.div>
  );
};

export default HomePage;