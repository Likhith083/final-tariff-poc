import React from 'react';
import { motion } from 'framer-motion';
import { X, Calculator, Search, Package, TrendingUp, Settings, HelpCircle } from 'lucide-react';

const Sidebar = ({ onClose }) => {
  const menuItems = [
    { icon: Calculator, label: 'Tariff Calculator', description: 'Calculate import costs' },
    { icon: Search, label: 'HTS Search', description: 'Find product classifications' },
    { icon: Package, label: 'Material Analysis', description: 'Analyze compositions' },
    { icon: TrendingUp, label: 'Scenario Simulation', description: 'Compare alternatives' },
    { icon: Settings, label: 'Settings', description: 'Configure preferences' },
    { icon: HelpCircle, label: 'Help', description: 'Get assistance' },
  ];

  return (
    <motion.div
      className="sidebar"
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -300, opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="sidebar-header">
        <h2>Navigation</h2>
        <motion.button
          className="close-button"
          onClick={onClose}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <X size={20} />
        </motion.button>
      </div>

      <div className="sidebar-section">
        <h3>Quick Actions</h3>
        {menuItems.map((item, index) => (
          <motion.div
            key={item.label}
            className="sidebar-item"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ x: 5 }}
            whileTap={{ scale: 0.95 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <item.icon size={18} />
              <div>
                <div style={{ fontWeight: 500 }}>{item.label}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>{item.description}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="sidebar-section">
        <h3>Recent Queries</h3>
        <div className="sidebar-item">
          <div style={{ fontSize: '0.9rem' }}>HTS 8471.30.01 tariff calculation</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>2 minutes ago</div>
        </div>
        <div className="sidebar-item">
          <div style={{ fontSize: '0.9rem' }}>Material analysis for gloves</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>5 minutes ago</div>
        </div>
        <div className="sidebar-item">
          <div style={{ fontSize: '0.9rem' }}>Alternative sourcing for China</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>10 minutes ago</div>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>System Status</h3>
        <div style={{ 
          background: 'rgba(0, 255, 0, 0.2)', 
          padding: '0.5rem 1rem', 
          borderRadius: '10px',
          border: '1px solid rgba(0, 255, 0, 0.3)'
        }}>
          <div style={{ fontSize: '0.9rem', color: '#90EE90' }}>🟢 All systems operational</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>Last updated: Just now</div>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar; 