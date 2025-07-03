import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Calculator, 
  BarChart3, 
  MessageSquare, 
  TrendingUp, 
  AlertTriangle,
  Globe,
  FileText,
  Settings,
  Zap,
  ExternalLink,
  Building2,
  Database,
  BookOpen,
  Shield,
  BarChart
} from 'lucide-react';
import apiService from '../services/apiService';
import logger from '../utils/logger';

const Dashboard = ({ backendStatus, onViewChange }) => {
  const [stats, setStats] = useState({
    totalHTS: 0,
    recentSearches: 0,
    calculations: 0,
    scenarios: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    logger.componentMount('Dashboard');
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      // Simulate loading dashboard data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalHTS: 12500,
        recentSearches: 47,
        calculations: 23,
        scenarios: 8
      });

      setRecentActivity([
        { id: 1, type: 'search', text: 'HTS search for "electronics"', time: '2 min ago' },
        { id: 2, type: 'calculation', text: 'Tariff calculation for HTS 8471.30.01', time: '5 min ago' },
        { id: 3, type: 'scenario', text: 'Scenario analysis: Trade war impact', time: '12 min ago' },
        { id: 4, type: 'chat', text: 'AI chat: "What are the duties for textiles?"', time: '15 min ago' }
      ]);

      setIsLoading(false);
    } catch (error) {
      logger.error('Dashboard', 'Failed to load dashboard data', error);
      setIsLoading(false);
    }
  };

  const QuickActionCard = ({ icon: Icon, title, description, color, onClick, disabled = false }) => (
    <motion.div
      className={`quick-action-card ${color} ${disabled ? 'disabled' : ''}`}
      whileHover={!disabled ? { scale: 1.02, y: -2 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={!disabled ? onClick : undefined}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="card-icon">
        <Icon size={24} />
      </div>
      <div className="card-content">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      <div className="card-arrow">→</div>
    </motion.div>
  );

  const QuickLinkCard = ({ icon: Icon, title, description, url, color }) => (
    <motion.a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`quick-link-card ${color}`}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="link-icon">
        <Icon size={20} />
      </div>
      <div className="link-content">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      <div className="link-arrow">
        <ExternalLink size={16} />
      </div>
    </motion.a>
  );

  const StatCard = ({ title, value, icon: Icon, color, change }) => (
    <motion.div
      className={`stat-card ${color}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="stat-icon">
        <Icon size={20} />
      </div>
      <div className="stat-content">
        <h3>{title}</h3>
        <div className="stat-value">{value.toLocaleString()}</div>
        {change && (
          <div className={`stat-change ${change > 0 ? 'positive' : 'negative'}`}>
            {change > 0 ? '+' : ''}{change}% from last month
          </div>
        )}
      </div>
    </motion.div>
  );

  const ActivityItem = ({ activity }) => (
    <motion.div
      className="activity-item"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={`activity-icon ${activity.type}`}>
        {activity.type === 'search' && <Search size={16} />}
        {activity.type === 'calculation' && <Calculator size={16} />}
        {activity.type === 'scenario' && <BarChart3 size={16} />}
        {activity.type === 'chat' && <MessageSquare size={16} />}
      </div>
      <div className="activity-content">
        <p>{activity.text}</p>
        <span className="activity-time">{activity.time}</span>
      </div>
    </motion.div>
  );

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Zap size={32} />
        </motion.div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <motion.div
      className="dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Welcome to TariffAI</h1>
          <p>Your intelligent companion for tariff management and trade compliance</p>
        </div>
        <div className="header-status">
          <span className={`status-badge ${backendStatus}`}>
            {backendStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <QuickActionCard
            icon={Search}
            title="HTS Search"
            description="Find HTS codes and descriptions"
            color="blue"
            onClick={() => onViewChange('hts')}
            disabled={backendStatus !== 'connected'}
          />
          <QuickActionCard
            icon={Calculator}
            title="Tariff Calculator"
            description="Calculate duties and taxes"
            color="green"
            onClick={() => onViewChange('tariff')}
            disabled={backendStatus !== 'connected'}
          />
          <QuickActionCard
            icon={BarChart3}
            title="Scenario Analysis"
            description="Analyze trade scenarios"
            color="purple"
            onClick={() => onViewChange('scenario')}
            disabled={backendStatus !== 'connected'}
          />
          <QuickActionCard
            icon={MessageSquare}
            title="AI Chat"
            description="Ask questions about tariffs"
            color="orange"
            onClick={() => onViewChange('chat')}
            disabled={backendStatus !== 'connected'}
          />
        </div>
      </div>

      {/* Quick Links */}
      <div className="quick-links">
        <h2>External Resources</h2>
        <p className="section-description">Access official trade and tariff databases</p>
        <div className="links-grid">
          <QuickLinkCard
            icon={Building2}
            title="USITC HTS Database"
            description="Official US Harmonized Tariff Schedule"
            url="https://hts.usitc.gov/"
            color="blue"
          />
          <QuickLinkCard
            icon={Database}
            title="USITC DataWeb"
            description="Comprehensive trade data and statistics"
            url="https://dataweb.usitc.gov/"
            color="green"
          />
          <QuickLinkCard
            icon={Globe}
            title="WTO Tariff Analysis"
            description="Global tariff rates and trade agreements"
            url="https://ta.wto.org/"
            color="purple"
          />
          <QuickLinkCard
            icon={BarChart}
            title="UN Comtrade"
            description="International trade statistics database"
            url="https://comtrade.un.org/data/"
            color="orange"
          />
          <QuickLinkCard
            icon={BookOpen}
            title="WCO HS Nomenclature"
            description="Harmonized System classification guide"
            url="http://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx"
            color="teal"
          />
          <QuickLinkCard
            icon={Shield}
            title="Data.gov HTS"
            description="US government HTS datasets"
            url="https://catalog.data.gov/dataset?q=harmonized+tariff+schedule"
            color="indigo"
          />
        </div>
      </div>

      {/* Statistics */}
      <div className="dashboard-stats">
        <h2>Overview</h2>
        <div className="stats-grid">
          <StatCard
            title="Total HTS Codes"
            value={stats.totalHTS}
            icon={FileText}
            color="blue"
            change={12}
          />
          <StatCard
            title="Recent Searches"
            value={stats.recentSearches}
            icon={Search}
            color="green"
            change={8}
          />
          <StatCard
            title="Calculations"
            value={stats.calculations}
            icon={Calculator}
            color="purple"
            change={-3}
          />
          <StatCard
            title="Scenarios"
            value={stats.scenarios}
            icon={TrendingUp}
            color="orange"
            change={25}
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {recentActivity.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">
            <Globe size={24} />
          </div>
          <h3>Global Coverage</h3>
          <p>Access tariff data from 200+ countries and territories</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <Zap size={24} />
          </div>
          <h3>AI-Powered</h3>
          <p>Advanced AI for intelligent HTS classification and analysis</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <AlertTriangle size={24} />
          </div>
          <h3>Risk Assessment</h3>
          <p>Identify potential compliance risks and trade barriers</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <Settings size={24} />
          </div>
          <h3>Customizable</h3>
          <p>Tailor the platform to your specific business needs</p>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard; 