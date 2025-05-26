import React from 'react';
import { Mail } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white py-4 shadow-inner">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <div>
            © 2025  Early Parkinson's Detection. All rights reserved.
          </div>
          <div className="flex items-center mt-2 md:mt-0">
            <Mail size={16} className="mr-2" />
            <a href="mailto:contact@neuroaid.com" className="hover:text-primary transition-colors">
             srujanvn14@gmail.com
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;