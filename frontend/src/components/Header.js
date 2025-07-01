import React from 'react';
import { motion } from 'framer-motion';
import { Menu } from 'lucide-react';

const Header = ({ onMenuClick }) => {
  return (
    <motion.header
      className="header"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h1
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        🚢 TariffAI
      </motion.h1>
      
      <motion.button
        className="menu-button"
        onClick={onMenuClick}
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