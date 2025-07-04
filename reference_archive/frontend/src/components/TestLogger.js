import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import apiService from '../services/apiService';
import logger from '../utils/logger';

const TestLogger = () => {
  const [logs, setLogs] = useState([]);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    logger.componentMount('TestLogger');
    
    // Capture console logs
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalInfo = console.info;

    console.log = (...args) => {
      originalLog(...args);
      addLog('LOG', ...args);
    };

    console.error = (...args) => {
      originalError(...args);
      addLog('ERROR', ...args);
    };

    console.warn = (...args) => {
      originalWarn(...args);
      addLog('WARN', ...args);
    };

    console.info = (...args) => {
      originalInfo(...args);
      addLog('INFO', ...args);
    };

    return () => {
      logger.componentUnmount('TestLogger');
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
      console.info = originalInfo;
    };
  }, []);

  const addLog = (level, ...args) => {
    const timestamp = new Date().toLocaleTimeString();
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');
    
    setLogs(prev => [...prev.slice(-49), { timestamp, level, message }]);
  };

  const testBackendConnection = async () => {
    setIsTesting(true);
    logger.info('TestLogger', 'Testing backend connection');
    
    try {
      const health = await apiService.healthCheck();
      logger.info('TestLogger', 'Backend health check successful', health);
    } catch (error) {
      logger.error('TestLogger', 'Backend health check failed', error);
    } finally {
      setIsTesting(false);
    }
  };

  const testChatAPI = async () => {
    setIsTesting(true);
    logger.info('TestLogger', 'Testing chat API');
    
    try {
      const response = await apiService.sendChatMessage('Hello, this is a test message');
      logger.info('TestLogger', 'Chat API test successful', response);
    } catch (error) {
      logger.error('TestLogger', 'Chat API test failed', error);
    } finally {
      setIsTesting(false);
    }
  };

  const testHTSSearch = async () => {
    setIsTesting(true);
    logger.info('TestLogger', 'Testing HTS search API');
    
    try {
      const response = await apiService.searchHTS('electronics');
      logger.info('TestLogger', 'HTS search test successful', response);
    } catch (error) {
      logger.error('TestLogger', 'HTS search test failed', error);
    } finally {
      setIsTesting(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
    logger.info('TestLogger', 'Logs cleared');
  };

  return (
    <motion.div
      className="test-logger"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="test-controls">
        <h2>🔧 Logger Test Panel</h2>
        <p>Test the logging system and API connections</p>
        
        <div className="test-buttons">
          <button 
            onClick={testBackendConnection}
            disabled={isTesting}
            className="test-button"
          >
            {isTesting ? 'Testing...' : 'Test Backend Connection'}
          </button>
          
          <button 
            onClick={testChatAPI}
            disabled={isTesting}
            className="test-button"
          >
            {isTesting ? 'Testing...' : 'Test Chat API'}
          </button>
          
          <button 
            onClick={testHTSSearch}
            disabled={isTesting}
            className="test-button"
          >
            {isTesting ? 'Testing...' : 'Test HTS Search'}
          </button>
          
          <button 
            onClick={clearLogs}
            className="test-button clear"
          >
            Clear Logs
          </button>
        </div>
      </div>

      <div className="log-display">
        <h3>📋 Live Logs</h3>
        <div className="log-container">
          {logs.length === 0 ? (
            <p className="no-logs">No logs yet. Try testing the APIs above!</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.level.toLowerCase()}`}>
                <span className="log-timestamp">{log.timestamp}</span>
                <span className={`log-level log-level-${log.level.toLowerCase()}`}>
                  {log.level}
                </span>
                <span className="log-message">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default TestLogger; 