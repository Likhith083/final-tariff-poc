import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Globe, Calculator, BarChart3, AlertTriangle, ArrowRight, Info, RefreshCw } from 'lucide-react';

const ScenarioAnalysis: React.FC = () => {
  const [currentScenario, setCurrentScenario] = useState('base');
  const [showComingSoon, setShowComingSoon] = useState(false);

  const handleScenarioChange = () => {
    setShowComingSoon(true);
    setTimeout(() => setShowComingSoon(false), 3000);
  };

  const scenarios = [
    {
      id: 'base',
      name: 'Current Scenario',
      country: 'China',
      tariff: '3.0%',
      totalCost: '$10,300',
      savings: '$0'
    },
    {
      id: 'vietnam',
      name: 'Vietnam Sourcing',
      country: 'Vietnam',
      tariff: '0.0%',
      totalCost: '$10,000',
      savings: '$300'
    },
    {
      id: 'mexico',
      name: 'Mexico Sourcing',
      country: 'Mexico',
      tariff: '0.0%',
      totalCost: '$10,200',
      savings: '$100'
    },
    {
      id: 'rate-increase',
      name: 'Rate Increase',
      country: 'China',
      tariff: '5.0%',
      totalCost: '$10,500',
      savings: '-$200'
    }
  ];

  const comparisonData = [
    { metric: 'Product Cost', base: '$10,000', scenario: '$10,000', change: '0%' },
    { metric: 'Tariff Amount', base: '$300', scenario: '$0', change: '-100%' },
    { metric: 'Shipping Cost', base: '$500', scenario: '$600', change: '+20%' },
    { metric: 'Insurance', base: '$100', scenario: '$100', change: '0%' },
    { metric: 'Total Landed Cost', base: '$10,900', scenario: '$10,700', change: '-1.8%' }
  ];

  return (
    <div className="scenario-analysis">
      <motion.div
        className="scenario-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>
          <BarChart3 size={24} />
          Scenario Analysis
        </h1>
        <p>Compare different sourcing scenarios and tariff impacts</p>
      </motion.div>

      {/* Coming Soon Alert */}
      <AnimatePresence>
        {showComingSoon && (
          <motion.div
            className="coming-soon-alert"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="glass-card alert-card">
              <Info size={20} />
              <span>Advanced scenario modeling coming soon! This will include real-time data, predictive analytics, and automated recommendations.</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scenario Selector */}
      <motion.div
        className="scenario-selector"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="glass-card">
          <h3>
            <Globe size={20} />
            Select Scenario
          </h3>
          <div className="scenario-grid">
            {scenarios.map((scenario, index) => (
              <motion.button
                key={scenario.id}
                className={`scenario-card ${currentScenario === scenario.id ? 'active' : ''}`}
                onClick={() => {
                  setCurrentScenario(scenario.id);
                  handleScenarioChange();
                }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="scenario-header">
                  <h4>{scenario.name}</h4>
                  <span className="country">{scenario.country}</span>
                </div>
                <div className="scenario-metrics">
                  <div className="metric">
                    <span>Tariff Rate:</span>
                    <span className="value">{scenario.tariff}</span>
                  </div>
                  <div className="metric">
                    <span>Total Cost:</span>
                    <span className="value">{scenario.totalCost}</span>
                  </div>
                  <div className="metric savings">
                    <span>Savings:</span>
                    <span className={`value ${scenario.savings.startsWith('-') ? 'negative' : 'positive'}`}>
                      {scenario.savings}
                    </span>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Comparison Chart */}
      <motion.div
        className="comparison-section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="glass-card">
          <h3>
            <TrendingUp size={20} />
            Cost Comparison
          </h3>
          <div className="comparison-table">
            <div className="table-header">
              <div className="header-cell">Metric</div>
              <div className="header-cell">Base Scenario</div>
              <div className="header-cell">Selected Scenario</div>
              <div className="header-cell">Change</div>
            </div>
            {comparisonData.map((row, index) => (
              <motion.div
                key={index}
                className="table-row"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
              >
                <div className="cell metric">{row.metric}</div>
                <div className="cell base">{row.base}</div>
                <div className="cell scenario">{row.scenario}</div>
                <div className={`cell change ${row.change.startsWith('-') ? 'negative' : row.change.startsWith('+') ? 'positive' : 'neutral'}`}>
                  {row.change}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Visual Comparison */}
      <motion.div
        className="visual-comparison"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="glass-card">
          <h3>
            <BarChart3 size={20} />
            Cost Breakdown
          </h3>
          <div className="chart-container">
            <div className="chart-placeholder">
              <div className="chart-bars">
                {[100, 85, 95, 110].map((height, index) => (
                  <motion.div
                    key={index}
                    className="chart-bar"
                    style={{ height: `${height}%` }}
                    initial={{ height: 0 }}
                    animate={{ height: `${height}%` }}
                    transition={{ duration: 0.8, delay: 0.4 + index * 0.1 }}
                  />
                ))}
              </div>
              <div className="chart-labels">
                {['Base', 'Vietnam', 'Mexico', 'Rate +']}
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Recommendations */}
      <motion.div
        className="recommendations"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="glass-card">
          <h3>
            <AlertTriangle size={20} />
            AI Recommendations
          </h3>
          <div className="recommendations-list">
            {[
              {
                title: 'Switch to Vietnam Sourcing',
                description: 'Potential savings of $300 per shipment',
                impact: 'High',
                confidence: '95%'
              },
              {
                title: 'Consider Mexico for Logistics',
                description: 'Better shipping times and lower costs',
                impact: 'Medium',
                confidence: '87%'
              },
              {
                title: 'Monitor Rate Changes',
                description: 'China rates may increase in Q3',
                impact: 'Medium',
                confidence: '78%'
              }
            ].map((rec, index) => (
              <motion.div
                key={index}
                className="recommendation-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              >
                <div className="rec-header">
                  <h4>{rec.title}</h4>
                  <div className="rec-metrics">
                    <span className={`impact ${rec.impact.toLowerCase()}`}>{rec.impact}</span>
                    <span className="confidence">{rec.confidence} confidence</span>
                  </div>
                </div>
                <p>{rec.description}</p>
                <button className="rec-action">
                  Learn More
                  <ArrowRight size={16} />
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Coming Soon Features */}
      <motion.div
        className="coming-soon-features"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <div className="glass-card">
          <h3>
            <RefreshCw size={20} />
            Advanced Features Coming Soon
          </h3>
          <div className="features-grid">
            {[
              {
                title: 'Predictive Analytics',
                description: 'AI-powered cost forecasting',
                icon: <TrendingUp size={24} />
              },
              {
                title: 'Real-time Data',
                description: 'Live tariff and exchange rates',
                icon: <RefreshCw size={24} />
              },
              {
                title: 'Automated Recommendations',
                description: 'Smart sourcing suggestions',
                icon: <BarChart3 size={24} />
              },
              {
                title: 'Risk Assessment',
                description: 'Political and economic risk analysis',
                icon: <AlertTriangle size={24} />
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="feature-item"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
              >
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h4>{feature.title}</h4>
                <p>{feature.description}</p>
                <span className="coming-soon-badge">Coming Soon</span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ScenarioAnalysis; 