import React from 'react';
import { motion } from 'framer-motion';
import { Menu, Wifi, WifiOff, Loader } from 'lucide-react';
import logger from '../utils/logger';

const Header = ({ onMenuClick, backendStatus = 'checking' }) => {
  const getStatusIcon = () => {
    switch (backendStatus) {
      case 'connected':
        return <Wifi size={16} />;
      case 'disconnected':
        return <WifiOff size={16} />;
      case 'checking':
      default:
        return <Loader size={16} className="spinning" />;
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'checking':
      default:
        return 'Checking...';
    }
  };

  const handleMenuClick = () => {
    logger.userAction('Header', 'menu_button_click');
    onMenuClick();
  };

  return (
    <motion.header
      className="header"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-left">
        <motion.h1
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          🚢 TariffAI
        </motion.h1>
        
        {/* Backend Status Indicator */}
        <motion.div
          className={`status-badge ${backendStatus}`}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {getStatusIcon()}
          <span>{getStatusText()}</span>
        </motion.div>
      </div>
      
      <motion.button
        className="menu-button"
        onClick={handleMenuClick}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        initial={{ x: 20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <Menu size={20} />
      </motion.button>
    </motion.header>
  );
};

export default Header; 