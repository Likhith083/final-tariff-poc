import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import HTSSearch from './components/HTSSearch';
import TariffCalculator from './components/TariffCalculator';
import ScenarioAnalysis from './components/ScenarioAnalysis';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import apiService from './services/apiService';
import logger from './utils/logger';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, chat, hts, tariff, scenario

  useEffect(() => {
    logger.componentMount('App');
    
    const initializeApp = async () => {
      try {
        logger.info('App', 'Initializing application');
        
        // Check backend health
        logger.info('App', 'Checking backend health');
        await checkBackendHealth();
        
        // Simulate loading time for better UX
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        logger.info('App', 'Application initialization complete');
        setIsLoading(false);
      } catch (error) {
        logger.error('App', 'Application initialization failed', error);
        setError(error);
        setIsLoading(false);
      }
    };

    initializeApp();

    return () => {
      logger.componentUnmount('App');
    };
  }, []);

  const checkBackendHealth = async () => {
    try {
      logger.info('App', 'Performing backend health check');
      const health = await apiService.healthCheck();
      logger.info('App', 'Backend health check successful', health);
      setBackendStatus('connected');
    } catch (error) {
      logger.error('App', 'Backend health check failed', error);
      setBackendStatus('disconnected');
      throw new Error('Unable to connect to backend server');
    }
  };

  const handleMenuClick = () => {
    logger.userAction('App', 'menu_button_click');
    setSidebarOpen(true);
  };

  const handleSidebarClose = () => {
    logger.userAction('App', 'sidebar_close');
    setSidebarOpen(false);
  };

  const handleViewChange = (view) => {
    logger.userAction('App', `view_change_to_${view}`);
    setCurrentView(view);
    setSidebarOpen(false);
  };

  if (isLoading) {
    return (
      <motion.div
        className="loading-screen"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="loading-content"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="logo"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            🚢
          </motion.div>
          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            TariffAI
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Intelligent HTS & Tariff Management
          </motion.p>
          
          {/* Backend Status Indicator */}
          <motion.div
            className="backend-status"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <span className={`status-indicator ${backendStatus}`}>
              {backendStatus === 'checking' && '🔍 Checking backend...'}
              {backendStatus === 'connected' && '✅ Backend connected'}
              {backendStatus === 'disconnected' && '❌ Backend disconnected'}
            </span>
          </motion.div>
          
          <motion.div
            className="loading-bar"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 1.5, delay: 0.9 }}
          />
        </motion.div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        className="error-screen"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="error-content">
          <div className="error-icon">⚠️</div>
          <h1>Connection Error</h1>
          <p>{error.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="retry-button"
          >
            Retry Connection
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="app"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Header onMenuClick={handleMenuClick} backendStatus={backendStatus} />
      
      <div className="app-content">
        <AnimatePresence>
          {sidebarOpen && (
            <Sidebar onClose={handleSidebarClose} onViewChange={handleViewChange} currentView={currentView} />
          )}
        </AnimatePresence>
        
        <motion.main
          className="main-content"
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <AnimatePresence mode="wait">
            {currentView === 'dashboard' && (
              <Dashboard key="dashboard" backendStatus={backendStatus} onViewChange={handleViewChange} />
            )}
            {currentView === 'chat' && (
              <ChatInterface key="chat" backendStatus={backendStatus} />
            )}
            {currentView === 'hts' && (
              <HTSSearch key="hts" backendStatus={backendStatus} />
            )}
            {currentView === 'tariff' && (
              <TariffCalculator key="tariff" backendStatus={backendStatus} />
            )}
            {currentView === 'scenario' && (
              <ScenarioAnalysis key="scenario" backendStatus={backendStatus} />
            )}
          </AnimatePresence>
        </motion.main>
      </div>
    </motion.div>
  );
}

export default App; 