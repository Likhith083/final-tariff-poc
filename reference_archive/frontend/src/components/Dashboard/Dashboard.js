import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  Calculator, 
  Package, 
  TrendingUp, 
  MessageCircle, 
  FileText, 
  Database,
  TrendingDown,
  DollarSign,
  Activity,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Globe,
  BookOpen,
  Database as DatabaseIcon,
  BarChart3
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalCalculations: 0,
    totalSavings: 0,
    activeSessions: 0,
    systemHealth: 'healthy'
  });

  useEffect(() => {
    // Fetch dashboard statistics
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      // In a real app, you'd fetch this from your API
      setStats({
        totalCalculations: 1247,
        totalSavings: 45678.90,
        activeSessions: 3,
        systemHealth: 'healthy'
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const quickActions = [
    {
      icon: Search,
      title: 'HTS Search',
      description: 'Find product classifications',
      path: '/hts-search',
      color: '#3B82F6'
    },
    {
      icon: Calculator,
      title: 'Tariff Calculator',
      description: 'Calculate import costs',
      path: '/tariff-calculator',
      color: '#10B981'
    },
    {
      icon: Package,
      title: 'Material Analysis',
      description: 'Analyze compositions',
      path: '/material-analysis',
      color: '#F59E0B'
    },
    {
      icon: TrendingUp,
      title: 'Scenario Analysis',
      description: 'Compare alternatives',
      path: '/scenario-analysis',
      color: '#8B5CF6'
    },
    {
      icon: MessageCircle,
      title: 'AI Chat',
      description: 'Get intelligent assistance',
      path: '/chat',
      color: '#EC4899'
    },
    {
      icon: FileText,
      title: 'Reports',
      description: 'Generate and view reports',
      path: '/reports',
      color: '#6B7280'
    }
  ];

  const recentActivity = [
    {
      type: 'calculation',
      title: 'HTS 8471.30.01 tariff calculation',
      description: 'Calculated tariff for laptop computers',
      time: '2 minutes ago',
      amount: '$125.00'
    },
    {
      type: 'analysis',
      title: 'Material analysis for nitrile gloves',
      description: 'Found 15% cost savings opportunity',
      time: '5 minutes ago',
      amount: '$45.00'
    },
    {
      type: 'scenario',
      title: 'Alternative sourcing for China',
      description: 'Mexico scenario shows 20% savings',
      time: '10 minutes ago',
      amount: '$2,340.00'
    }
  ];

  const handleQuickAction = (path) => {
    navigate(path);
  };

  const quickLinks = [
    {
      icon: Globe,
      title: 'USITC HTS',
      description: 'Official US Harmonized Tariff Schedule',
      url: 'https://hts.usitc.gov/',
      color: '#3B82F6'
    },
    {
      icon: BookOpen,
      title: 'WTO Tariff Analysis',
      description: 'World Trade Organization tariff data',
      url: 'https://tariffdata.wto.org/',
      color: '#10B981'
    },
    {
      icon: DatabaseIcon,
      title: 'UN Comtrade',
      description: 'United Nations trade statistics',
      url: 'https://comtrade.un.org/',
      color: '#F59E0B'
    },
    {
      icon: BookOpen,
      title: 'WCO HS Nomenclature',
      description: 'World Customs Organization classification',
      url: 'http://www.wcoomd.org/en/topics/nomenclature.aspx',
      color: '#8B5CF6'
    },
    {
      icon: BarChart3,
      title: 'Data.gov HTS',
      description: 'US government tariff data portal',
      url: 'https://data.gov/dataset/harmonized-tariff-schedule',
      color: '#EC4899'
    }
  ];

  const handleQuickLink = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <motion.div
      className="dashboard"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to TariffAI - Your intelligent tariff management system</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
            <Calculator size={24} color="#3B82F6" />
          </div>
          <div className="stat-content">
            <h3>{stats.totalCalculations.toLocaleString()}</h3>
            <p>Total Calculations</p>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
            <TrendingDown size={24} color="#10B981" />
          </div>
          <div className="stat-content">
            <h3>${stats.totalSavings.toLocaleString()}</h3>
            <p>Total Savings</p>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.1)' }}>
            <Activity size={24} color="#8B5CF6" />
          </div>
          <div className="stat-content">
            <h3>{stats.activeSessions}</h3>
            <p>Active Sessions</p>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
            <CheckCircle size={24} color="#10B981" />
          </div>
          <div className="stat-content">
            <h3>Healthy</h3>
            <p>System Status</p>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-section">
        <h2>Quick Actions</h2>
        <div className="quick-actions-grid">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.title}
              className="quick-action-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleQuickAction(action.path)}
            >
              <div className="action-icon" style={{ background: `${action.color}20` }}>
                <action.icon size={24} color={action.color} />
              </div>
              <h3>{action.title}</h3>
              <p>{action.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Quick Links */}
      <div className="dashboard-section">
        <h2>Quick Links</h2>
        <p className="section-description">Access external trade and tariff resources</p>
        <div className="quick-links-grid">
          {quickLinks.map((link, index) => (
            <motion.div
              key={link.title}
              className="quick-link-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleQuickLink(link.url)}
            >
              <div className="link-icon" style={{ background: `${link.color}20` }}>
                <link.icon size={24} color={link.color} />
              </div>
              <div className="link-content">
                <h3>{link.title}</h3>
                <p>{link.description}</p>
              </div>
              <div className="link-external">
                <ExternalLink size={16} color={link.color} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="dashboard-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {recentActivity.map((activity, index) => (
            <motion.div
              key={index}
              className="activity-item"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              <div className="activity-icon">
                {activity.type === 'calculation' && <Calculator size={16} />}
                {activity.type === 'analysis' && <Package size={16} />}
                {activity.type === 'scenario' && <TrendingUp size={16} />}
              </div>
              <div className="activity-content">
                <h4>{activity.title}</h4>
                <p>{activity.description}</p>
                <span className="activity-time">{activity.time}</span>
              </div>
              <div className="activity-amount">
                {activity.amount}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="dashboard-section">
        <h2>System Status</h2>
        <div className="system-status-grid">
          <motion.div
            className="status-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="status-header">
              <CheckCircle size={20} color="#10B981" />
              <span>Backend API</span>
            </div>
            <div className="status-indicator online">Online</div>
          </motion.div>

          <motion.div
            className="status-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="status-header">
              <CheckCircle size={20} color="#10B981" />
              <span>AI Service</span>
            </div>
            <div className="status-indicator online">Online</div>
          </motion.div>

          <motion.div
            className="status-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
          >
            <div className="status-header">
              <CheckCircle size={20} color="#10B981" />
              <span>Database</span>
            </div>
            <div className="status-indicator online">Online</div>
          </motion.div>

          <motion.div
            className="status-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
          >
            <div className="status-header">
              <CheckCircle size={20} color="#10B981" />
              <span>Vector Search</span>
            </div>
            <div className="status-indicator online">Online</div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
