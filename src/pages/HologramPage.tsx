import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';
import HologramViewer from '../components/hologram/HologramViewer';
import { useImage } from '../contexts/ImageContext';

const HologramPage: React.FC = () => {
  const { uploadedImage } = useImage();
  
  // Use uploaded image if available, otherwise use placeholder
  const imageUrl = uploadedImage.originalUrl || uploadedImage.previewUrl || 
    'https://images.pexels.com/photos/7659564/pexels-photo-7659564.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2';
  const overlayUrl = uploadedImage.gradcamUrl || 
    (uploadedImage.originalUrl ? null : 'https://images.pexels.com/photos/7659564/pexels-photo-7659564.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2');

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
              <Zap size={24} />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Holographic Visualization</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Explore your medical data in an interactive 3D holographic view for deeper insights.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {uploadedImage.originalUrl || uploadedImage.previewUrl ? (
            <HologramViewer 
              imageUrl={imageUrl}
              overlayUrl={overlayUrl || undefined}
              title="Uploaded Image - Holographic View"
            />
          ) : (
            <div className="bg-white rounded-2xl p-12 text-center shadow-neuro">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                  <Upload className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No Image Uploaded</h3>
                <p className="text-gray-600 mb-6 max-w-md">
                  Upload an image on the Analysis page to view it in holographic 3D visualization
                </p>
                <Link to="/upload">
                  <button className="px-6 py-3 bg-gradient-to-r from-primary to-accent text-white rounded-lg font-medium hover:from-primary/90 hover:to-accent/90 transition-all">
                    Go to Upload Page
                  </button>
                </Link>
              </div>
            </div>
          )}
          
          <div className="mt-12 bg-white rounded-2xl p-6 shadow-neuro">
            <h2 className="text-xl font-semibold mb-4">Understanding the Visualization</h2>
            <p className="text-gray-600 mb-4">
              The holographic view provides an interactive way to examine medical imagery. 
              Here's how to interpret what you're seeing:
            </p>
            <ul className="space-y-3">
              <li className="flex">
                <span className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 flex-shrink-0">1</span>
                <p>
                  <span className="font-medium">Base Image:</span> The original medical scan or image uploaded for analysis.
                </p>
              </li>
              <li className="flex">
                <span className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 flex-shrink-0">2</span>
                <p>
                  <span className="font-medium">Heat Map Overlay:</span> Shows areas of interest identified by our  algorithm, with brighter regions indicating higher relevance to the diagnosis.
                </p>
              </li>
              <li className="flex">
                <span className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 flex-shrink-0">3</span>
                <p>
                  <span className="font-medium">Interactive Controls:</span> Use the buttons to toggle fullscreen mode, auto-rotation, or to show/hide the analysis overlay.
                </p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default HologramPage;