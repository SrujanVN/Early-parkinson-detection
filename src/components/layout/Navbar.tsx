import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Brain, Menu, X, LogIn, LogOut, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on navigation
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Analysis', path: '/upload' },
    { name: 'Hologram', path: '/hologram' },
    { name: 'Reports', path: '/report' },
    { name: 'Assistant', path: '/chatbot' },
  ];

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`sticky top-0 z-50 ${
        scrolled 
          ? 'bg-white shadow-md' 
          : 'bg-transparent'
      } transition-all duration-300`}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Early Parkinson's Detection
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`font-medium hover:text-primary transition-colors ${
                  location.pathname === link.path ? 'text-primary' : 'text-text'
                }`}
              >
                {link.name}
              </Link>
            ))}
            
            {/* Auth Buttons */}
            <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-200">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center space-x-2 text-sm text-text/70">
                    <User className="w-4 h-4" />
                    <span className="hidden lg:inline">{user?.email}</span>
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      {user?.role}
                    </span>
                  </div>
                  <button
                    onClick={async () => {
                      await logout();
                      navigate('/');
                    }}
                    className="flex items-center space-x-1 text-text hover:text-primary transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  className="flex items-center space-x-1 text-text hover:text-primary transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Login</span>
                </Link>
              )}
            </div>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-text focus:outline-none"
            aria-label="Toggle menu"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <motion.nav
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden mt-4 py-4 space-y-4"
          >
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`block py-2 font-medium hover:text-primary transition-colors ${
                  location.pathname === link.path ? 'text-primary' : 'text-text'
                }`}
              >
                {link.name}
              </Link>
            ))}
            
            {/* Mobile Auth Section */}
            <div className="pt-4 border-t border-gray-200">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center space-x-2 py-2 text-sm text-text/70">
                    <User className="w-4 h-4" />
                    <span>{user?.email}</span>
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      {user?.role}
                    </span>
                  </div>
                  <button
                    onClick={async () => {
                      await logout();
                      navigate('/');
                      setIsOpen(false);
                    }}
                    className="flex items-center space-x-2 w-full py-2 text-text hover:text-primary transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  onClick={() => setIsOpen(false)}
                  className="flex items-center space-x-2 py-2 text-text hover:text-primary transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Login</span>
                </Link>
              )}
            </div>
          </motion.nav>
        )}
      </div>
    </motion.header>
  );
};

export default Navbar;