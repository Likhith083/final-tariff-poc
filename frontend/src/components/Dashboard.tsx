import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Package, Globe, AlertTriangle, BarChart3, Activity, Search } from 'lucide-react';

const Dashboard: React.FC = () => {
  const kpis = [
    {
      title: 'Total Searches',
      value: '1,247',
      change: '+12.5%',
      trend: 'up',
      icon: <Search size={24} />,
      color: '#4ecdc4'
    },
    {
      title: 'Tariff Savings',
      value: '$45,230',
      change: '+8.3%',
      trend: 'up',
      icon: <DollarSign size={24} />,
      color: '#45b7d1'
    },
    {
      title: 'Products Analyzed',
      value: '892',
      change: '+15.2%',
      trend: 'up',
      icon: <Package size={24} />,
      color: '#96ceb4'
    },
    {
      title: 'Countries Sourced',
      value: '23',
      change: '+2',
      trend: 'up',
      icon: <Globe size={24} />,
      color: '#feca57'
    }
  ];

  const recentActivity = [
    {
      type: 'search',
      title: 'HTS Code Lookup',
      description: 'Nitrile gloves - HTS 4015.19.0510',
      time: '2 minutes ago',
      status: 'completed'
    },
    {
      type: 'calculation',
      title: 'Tariff Calculation',
      description: 'Cotton t-shirts - $2,340 tariff',
      time: '15 minutes ago',
      status: 'completed'
    },
    {
      type: 'alert',
      title: 'Tariff Change Alert',
      description: 'HTS 6109.10.0010 rate increased',
      time: '1 hour ago',
      status: 'warning'
    },
    {
      type: 'analysis',
      title: 'Material Analysis',
      description: 'Alternative sourcing for steel pipes',
      time: '2 hours ago',
      status: 'completed'
    }
  ];

  const topProducts = [
    { name: 'Nitrile Gloves', searches: 156, tariff: '3.0%' },
    { name: 'Cotton T-shirts', searches: 134, tariff: '16.5%' },
    { name: 'Steel Pipes', searches: 98, tariff: '5.2%' },
    { name: 'Plastic Containers', searches: 87, tariff: '2.8%' },
    { name: 'Electronic Components', searches: 76, tariff: '0.0%' }
  ];

  return (
    <div className="dashboard">
      <motion.div
        className="dashboard-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>
          <BarChart3 size={24} />
          Dashboard
        </h1>
        <p>Comprehensive overview of your tariff management activities</p>
      </motion.div>

      {/* KPI Cards */}
      <motion.div
        className="kpi-grid"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        {kpis.map((kpi, index) => (
          <motion.div
            key={kpi.title}
            className="glass-card kpi-card"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
            whileHover={{ 
              scale: 1.02,
              y: -5
            }}
          >
            <div className="kpi-header">
              <div 
                className="kpi-icon"
                style={{ backgroundColor: kpi.color + '20', color: kpi.color }}
              >
                {kpi.icon}
              </div>
              <div className="kpi-trend">
                <span className={`trend-indicator ${kpi.trend}`}>
                  {kpi.trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  {kpi.change}
                </span>
              </div>
            </div>
            
            <div className="kpi-content">
              <h3>{kpi.title}</h3>
              <div className="kpi-value">{kpi.value}</div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <div className="dashboard-grid">
        {/* Recent Activity */}
        <motion.div
          className="activity-section"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="glass-card">
            <h3>
              <Activity size={20} />
              Recent Activity
            </h3>
            <div className="activity-list">
              {recentActivity.map((activity, index) => (
                <motion.div
                  key={index}
                  className={`activity-item ${activity.status}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                >
                  <div className="activity-icon">
                    {activity.type === 'search' && <Search size={16} />}
                    {activity.type === 'calculation' && <DollarSign size={16} />}
                    {activity.type === 'alert' && <AlertTriangle size={16} />}
                    {activity.type === 'analysis' && <BarChart3 size={16} />}
                  </div>
                  <div className="activity-content">
                    <h4>{activity.title}</h4>
                    <p>{activity.description}</p>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                  <div className={`activity-status ${activity.status}`}>
                    {activity.status === 'completed' && '✓'}
                    {activity.status === 'warning' && '⚠'}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Top Products */}
        <motion.div
          className="products-section"
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="glass-card">
            <h3>
              <Package size={20} />
              Top Products
            </h3>
            <div className="products-list">
              {topProducts.map((product, index) => (
                <motion.div
                  key={product.name}
                  className="product-item"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                >
                  <div className="product-rank">#{index + 1}</div>
                  <div className="product-info">
                    <h4>{product.name}</h4>
                    <p>{product.searches} searches</p>
                  </div>
                  <div className="product-tariff">
                    {product.tariff}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Charts Section */}
      <motion.div
        className="charts-section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <div className="glass-card">
          <h3>
            <BarChart3 size={20} />
            Search Trends
          </h3>
          <div className="chart-container">
            <div className="chart-placeholder">
              <div className="chart-bars">
                {[65, 80, 45, 90, 70, 85, 60].map((height, index) => (
                  <motion.div
                    key={index}
                    className="chart-bar"
                    style={{ height: `${height}%` }}
                    initial={{ height: 0 }}
                    animate={{ height: `${height}%` }}
                    transition={{ duration: 0.8, delay: 0.6 + index * 0.1 }}
                  />
                ))}
              </div>
              <div className="chart-labels">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard; 