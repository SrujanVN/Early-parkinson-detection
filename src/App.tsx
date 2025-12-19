import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Context
import { ImageProvider } from './contexts/ImageContext';

// Pages
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import HologramPage from './pages/HologramPage';
import ReportPage from './pages/ReportPage';
import ChatbotPage from './pages/ChatbotPage';

// Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

function App() {
  return (
    <ImageProvider>
      <BrowserRouter>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <main className="flex-grow">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/hologram" element={<HologramPage />} />
                <Route path="/report" element={<ReportPage />} />
                <Route path="/chatbot" element={<ChatbotPage />} />
              </Routes>
            </AnimatePresence>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </ImageProvider>
  );
}

export default App;