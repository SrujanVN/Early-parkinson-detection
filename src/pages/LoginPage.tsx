import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { Brain, Mail, Lock, User } from 'lucide-react';

const LoginPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [role, setRole] = useState<'Patient' | 'Researcher'>('Patient');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Frontend validation
    if (!isLogin) {
      // Registration validation
      if (password.length < 6) {
        setError('Password must be at least 6 characters long');
        return;
      }
      
      if (password !== passwordConfirm) {
        setError('Passwords do not match. Please enter the same password in both fields.');
        return;
      }
      
      // Check for weak passwords
      const weakPasswords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'password123'];
      if (weakPasswords.includes(password.toLowerCase())) {
        setError('Password is too weak. Please choose a stronger password.');
        return;
      }
    }

    setLoading(true);

    try {
      if (isLogin) {
        // Login: Verify password matches stored hash
        await login(email, password);
        navigate('/');
      } else {
        // Register: Send password confirmation to backend
        await register(email, password, role, passwordConfirm);
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/10 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full space-y-8 bg-white rounded-2xl shadow-xl p-8"
      >
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-r from-primary to-accent p-3 rounded-full">
              <Brain className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-text">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="mt-2 text-sm text-text/70">
            {isLogin
              ? 'Sign in to access your account'
              : 'Join us to start detecting early signs of Parkinson\'s'}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
            >
              {error}
            </motion.div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-text mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text/40 w-5 h-5" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none relative block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-text mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text/40 w-5 h-5" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError(''); // Clear error when user types
                  }}
                  minLength={6}
                  maxLength={128}
                  className="appearance-none relative block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder={isLogin ? "Enter your password" : "Create a password (min 6 characters)"}
                />
              </div>
              {!isLogin && password.length > 0 && (
                <p className="mt-1 text-xs text-text/60">
                  {password.length < 6 ? 'Password must be at least 6 characters' : '✓ Password length OK'}
                </p>
              )}
            </div>

            {!isLogin && (
              <>
                <div>
                  <label htmlFor="passwordConfirm" className="block text-sm font-medium text-text mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text/40 w-5 h-5" />
                    <input
                      id="passwordConfirm"
                      name="passwordConfirm"
                      type="password"
                      autoComplete="new-password"
                      required
                      value={passwordConfirm}
                      onChange={(e) => {
                        setPasswordConfirm(e.target.value);
                        setError(''); // Clear error when user types
                      }}
                      minLength={6}
                      maxLength={128}
                      className={`appearance-none relative block w-full pl-10 pr-3 py-3 border rounded-lg placeholder-gray-400 text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                        passwordConfirm && password !== passwordConfirm
                          ? 'border-red-300 focus:ring-red-500'
                          : passwordConfirm && password === passwordConfirm
                          ? 'border-green-300 focus:ring-green-500'
                          : 'border-gray-300'
                      }`}
                      placeholder="Re-enter your password"
                    />
                  </div>
                  {passwordConfirm && (
                    <p className={`mt-1 text-xs ${
                      password === passwordConfirm ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {password === passwordConfirm ? '✓ Passwords match' : '✗ Passwords do not match'}
                    </p>
                  )}
                </div>
                <div>
                  <label htmlFor="role" className="block text-sm font-medium text-text mb-2">
                    Role
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text/40 w-5 h-5" />
                    <select
                      id="role"
                      value={role}
                      onChange={(e) => setRole(e.target.value as 'Patient' | 'Researcher')}
                      className="appearance-none relative block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="Patient">Patient</option>
                      <option value="Researcher">Researcher</option>
                    </select>
                  </div>
                </div>
              </>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {isLogin ? 'Signing in...' : 'Creating account...'}
                </span>
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setPassword('');
                setPasswordConfirm('');
              }}
              className="text-sm text-primary hover:text-accent font-medium"
            >
              {isLogin
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </button>
          </div>
          
          {isLogin && (
            <div className="text-center text-xs text-text/60 mt-4">
              <p>🔒 Your password is securely verified against the stored hash</p>
              <p className="mt-1">You must use the exact same password you registered with</p>
            </div>
          )}
        </form>
      </motion.div>
    </div>
  );
};

export default LoginPage;
