import React from 'react';
import { motion } from 'framer-motion';
import { 
  X, 
  Calculator, 
  Search, 
  BarChart3, 
  MessageSquare, 
  Home,
  TrendingUp, 
  Settings, 
  HelpCircle,
  FileText,
  Globe
} from 'lucide-react';
import logger from '../utils/logger';

const Sidebar = ({ onClose, onViewChange, currentView }) => {
  const menuItems = [
    { 
      id: 'dashboard',
      icon: Home, 
      label: 'Dashboard', 
      description: 'Overview and quick actions',
      color: 'blue'
    },
    { 
      id: 'hts',
      icon: Search, 
      label: 'HTS Search', 
      description: 'Find product classifications',
      color: 'green'
    },
    { 
      id: 'tariff',
      icon: Calculator, 
      label: 'Tariff Calculator', 
      description: 'Calculate import costs',
      color: 'purple'
    },
    { 
      id: 'scenario',
      icon: BarChart3, 
      label: 'Scenario Analysis', 
      description: 'Compare trade scenarios',
      color: 'orange'
    },
    { 
      id: 'chat',
      icon: MessageSquare, 
      label: 'AI Chat', 
      description: 'Ask questions about tariffs',
      color: 'cyan'
    },
  ];

  const handleItemClick = (itemId) => {
    logger.userAction('Sidebar', `navigate_to_${itemId}`);
    onViewChange(itemId);
  };

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
        <h3>Main Menu</h3>
        {menuItems.map((item, index) => (
          <motion.div
            key={item.id}
            className={`sidebar-item ${currentView === item.id ? 'active' : ''}`}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ x: 5 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleItemClick(item.id)}
          >
            <div className="sidebar-item-content">
              <div className={`sidebar-icon ${item.color}`}>
                <item.icon size={18} />
              </div>
              <div className="sidebar-text">
                <div className="sidebar-label">{item.label}</div>
                <div className="sidebar-description">{item.description}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="sidebar-section">
        <h3>Quick Stats</h3>
        <div className="quick-stats">
          <div className="stat-item">
            <FileText size={16} />
            <span>12,500 HTS Codes</span>
          </div>
          <div className="stat-item">
            <Globe size={16} />
            <span>200+ Countries</span>
          </div>
          <div className="stat-item">
            <TrendingUp size={16} />
            <span>Real-time Updates</span>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>Recent Activity</h3>
        <div className="recent-items">
          <div className="recent-item">
            <div className="recent-text">HTS search for "electronics"</div>
            <div className="recent-time">2 min ago</div>
          </div>
          <div className="recent-item">
            <div className="recent-text">Tariff calculation completed</div>
            <div className="recent-time">5 min ago</div>
          </div>
          <div className="recent-item">
            <div className="recent-text">Scenario analysis saved</div>
            <div className="recent-time">12 min ago</div>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>System Status</h3>
        <div className="system-status">
          <div className="status-item">
            <div className="status-dot online"></div>
            <span>Backend API</span>
          </div>
          <div className="status-item">
            <div className="status-dot online"></div>
            <span>Database</span>
          </div>
          <div className="status-item">
            <div className="status-dot online"></div>
            <span>AI Services</span>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="footer-item">
          <Settings size={16} />
          <span>Settings</span>
        </div>
        <div className="footer-item">
          <HelpCircle size={16} />
          <span>Help & Support</span>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar; 