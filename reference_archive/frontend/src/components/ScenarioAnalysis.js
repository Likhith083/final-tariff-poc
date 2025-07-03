import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, TrendingDown, Plus, Trash2, Save, Share2 } from 'lucide-react';
import apiService from '../services/apiService';
import logger from '../utils/logger';

const ScenarioAnalysis = ({ backendStatus }) => {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    htsCode: '',
    value: '',
    country: 'US',
    alternativeCountry: 'MX'
  });

  useEffect(() => {
    logger.componentMount('ScenarioAnalysis');
    loadScenarios();
  }, []);

  const loadScenarios = () => {
    const mockScenarios = [
      {
        id: 1,
        name: 'Electronics Import - China vs Mexico',
        description: 'Compare importing electronics from China vs Mexico',
        htsCode: '8471.30.01',
        value: 50000,
        baseCountry: 'CN',
        alternativeCountry: 'MX',
        results: {
          base: {
            country: 'China',
            dutyRate: 25,
            dutyAmount: 12500,
            totalCost: 62500,
            leadTime: '45 days',
            risk: 'High'
          },
          alternative: {
            country: 'Mexico',
            dutyRate: 0,
            dutyAmount: 0,
            totalCost: 50000,
            leadTime: '15 days',
            risk: 'Low'
          }
        },
        savings: 12500,
        savingsPercent: 20,
        created: '2024-01-15'
      },
      {
        id: 2,
        name: 'Textile Sourcing Analysis',
        description: 'Compare textile imports from Vietnam vs Bangladesh',
        htsCode: '6204.43.40',
        value: 25000,
        baseCountry: 'VN',
        alternativeCountry: 'BD',
        results: {
          base: {
            country: 'Vietnam',
            dutyRate: 8.5,
            dutyAmount: 2125,
            totalCost: 27125,
            leadTime: '30 days',
            risk: 'Medium'
          },
          alternative: {
            country: 'Bangladesh',
            dutyRate: 0,
            dutyAmount: 0,
            totalCost: 25000,
            leadTime: '35 days',
            risk: 'Medium'
          }
        },
        savings: 2125,
        savingsPercent: 7.8,
        created: '2024-01-14'
      }
    ];
    setScenarios(mockScenarios);
  };

  const handleCreateScenario = async () => {
    if (!newScenario.name || !newScenario.htsCode || !newScenario.value) return;

    try {
      setIsLoading(true);
      logger.userAction('ScenarioAnalysis', `create_scenario: ${newScenario.name}`);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockResults = {
        base: {
          country: 'China',
          dutyRate: 25,
          dutyAmount: parseFloat(newScenario.value) * 0.25,
          totalCost: parseFloat(newScenario.value) * 1.25,
          leadTime: '45 days',
          risk: 'High'
        },
        alternative: {
          country: 'Mexico',
          dutyRate: 0,
          dutyAmount: 0,
          totalCost: parseFloat(newScenario.value),
          leadTime: '15 days',
          risk: 'Low'
        }
      };

      const scenario = {
        id: Date.now(),
        ...newScenario,
        value: parseFloat(newScenario.value),
        results: mockResults,
        savings: mockResults.base.totalCost - mockResults.alternative.totalCost,
        savingsPercent: ((mockResults.base.totalCost - mockResults.alternative.totalCost) / mockResults.base.totalCost) * 100,
        created: new Date().toISOString().split('T')[0]
      };

      setScenarios(prev => [scenario, ...prev]);
      setNewScenario({
        name: '',
        description: '',
        htsCode: '',
        value: '',
        country: 'US',
        alternativeCountry: 'MX'
      });
      setShowCreateForm(false);
      
      logger.info('ScenarioAnalysis', 'Scenario created successfully');
    } catch (error) {
      logger.error('ScenarioAnalysis', 'Failed to create scenario', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteScenario = (scenarioId) => {
    setScenarios(prev => prev.filter(s => s.id !== scenarioId));
    if (selectedScenario?.id === scenarioId) {
      setSelectedScenario(null);
    }
    logger.userAction('ScenarioAnalysis', `delete_scenario: ${scenarioId}`);
  };

  const countries = [
    { code: 'CN', name: 'China' },
    { code: 'MX', name: 'Mexico' },
    { code: 'VN', name: 'Vietnam' },
    { code: 'BD', name: 'Bangladesh' },
    { code: 'IN', name: 'India' },
    { code: 'TH', name: 'Thailand' },
    { code: 'ID', name: 'Indonesia' },
    { code: 'MY', name: 'Malaysia' }
  ];

  const getCountryName = (code) => {
    return countries.find(c => c.code === code)?.name || code;
  };

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <motion.div
      className="scenario-analysis"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="scenario-header">
        <h1>Scenario Analysis</h1>
        <p>Compare trade scenarios and identify cost-saving opportunities</p>
        <div className="coming-soon-banner">
          <span>🚧 Coming Soon - This feature is under development</span>
        </div>
      </div>

      <div className="scenario-content">
        {/* Create New Scenario */}
        <motion.div
          className="create-scenario"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="create-header">
            <BarChart3 size={24} />
            <h3>Create New Scenario</h3>
            <motion.button
              className="toggle-button"
              onClick={() => setShowCreateForm(!showCreateForm)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Plus size={20} />
              {showCreateForm ? 'Cancel' : 'New Scenario'}
            </motion.button>
          </div>

          {showCreateForm && (
            <motion.div
              className="create-form"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="form-grid">
                <div className="form-group">
                  <label>Scenario Name *</label>
                  <input
                    type="text"
                    placeholder="e.g., Electronics Import Comparison"
                    value={newScenario.name}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, name: e.target.value }))}
                    disabled={backendStatus !== 'connected'}
                  />
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <input
                    type="text"
                    placeholder="Brief description of the scenario"
                    value={newScenario.description}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, description: e.target.value }))}
                    disabled={backendStatus !== 'connected'}
                  />
                </div>

                <div className="form-group">
                  <label>HTS Code *</label>
                  <input
                    type="text"
                    placeholder="e.g., 8471.30.01"
                    value={newScenario.htsCode}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, htsCode: e.target.value }))}
                    disabled={backendStatus !== 'connected'}
                  />
                </div>

                <div className="form-group">
                  <label>Value (USD) *</label>
                  <input
                    type="number"
                    placeholder="0.00"
                    value={newScenario.value}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, value: e.target.value }))}
                    disabled={backendStatus !== 'connected'}
                  />
                </div>

                <div className="form-group">
                  <label>Base Country</label>
                  <select
                    value={newScenario.country}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, country: e.target.value }))}
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
                  <label>Alternative Country</label>
                  <select
                    value={newScenario.alternativeCountry}
                    onChange={(e) => setNewScenario(prev => ({ ...prev, alternativeCountry: e.target.value }))}
                    disabled={backendStatus !== 'connected'}
                  >
                    {countries.map(country => (
                      <option key={country.code} value={country.code}>
                        {country.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-actions">
                <motion.button
                  className="create-button"
                  onClick={handleCreateScenario}
                  disabled={!newScenario.name || !newScenario.htsCode || !newScenario.value || backendStatus !== 'connected' || isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isLoading ? 'Creating...' : 'Create Scenario'}
                </motion.button>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Scenarios List */}
        <motion.div
          className="scenarios-list"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3>Your Scenarios</h3>
          
          {scenarios.length === 0 ? (
            <div className="no-scenarios">
              <BarChart3 size={48} />
              <h4>No scenarios yet</h4>
              <p>Create your first scenario to start analyzing trade alternatives</p>
            </div>
          ) : (
            <div className="scenarios-grid">
              {scenarios.map((scenario) => (
                <motion.div
                  key={scenario.id}
                  className={`scenario-card ${selectedScenario?.id === scenario.id ? 'selected' : ''}`}
                  onClick={() => setSelectedScenario(scenario)}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="scenario-header">
                    <h4>{scenario.name}</h4>
                    <div className="scenario-actions">
                      <button
                        className="action-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Handle share
                        }}
                      >
                        <Share2 size={16} />
                      </button>
                      <button
                        className="action-button delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteScenario(scenario.id);
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  <p className="scenario-description">{scenario.description}</p>

                  <div className="scenario-summary">
                    <div className="summary-item">
                      <span>HTS Code:</span>
                      <span>{scenario.htsCode}</span>
                    </div>
                    <div className="summary-item">
                      <span>Value:</span>
                      <span>${scenario.value.toLocaleString()}</span>
                    </div>
                    <div className="summary-item">
                      <span>Savings:</span>
                      <span className="savings">${scenario.savings.toLocaleString()} ({scenario.savingsPercent.toFixed(1)}%)</span>
                    </div>
                  </div>

                  <div className="scenario-comparison">
                    <div className="comparison-item">
                      <span className="country">{getCountryName(scenario.baseCountry)}</span>
                      <span className="cost">${scenario.results.base.totalCost.toLocaleString()}</span>
                    </div>
                    <div className="comparison-arrow">→</div>
                    <div className="comparison-item alternative">
                      <span className="country">{getCountryName(scenario.alternativeCountry)}</span>
                      <span className="cost">${scenario.results.alternative.totalCost.toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="scenario-date">
                    Created: {scenario.created}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Selected Scenario Details */}
        {selectedScenario && (
          <motion.div
            className="scenario-details"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="details-header">
              <h3>{selectedScenario.name}</h3>
              <button
                className="close-details"
                onClick={() => setSelectedScenario(null)}
              >
                ×
              </button>
            </div>

            <div className="details-content">
              <div className="comparison-table">
                <div className="table-header">
                  <div className="header-cell">Metric</div>
                  <div className="header-cell">{getCountryName(selectedScenario.baseCountry)}</div>
                  <div className="header-cell">{getCountryName(selectedScenario.alternativeCountry)}</div>
                  <div className="header-cell">Difference</div>
                </div>

                <div className="table-row">
                  <div className="cell">Duty Rate</div>
                  <div className="cell">{selectedScenario.results.base.dutyRate}%</div>
                  <div className="cell">{selectedScenario.results.alternative.dutyRate}%</div>
                  <div className="cell difference">
                    {selectedScenario.results.base.dutyRate - selectedScenario.results.alternative.dutyRate}%
                  </div>
                </div>

                <div className="table-row">
                  <div className="cell">Duty Amount</div>
                  <div className="cell">${selectedScenario.results.base.dutyAmount.toLocaleString()}</div>
                  <div className="cell">${selectedScenario.results.alternative.dutyAmount.toLocaleString()}</div>
                  <div className="cell difference">
                    ${(selectedScenario.results.base.dutyAmount - selectedScenario.results.alternative.dutyAmount).toLocaleString()}
                  </div>
                </div>

                <div className="table-row">
                  <div className="cell">Total Cost</div>
                  <div className="cell">${selectedScenario.results.base.totalCost.toLocaleString()}</div>
                  <div className="cell">${selectedScenario.results.alternative.totalCost.toLocaleString()}</div>
                  <div className="cell difference savings">
                    -${selectedScenario.savings.toLocaleString()}
                  </div>
                </div>

                <div className="table-row">
                  <div className="cell">Lead Time</div>
                  <div className="cell">{selectedScenario.results.base.leadTime}</div>
                  <div className="cell">{selectedScenario.results.alternative.leadTime}</div>
                  <div className="cell">-</div>
                </div>

                <div className="table-row">
                  <div className="cell">Risk Level</div>
                  <div className="cell">
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: getRiskColor(selectedScenario.results.base.risk) }}
                    >
                      {selectedScenario.results.base.risk}
                    </span>
                  </div>
                  <div className="cell">
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: getRiskColor(selectedScenario.results.alternative.risk) }}
                    >
                      {selectedScenario.results.alternative.risk}
                    </span>
                  </div>
                  <div className="cell">-</div>
                </div>
              </div>

              <div className="savings-summary">
                <div className="savings-card">
                  <TrendingDown size={24} />
                  <div className="savings-content">
                    <h4>Total Savings</h4>
                    <div className="savings-amount">${selectedScenario.savings.toLocaleString()}</div>
                    <div className="savings-percent">{selectedScenario.savingsPercent.toFixed(1)}% cost reduction</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default ScenarioAnalysis; 