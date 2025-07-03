import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calculator, DollarSign, Percent, Package, Download, RefreshCw } from 'lucide-react';
import apiService from '../services/apiService';
import logger from '../utils/logger';

const TariffCalculator = ({ backendStatus }) => {
  const [formData, setFormData] = useState({
    htsCode: '',
    country: 'US',
    value: '',
    quantity: '',
    unit: 'pieces'
  });
  const [calculation, setCalculation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [calculationHistory, setCalculationHistory] = useState([]);

  useEffect(() => {
    logger.componentMount('TariffCalculator');
    loadCalculationHistory();
  }, []);

  const loadCalculationHistory = () => {
    const history = [
      {
        id: 1,
        htsCode: '8471.30.01',
        description: 'Portable computers',
        value: 1200,
        duty: 0,
        total: 1200,
        date: '2024-01-15'
      },
      {
        id: 2,
        htsCode: '6204.43.40',
        description: 'Women\'s dresses',
        value: 500,
        duty: 25,
        total: 625,
        date: '2024-01-14'
      }
    ];
    setCalculationHistory(history);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCalculate = async () => {
    if (!formData.htsCode || !formData.value || backendStatus !== 'connected') return;

    try {
      setIsLoading(true);
      logger.userAction('TariffCalculator', `calculate_tariff: ${formData.htsCode}`);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock calculation result
      const mockCalculation = {
        htsCode: formData.htsCode,
        description: 'Portable automatic data processing machines',
        country: formData.country,
        value: parseFloat(formData.value),
        quantity: parseInt(formData.quantity) || 1,
        unit: formData.unit,
        dutyRate: 0,
        dutyAmount: 0,
        totalValue: parseFloat(formData.value),
        breakdown: {
          customsValue: parseFloat(formData.value),
          duty: 0,
          processingFee: 25,
          total: parseFloat(formData.value) + 25
        }
      };

      setCalculation(mockCalculation);
      
      // Add to history
      const newHistoryItem = {
        id: Date.now(),
        htsCode: mockCalculation.htsCode,
        description: mockCalculation.description,
        value: mockCalculation.value,
        duty: mockCalculation.dutyAmount,
        total: mockCalculation.breakdown.total,
        date: new Date().toISOString().split('T')[0]
      };
      
      setCalculationHistory(prev => [newHistoryItem, ...prev.slice(0, 4)]);
      
      logger.info('TariffCalculator', 'Calculation completed successfully');
    } catch (error) {
      logger.error('TariffCalculator', 'Calculation failed', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      htsCode: '',
      country: 'US',
      value: '',
      quantity: '',
      unit: 'pieces'
    });
    setCalculation(null);
    logger.userAction('TariffCalculator', 'reset_form');
  };

  const exportCalculation = () => {
    if (!calculation) return;
    
    const data = {
      calculation,
      timestamp: new Date().toISOString(),
      exportedBy: 'TariffAI'
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tariff-calculation-${calculation.htsCode}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    logger.userAction('TariffCalculator', 'export_calculation');
  };

  const countries = [
    { code: 'US', name: 'United States' },
    { code: 'CA', name: 'Canada' },
    { code: 'MX', name: 'Mexico' },
    { code: 'EU', name: 'European Union' },
    { code: 'CN', name: 'China' },
    { code: 'JP', name: 'Japan' }
  ];

  const units = [
    { value: 'pieces', label: 'Pieces' },
    { value: 'kg', label: 'Kilograms' },
    { value: 'liters', label: 'Liters' },
    { value: 'meters', label: 'Meters' },
    { value: 'pairs', label: 'Pairs' }
  ];

  return (
    <motion.div
      className="tariff-calculator"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="calculator-header">
        <h1>Tariff Calculator</h1>
        <p>Calculate import duties, taxes, and total landed costs</p>
        <div className="coming-soon-banner">
          <span>🚧 Coming Soon - This feature is under development</span>
        </div>
      </div>

      <div className="calculator-content">
        {/* Input Form */}
        <motion.div
          className="calculator-form"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="form-header">
            <Calculator size={24} />
            <h3>Calculation Parameters</h3>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>HTS Code *</label>
              <input
                type="text"
                placeholder="e.g., 8471.30.01"
                value={formData.htsCode}
                onChange={(e) => handleInputChange('htsCode', e.target.value)}
                disabled={backendStatus !== 'connected'}
              />
            </div>

            <div className="form-group">
              <label>Country of Origin</label>
              <select
                value={formData.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
                disabled={backendStatus !== 'connected'}
              >
                {countries.map(country => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Customs Value (USD) *</label>
              <div className="input-with-icon">
                <DollarSign size={16} />
                <input
                  type="number"
                  placeholder="0.00"
                  value={formData.value}
                  onChange={(e) => handleInputChange('value', e.target.value)}
                  disabled={backendStatus !== 'connected'}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Quantity</label>
              <input
                type="number"
                placeholder="1"
                value={formData.quantity}
                onChange={(e) => handleInputChange('quantity', e.target.value)}
                disabled={backendStatus !== 'connected'}
              />
            </div>

            <div className="form-group">
              <label>Unit of Measure</label>
              <select
                value={formData.unit}
                onChange={(e) => handleInputChange('unit', e.target.value)}
                disabled={backendStatus !== 'connected'}
              >
                {units.map(unit => (
                  <option key={unit.value} value={unit.value}>
                    {unit.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <motion.button
              className="calculate-button"
              onClick={handleCalculate}
              disabled={!formData.htsCode || !formData.value || backendStatus !== 'connected' || isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <RefreshCw size={20} />
                </motion.div>
              ) : (
                <>
                  <Calculator size={20} />
                  Calculate Tariff
                </>
              )}
            </motion.button>

            <button
              className="reset-button"
              onClick={handleReset}
              disabled={backendStatus !== 'connected'}
            >
              <RefreshCw size={20} />
              Reset
            </button>
          </div>
        </motion.div>

        {/* Calculation Results */}
        {calculation && (
          <motion.div
            className="calculation-results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="results-header">
              <h3>Calculation Results</h3>
              <button
                className="export-button"
                onClick={exportCalculation}
              >
                <Download size={16} />
                Export
              </button>
            </div>

            <div className="results-grid">
              <div className="result-card primary">
                <div className="result-icon">
                  <DollarSign size={24} />
                </div>
                <div className="result-content">
                  <h4>Total Landed Cost</h4>
                  <div className="result-value">${calculation.breakdown.total.toFixed(2)}</div>
                </div>
              </div>

              <div className="result-card">
                <div className="result-icon">
                  <Percent size={24} />
                </div>
                <div className="result-content">
                  <h4>Duty Rate</h4>
                  <div className="result-value">{calculation.dutyRate}%</div>
                </div>
              </div>

              <div className="result-card">
                <div className="result-icon">
                  <Package size={24} />
                </div>
                <div className="result-content">
                  <h4>Duty Amount</h4>
                  <div className="result-value">${calculation.dutyAmount.toFixed(2)}</div>
                </div>
              </div>
            </div>

            <div className="breakdown-details">
              <h4>Cost Breakdown</h4>
              <div className="breakdown-list">
                <div className="breakdown-item">
                  <span>Customs Value:</span>
                  <span>${calculation.breakdown.customsValue.toFixed(2)}</span>
                </div>
                <div className="breakdown-item">
                  <span>Duty ({calculation.dutyRate}%):</span>
                  <span>${calculation.breakdown.duty.toFixed(2)}</span>
                </div>
                <div className="breakdown-item">
                  <span>Processing Fee:</span>
                  <span>${calculation.breakdown.processingFee.toFixed(2)}</span>
                </div>
                <div className="breakdown-item total">
                  <span>Total:</span>
                  <span>${calculation.breakdown.total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="calculation-info">
              <div className="info-item">
                <label>HTS Code:</label>
                <span>{calculation.htsCode}</span>
              </div>
              <div className="info-item">
                <label>Description:</label>
                <span>{calculation.description}</span>
              </div>
              <div className="info-item">
                <label>Country:</label>
                <span>{calculation.country}</span>
              </div>
              <div className="info-item">
                <label>Quantity:</label>
                <span>{calculation.quantity} {calculation.unit}</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Calculation History */}
        {calculationHistory.length > 0 && (
          <motion.div
            className="calculation-history"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h3>Recent Calculations</h3>
            <div className="history-list">
              {calculationHistory.map((item) => (
                <div key={item.id} className="history-item">
                  <div className="history-main">
                    <div className="history-code">{item.htsCode}</div>
                    <div className="history-description">{item.description}</div>
                  </div>
                  <div className="history-values">
                    <div className="history-value">${item.value}</div>
                    <div className="history-duty">Duty: ${item.duty}</div>
                    <div className="history-total">Total: ${item.total}</div>
                  </div>
                  <div className="history-date">{item.date}</div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default TariffCalculator; 