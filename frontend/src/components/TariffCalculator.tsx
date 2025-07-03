import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calculator, DollarSign, Package, Globe, TrendingUp, AlertTriangle, ArrowRight, Info } from 'lucide-react';

const TariffCalculator: React.FC = () => {
  const [formData, setFormData] = useState({
    htsCode: '',
    productValue: '',
    countryOfOrigin: '',
    shippingCost: '',
    insuranceCost: ''
  });

  const [showComingSoon, setShowComingSoon] = useState(false);

  const handleCalculate = () => {
    setShowComingSoon(true);
    setTimeout(() => setShowComingSoon(false), 3000);
  };

  const sampleCalculations = [
    {
      product: 'Nitrile Gloves',
      htsCode: '4015.19.0510',
      value: '$10,000',
      tariff: '$300',
      totalCost: '$10,300',
      savings: '$200'
    },
    {
      product: 'Cotton T-shirts',
      htsCode: '6109.10.0010',
      value: '$25,000',
      tariff: '$4,125',
      totalCost: '$29,125',
      savings: '$0'
    },
    {
      product: 'Steel Pipes',
      htsCode: '7306.30.50',
      value: '$50,000',
      tariff: '$2,600',
      totalCost: '$52,600',
      savings: '$1,500'
    }
  ];

  return (
    <div className="tariff-calculator">
      <motion.div
        className="calculator-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>
          <Calculator size={24} />
          Tariff Calculator
        </h1>
        <p>Calculate tariffs, duties, and landed costs for your imports</p>
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
              <span>Advanced tariff calculation features coming soon! This will include real-time rate updates, FTA calculations, and detailed breakdowns.</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Calculator Form */}
      <motion.div
        className="calculator-section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="glass-card calculator-card">
          <h3>
            <Calculator size={20} />
            Calculate Tariff
          </h3>
          
          <div className="form-grid">
            <div className="form-group">
              <label>HTS Code</label>
              <input
                type="text"
                className="glass-input"
                placeholder="e.g., 4015.19.0510"
                value={formData.htsCode}
                onChange={(e) => setFormData({...formData, htsCode: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Product Value (USD)</label>
              <input
                type="number"
                className="glass-input"
                placeholder="e.g., 10000"
                value={formData.productValue}
                onChange={(e) => setFormData({...formData, productValue: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Country of Origin</label>
              <select className="glass-input">
                <option value="">Select country</option>
                <option value="china">China</option>
                <option value="vietnam">Vietnam</option>
                <option value="mexico">Mexico</option>
                <option value="canada">Canada</option>
                <option value="germany">Germany</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Shipping Cost (USD)</label>
              <input
                type="number"
                className="glass-input"
                placeholder="e.g., 500"
                value={formData.shippingCost}
                onChange={(e) => setFormData({...formData, shippingCost: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Insurance Cost (USD)</label>
              <input
                type="number"
                className="glass-input"
                placeholder="e.g., 100"
                value={formData.insuranceCost}
                onChange={(e) => setFormData({...formData, insuranceCost: e.target.value})}
              />
            </div>
          </div>

          <motion.button
            className="glass-button primary calculate-button"
            onClick={handleCalculate}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Calculate Tariff
            <Calculator size={20} />
          </motion.button>
        </div>
      </motion.div>

      {/* Sample Calculations */}
      <motion.div
        className="sample-calculations"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="glass-card">
          <h3>
            <TrendingUp size={20} />
            Sample Calculations
          </h3>
          <div className="calculations-grid">
            {sampleCalculations.map((calc, index) => (
              <motion.div
                key={index}
                className="calculation-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
              >
                <div className="calc-header">
                  <h4>{calc.product}</h4>
                  <span className="hts-code">{calc.htsCode}</span>
                </div>
                
                <div className="calc-details">
                  <div className="calc-row">
                    <span>Product Value:</span>
                    <span className="value">{calc.value}</span>
                  </div>
                  <div className="calc-row">
                    <span>Tariff Amount:</span>
                    <span className="tariff">{calc.tariff}</span>
                  </div>
                  <div className="calc-row total">
                    <span>Total Cost:</span>
                    <span className="total-value">{calc.totalCost}</span>
                  </div>
                  {calc.savings !== '$0' && (
                    <div className="calc-row savings">
                      <span>Potential Savings:</span>
                      <span className="savings-value">{calc.savings}</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Features Coming Soon */}
      <motion.div
        className="coming-soon-features"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="glass-card">
          <h3>
            <AlertTriangle size={20} />
            Advanced Features Coming Soon
          </h3>
          <div className="features-grid">
            {[
              {
                title: 'Real-time Rate Updates',
                description: 'Live tariff rates from official sources',
                icon: <TrendingUp size={24} />
              },
              {
                title: 'FTA Calculations',
                description: 'Free Trade Agreement benefits',
                icon: <Globe size={24} />
              },
              {
                title: 'Detailed Breakdowns',
                description: 'Itemized cost analysis',
                icon: <Calculator size={24} />
              },
              {
                title: 'Alternative Sourcing',
                description: 'Find lower-tariff countries',
                icon: <Package size={24} />
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="feature-item"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
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

export default TariffCalculator; 