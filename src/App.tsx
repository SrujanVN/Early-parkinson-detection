import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Context
import { AuthProvider } from './contexts/AuthContext';
import { ImageProvider } from './contexts/ImageContext';

// Pages
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import HologramPage from './pages/HologramPage';
import ReportPage from './pages/ReportPage';
import ChatbotPage from './pages/ChatbotPage';
import LoginPage from './pages/LoginPage';

// Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <ImageProvider>
        <BrowserRouter>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <main className="flex-grow">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/upload"
                  element={
                    <ProtectedRoute>
                      <UploadPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/hologram"
                  element={
                    <ProtectedRoute>
                      <HologramPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/report"
                  element={
                    <ProtectedRoute>
                      <ReportPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/chatbot"
                  element={
                    <ProtectedRoute>
                      <ChatbotPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </AnimatePresence>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
      </ImageProvider>
    </AuthProvider>
  );
}

export default App;