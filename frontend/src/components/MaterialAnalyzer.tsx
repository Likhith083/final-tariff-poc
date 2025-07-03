import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Beaker, TestTube, TrendingDown, AlertTriangle, ArrowRight, Info, Zap, Target } from 'lucide-react';

const MaterialAnalyzer: React.FC = () => {
  const [selectedMaterial, setSelectedMaterial] = useState('nitrile');
  const [showComingSoon, setShowComingSoon] = useState(false);

  const handleMaterialChange = () => {
    setShowComingSoon(true);
    setTimeout(() => setShowComingSoon(false), 3000);
  };

  const materials = [
    {
      id: 'nitrile',
      name: 'Nitrile Gloves',
      composition: '100% Nitrile',
      tariff: '3.0%',
      alternatives: [
        { material: 'Latex', tariff: '0.0%', savings: '$300', quality: '95%' },
        { material: 'Vinyl', tariff: '2.5%', savings: '$50', quality: '85%' },
        { material: 'Polyethylene', tariff: '1.0%', savings: '$200', quality: '90%' }
      ]
    },
    {
      id: 'cotton',
      name: 'Cotton T-shirts',
      composition: '100% Cotton',
      tariff: '16.5%',
      alternatives: [
        { material: 'Polyester Blend', tariff: '12.0%', savings: '$1,125', quality: '92%' },
        { material: 'Bamboo', tariff: '8.0%', savings: '$2,125', quality: '88%' },
        { material: 'Hemp', tariff: '5.0%', savings: '$2,875', quality: '85%' }
      ]
    },
    {
      id: 'steel',
      name: 'Steel Pipes',
      composition: 'Carbon Steel',
      tariff: '5.2%',
      alternatives: [
        { material: 'Aluminum', tariff: '2.0%', savings: '$1,600', quality: '90%' },
        { material: 'PVC', tariff: '0.0%', savings: '$2,600', quality: '75%' },
        { material: 'Copper', tariff: '1.5%', savings: '$1,850', quality: '95%' }
      ]
    }
  ];

  const currentMaterial = materials.find(m => m.id === selectedMaterial);

  return (
    <div className="material-analyzer">
      <motion.div
        className="analyzer-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>
          <Beaker size={24} />
          Material Analyzer
        </h1>
        <p>Analyze material compositions and find cost-saving alternatives</p>
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
              <span>Advanced material analysis coming soon! This will include AI-powered composition detection, real-time quality assessment, and automated supplier recommendations.</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Material Selector */}
      <motion.div
        className="material-selector"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="glass-card">
          <h3>
            <TestTube size={20} />
            Select Material
          </h3>
          <div className="material-grid">
            {materials.map((material, index) => (
              <motion.button
                key={material.id}
                className={`material-card ${selectedMaterial === material.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedMaterial(material.id);
                  handleMaterialChange();
                }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="material-header">
                  <h4>{material.name}</h4>
                  <span className="composition">{material.composition}</span>
                </div>
                <div className="material-metrics">
                  <div className="metric">
                    <span>Current Tariff:</span>
                    <span className="value">{material.tariff}</span>
                  </div>
                  <div className="metric">
                    <span>Alternatives:</span>
                    <span className="value">{material.alternatives.length}</span>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Current Material Analysis */}
      {currentMaterial && (
        <motion.div
          className="current-analysis"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="glass-card">
            <h3>
              <Target size={20} />
              Current Material Analysis
            </h3>
            <div className="analysis-content">
              <div className="material-info">
                <h4>{currentMaterial.name}</h4>
                <p><strong>Composition:</strong> {currentMaterial.composition}</p>
                <p><strong>Current Tariff Rate:</strong> {currentMaterial.tariff}</p>
                <p><strong>Quality Score:</strong> 95%</p>
                <p><strong>Durability:</strong> Excellent</p>
                <p><strong>Cost Impact:</strong> High</p>
              </div>
              <div className="material-chart">
                <div className="chart-placeholder">
                  <div className="pie-chart">
                    <div className="pie-segment current" style={{ transform: 'rotate(0deg)' }}>
                      <span>Current</span>
                    </div>
                    <div className="pie-segment potential" style={{ transform: 'rotate(180deg)' }}>
                      <span>Potential</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Alternative Materials */}
      {currentMaterial && (
        <motion.div
          className="alternatives-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="glass-card">
            <h3>
              <TrendingDown size={20} />
              Alternative Materials
            </h3>
            <div className="alternatives-grid">
              {currentMaterial.alternatives.map((alt, index) => (
                <motion.div
                  key={index}
                  className="alternative-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                >
                  <div className="alt-header">
                    <h4>{alt.material}</h4>
                    <span className="tariff-rate">{alt.tariff}</span>
                  </div>
                  <div className="alt-metrics">
                    <div className="metric">
                      <span>Potential Savings:</span>
                      <span className="savings">{alt.savings}</span>
                    </div>
                    <div className="metric">
                      <span>Quality Retention:</span>
                      <span className="quality">{alt.quality}</span>
                    </div>
                  </div>
                  <div className="alt-actions">
                    <button className="alt-action primary">
                      Switch to {alt.material}
                      <ArrowRight size={16} />
                    </button>
                    <button className="alt-action secondary">
                      Learn More
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Quality Impact Analysis */}
      <motion.div
        className="quality-analysis"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="glass-card">
          <h3>
            <Zap size={20} />
            Quality Impact Analysis
          </h3>
          <div className="quality-grid">
            {[
              { property: 'Durability', current: 95, alternative: 90, impact: 'Minimal' },
              { property: 'Flexibility', current: 85, alternative: 88, impact: 'Improved' },
              { property: 'Chemical Resistance', current: 90, alternative: 85, impact: 'Slight Decrease' },
              { property: 'Cost Efficiency', current: 60, alternative: 85, impact: 'Significant Improvement' }
            ].map((prop, index) => (
              <motion.div
                key={index}
                className="quality-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              >
                <div className="quality-header">
                  <h4>{prop.property}</h4>
                  <span className={`impact ${prop.impact.toLowerCase().includes('improvement') ? 'positive' : prop.impact.toLowerCase().includes('decrease') ? 'negative' : 'neutral'}`}>
                    {prop.impact}
                  </span>
                </div>
                <div className="quality-bars">
                  <div className="bar-container">
                    <span>Current</span>
                    <div className="bar">
                      <motion.div
                        className="bar-fill current"
                        initial={{ width: 0 }}
                        animate={{ width: `${prop.current}%` }}
                        transition={{ duration: 0.8, delay: 0.6 + index * 0.1 }}
                      />
                    </div>
                    <span>{prop.current}%</span>
                  </div>
                  <div className="bar-container">
                    <span>Alternative</span>
                    <div className="bar">
                      <motion.div
                        className="bar-fill alternative"
                        initial={{ width: 0 }}
                        animate={{ width: `${prop.alternative}%` }}
                        transition={{ duration: 0.8, delay: 0.7 + index * 0.1 }}
                      />
                    </div>
                    <span>{prop.alternative}%</span>
                  </div>
                </div>
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
            <AlertTriangle size={20} />
            Advanced Features Coming Soon
          </h3>
          <div className="features-grid">
            {[
              {
                title: 'AI Composition Detection',
                description: 'Automated material analysis',
                icon: <Beaker size={24} />
              },
              {
                title: 'Real-time Quality Assessment',
                description: 'Live quality monitoring',
                icon: <TestTube size={24} />
              },
              {
                title: 'Supplier Recommendations',
                description: 'AI-powered supplier matching',
                icon: <Target size={24} />
              },
              {
                title: 'Sustainability Analysis',
                description: 'Environmental impact assessment',
                icon: <Zap size={24} />
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

export default MaterialAnalyzer; 