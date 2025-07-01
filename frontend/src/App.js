import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

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
          <motion.div
            className="loading-bar"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 1.5, delay: 0.7 }}
          />
        </motion.div>
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
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      <div className="app-content">
        <AnimatePresence>
          {sidebarOpen && (
            <Sidebar onClose={() => setSidebarOpen(false)} />
          )}
        </AnimatePresence>
        
        <motion.main
          className="main-content"
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <ChatInterface />
        </motion.main>
      </div>
    </motion.div>
  );
}

export default App; 