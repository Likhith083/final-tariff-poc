import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import './ErrorPage.css';

interface ErrorPageProps {
  error?: string;
  onRetry?: () => void;
  isBackendError?: boolean;
}

const ErrorPage: React.FC<ErrorPageProps> = ({ 
  error = "Something went wrong", 
  onRetry,
  isBackendError = false 
}) => {
  return (
    <div className="error-page">
      <motion.div 
        className="error-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div 
          className="error-icon"
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 2, 
            repeat: Infinity,
            repeatType: "reverse"
          }}
        >
          {isBackendError ? <WifiOff size={80} /> : <AlertTriangle size={80} />}
        </motion.div>

        <h1 className="error-title">
          {isBackendError ? "Backend Connection Lost" : "Oops! Something went wrong"}
        </h1>

        <p className="error-message">
          {isBackendError 
            ? "We can't connect to our servers right now. Please check your internet connection and try again."
            : error
          }
        </p>

        {isBackendError && (
          <div className="error-details">
            <div className="detail-item">
              <Wifi size={20} />
              <span>Check your internet connection</span>
            </div>
            <div className="detail-item">
              <RefreshCw size={20} />
              <span>Make sure the backend server is running</span>
            </div>
            <div className="detail-item">
              <AlertTriangle size={20} />
              <span>Try refreshing the page</span>
            </div>
          </div>
        )}

        <div className="error-actions">
          {onRetry && (
            <motion.button
              className="retry-button"
              onClick={onRetry}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw size={20} />
              Try Again
            </motion.button>
          )}
          
          <motion.button
            className="home-button"
            onClick={() => window.location.href = '/'}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Go Home
          </motion.button>
        </div>

        <div className="error-code">
          {isBackendError ? "ERR_CONNECTION_REFUSED" : "ERR_UNKNOWN"}
        </div>
      </motion.div>

      {/* Animated background elements */}
      <div className="error-bg-elements">
        <motion.div 
          className="bg-circle"
          animate={{ 
            x: [0, 100, 0],
            y: [0, -50, 0],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ 
            duration: 8, 
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div 
          className="bg-circle"
          animate={{ 
            x: [0, -80, 0],
            y: [0, 60, 0],
            opacity: [0.2, 0.5, 0.2]
          }}
          transition={{ 
            duration: 10, 
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>
    </div>
  );
};

export default ErrorPage; 