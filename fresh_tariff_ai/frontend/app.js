/**
 * TariffAI Frontend Application
 * Modern JavaScript with enhanced functionality and glassmorphism UI
 */

class TariffAI {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        
        this.initializeElements();
        this.bindEvents();
        this.checkConnection();
        this.initializeTabs();
    }

    initializeElements() {
        // Core elements
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendMessage');
        this.chatMessages = document.getElementById('chatMessages');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingMessage = document.getElementById('loadingMessage');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.connectionIcon = document.getElementById('connectionIcon');

        // Tab elements
        this.tabButtons = document.querySelectorAll('.tab-btn');
        this.tabPanes = document.querySelectorAll('.tab-pane');

        // HTS Lookup elements
        this.htsSearchInput = document.getElementById('htsSearchInput');
        this.htsSearchBtn = document.getElementById('htsSearchBtn');
        this.htsResults = document.getElementById('htsResults');
        this.categoryFilter = document.getElementById('categoryFilter');
        this.rateFilter = document.getElementById('rateFilter');

        // Tariff Calculator elements
        this.calcHtsCode = document.getElementById('calcHtsCode');
        this.calcValue = document.getElementById('calcValue');
        this.calcQuantity = document.getElementById('calcQuantity');
        this.calcCountry = document.getElementById('calcCountry');
        this.calculateBtn = document.getElementById('calculateBtn');
        this.calcResults = document.getElementById('calcResults');

        // Risk Assessment elements
        this.riskInput = document.getElementById('riskInput');
        this.assessRiskBtn = document.getElementById('assessRiskBtn');
        this.riskResults = document.getElementById('riskResults');

        // Enhanced Scenario Analysis elements
        this.scenarioProductDesc = document.getElementById('scenarioProductDesc');
        this.scenarioHtsCode = document.getElementById('scenarioHtsCode');
        this.scenarioBaseValue = document.getElementById('scenarioBaseValue');
        this.scenarioQuantity = document.getElementById('scenarioQuantity');
        this.scenarioOriginCountry = document.getElementById('scenarioOriginCountry');
        this.scenarioDestCountry = document.getElementById('scenarioDestCountry');
        this.scenarioCurrency = document.getElementById('scenarioCurrency');
        this.scenarioShippingCost = document.getElementById('scenarioShippingCost');
        this.scenarioInsuranceCost = document.getElementById('scenarioInsuranceCost');
        this.scenarioAdditionalCosts = document.getElementById('scenarioAdditionalCosts');
        this.createScenarioBtn = document.getElementById('createScenarioBtn');
        this.quickAnalysisBtn = document.getElementById('quickAnalysisBtn');
        this.compareScenariosBtn = document.getElementById('compareScenariosBtn');
        this.scenarioResults = document.getElementById('scenarioResults');

        // Data Ingestion elements
        this.docType = document.getElementById('docType');
        this.docTitle = document.getElementById('docTitle');
        this.docContent = document.getElementById('docContent');
        this.fileUpload = document.getElementById('fileUpload');
        this.ingestDataBtn = document.getElementById('ingestDataBtn');
        this.ingestionStatus = document.getElementById('ingestionStatus');

        // Chat controls
        this.clearChatBtn = document.getElementById('clearChat');
        this.exportChatBtn = document.getElementById('exportChat');
        this.quickButtons = document.querySelectorAll('.quick-btn');
    }

    bindEvents() {
        // Chat events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Chat controls
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        this.exportChatBtn.addEventListener('click', () => this.exportChat());

        // Quick action buttons
        this.quickButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                this.messageInput.value = query;
                this.sendMessage();
            });
        });

        // HTS Lookup events
        this.htsSearchBtn.addEventListener('click', () => this.searchHTS());
        this.htsSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchHTS();
        });

        // Tariff Calculator events
        this.calculateBtn.addEventListener('click', () => this.calculateTariff());

        // Risk Assessment events
        this.assessRiskBtn.addEventListener('click', () => this.assessRisk());

        // Scenario Analysis events
        this.createScenarioBtn.addEventListener('click', () => this.createScenario());
        this.quickAnalysisBtn.addEventListener('click', () => this.quickAnalysis());
        this.compareScenariosBtn.addEventListener('click', () => this.compareScenarios());
        
        // Load scenarios when scenario tab is opened
        document.querySelector('[data-tab="scenario-analysis"]').addEventListener('click', () => {
            setTimeout(() => this.loadScenarios(), 100);
        });

        // Data Ingestion events
        this.ingestDataBtn.addEventListener('click', () => this.ingestData());
        this.fileUpload.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    initializeTabs() {
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;
                this.switchTab(targetTab);
            });
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        this.tabButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });

        // Update tab panes
        this.tabPanes.forEach(pane => {
            pane.classList.remove('active');
            if (pane.id === `${tabName}-tab`) {
                pane.classList.add('active');
            }
        });
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/status`);
            if (response.ok) {
                this.isConnected = true;
                this.updateStatus('Connected', 'online');
                this.connectionIcon.className = 'fas fa-wifi';
            } else {
                throw new Error('Backend not responding');
            }
        } catch (error) {
            this.isConnected = false;
            this.updateStatus('Disconnected', 'offline');
            this.connectionIcon.className = 'fas fa-wifi-slash';
            console.error('Connection check failed:', error);
        }
    }

    updateStatus(text, status) {
        this.statusText.textContent = text;
        this.statusIndicator.className = `status-indicator ${status}`;
    }

    showLoading(message = 'Processing your request...') {
        this.loadingMessage.textContent = message;
        this.loadingOverlay.classList.add('active');
    }

    hideLoading() {
        this.loadingOverlay.classList.remove('active');
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Chat functionality
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';

        // Show loading
        this.showLoading('AI is thinking...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.addMessage(data.response, 'assistant');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'system');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('Connection error. Please check if the backend is running.', 'system');
        } finally {
            this.hideLoading();
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    clearChat() {
        this.chatMessages.innerHTML = `
            <div class="message system">
                <div class="message-content">
                    <i class="fas fa-info-circle"></i>
                    Chat cleared. How can I help you today?
                </div>
            </div>
        `;
    }

    exportChat() {
        const messages = Array.from(this.chatMessages.children).map(msg => {
            const type = msg.classList.contains('user') ? 'User' : 
                        msg.classList.contains('assistant') ? 'AI' : 'System';
            const content = msg.querySelector('.message-content').textContent;
            return `${type}: ${content}`;
        }).join('\n\n');

        const blob = new Blob([messages], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tariffai-chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // HTS Lookup functionality
    async searchHTS() {
        const query = this.htsSearchInput.value.trim();
        if (!query) return;

        this.showLoading('Searching HTS database...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/hts/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    category: this.categoryFilter.value,
                    rate_filter: this.rateFilter.value
                })
            });

            const data = await response.json();
            this.displayHTSResults(data);
        } catch (error) {
            console.error('HTS search error:', error);
            this.htsResults.innerHTML = '<p class="error">Error searching HTS database. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    displayHTSResults(data) {
        if (!data.success || !data.data || !data.data.results || data.data.results.length === 0) {
            this.htsResults.innerHTML = '<p>No HTS codes found for your search.</p>';
            return;
        }

        const results = data.data.results;
        const resultsHtml = results.map((result, index) => `
            <div class="result-card hts-result">
                <div class="result-header">
                    <h4>${result.hts_code}</h4>
                    <button class="info-btn" onclick="app.showHTSDetails(${index})" title="View Details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
                <div class="result-item">
                    <span class="result-label">Description:</span>
                    <span class="result-value">${result.description}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Rate:</span>
                    <span class="result-value rate-badge ${result.rate_type.toLowerCase().replace(' ', '-')}">${result.rate_display}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Type:</span>
                    <span class="result-value">${result.rate_type}</span>
                </div>
                <div class="result-details" id="details-${index}" style="display: none;">
                    <div class="details-grid">
                        <div class="detail-item">
                            <span class="detail-label">Raw HTS Code:</span>
                            <span class="detail-value">${result.raw_hts_code}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">General Rate:</span>
                            <span class="detail-value">${result.general_rate}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Specific Rate:</span>
                            <span class="detail-value">$${result.specific_rate.toFixed(2)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Other Rate:</span>
                            <span class="detail-value">$${result.other_rate.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        this.htsResults.innerHTML = `
            <div class="results-header">
                <h3>Found ${results.length} HTS codes for "${data.data.query}"</h3>
            </div>
            ${resultsHtml}
        `;
    }

    showHTSDetails(index) {
        const detailsElement = document.getElementById(`details-${index}`);
        const infoBtn = detailsElement.previousElementSibling.querySelector('.info-btn');
        
        if (detailsElement.style.display === 'none') {
            detailsElement.style.display = 'block';
            infoBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
            infoBtn.title = 'Hide Details';
        } else {
            detailsElement.style.display = 'none';
            infoBtn.innerHTML = '<i class="fas fa-info-circle"></i>';
            infoBtn.title = 'View Details';
        }
    }

    // Tariff Calculator functionality
    async calculateTariff() {
        const htsCode = this.calcHtsCode.value.trim();
        const value = parseFloat(this.calcValue.value);
        const quantity = parseInt(this.calcQuantity.value) || 1;
        const country = this.calcCountry.value;

        if (!htsCode || !value) {
            this.calcResults.innerHTML = '<p class="error">Please enter HTS code and value.</p>';
            return;
        }

        this.showLoading('Calculating tariff...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/tariff/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    hts_code: htsCode,
                    value: value,
                    quantity: quantity,
                    country: country
                })
            });

            const data = await response.json();
            this.displayCalculationResults(data);
        } catch (error) {
            console.error('Calculation error:', error);
            this.calcResults.innerHTML = '<p class="error">Error calculating tariff. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    displayCalculationResults(data) {
        if (!data.success) {
            this.calcResults.innerHTML = '<p class="error">Calculation failed. Please check your inputs.</p>';
            return;
        }

        const calc = data.calculation;
        this.calcResults.innerHTML = `
            <div class="result-card">
                <h4>Tariff Calculation Results</h4>
                <div class="result-item">
                    <span class="result-label">Product Value:</span>
                    <span class="result-value">$${calc.product_value.toFixed(2)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Tariff Rate:</span>
                    <span class="result-value">${(calc.tariff_rate * 100).toFixed(2)}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Duty Amount:</span>
                    <span class="result-value">$${calc.tariff_amount.toFixed(2)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Brokerage:</span>
                    <span class="result-value">$${calc.additional_costs.brokerage.toFixed(2)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Handling:</span>
                    <span class="result-value">$${calc.additional_costs.handling.toFixed(2)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Transport:</span>
                    <span class="result-value">$${calc.additional_costs.transport.toFixed(2)}</span>
                </div>
                <div class="result-item" style="border-top: 2px solid #667eea; padding-top: 10px; font-weight: bold;">
                    <span class="result-label">Total Cost:</span>
                    <span class="result-value">$${calc.total_cost.toFixed(2)}</span>
                </div>
            </div>
        `;
    }

    // Risk Assessment functionality
    async assessRisk() {
        const input = this.riskInput.value.trim();
        if (!input) return;

        this.showLoading('Assessing risk...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/risk/assess`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: input
                })
            });

            const data = await response.json();
            this.displayRiskResults(data);
        } catch (error) {
            console.error('Risk assessment error:', error);
            this.riskResults.innerHTML = '<p class="error">Error assessing risk. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    displayRiskResults(data) {
        if (!data.success) {
            this.riskResults.innerHTML = '<p class="error">Risk assessment failed.</p>';
            return;
        }

        const risk = data.risk_assessment;
        this.riskResults.innerHTML = `
            <div class="result-card">
                <h4>Risk Assessment Results</h4>
                <div class="result-item">
                    <span class="result-label">Risk Level:</span>
                    <span class="result-value" style="color: ${risk.risk_level === 'HIGH' ? '#e53e3e' : risk.risk_level === 'MEDIUM' ? '#d69e2e' : '#48bb78'}">${risk.risk_level}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Restrictions:</span>
                    <span class="result-value">${risk.restrictions.description}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Licenses Required:</span>
                    <span class="result-value">${risk.requirements.licenses_required ? 'Yes' : 'No'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Certificates Required:</span>
                    <span class="result-value">${risk.requirements.certificates_required ? 'Yes' : 'No'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Inspections Required:</span>
                    <span class="result-value">${risk.requirements.inspections_required ? 'Yes' : 'No'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Recommendations:</span>
                    <span class="result-value">
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            ${risk.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </span>
                </div>
            </div>
        `;
    }

    // Enhanced Scenario Analysis functionality
    async createScenario() {
        const data = {
            product_description: this.scenarioProductDesc.value.trim(),
            hts_code: this.scenarioHtsCode.value.trim(),
            base_value: parseFloat(this.scenarioBaseValue.value),
            quantity: parseInt(this.scenarioQuantity.value),
            origin_country: this.scenarioOriginCountry.value,
            destination_country: this.scenarioDestCountry.value,
            currency: this.scenarioCurrency.value,
            shipping_cost: parseFloat(this.scenarioShippingCost.value) || 0,
            insurance_cost: parseFloat(this.scenarioInsuranceCost.value) || 0,
            additional_costs: parseFloat(this.scenarioAdditionalCosts.value) || 0
        };

        if (!data.product_description || !data.base_value || !data.origin_country) {
            this.scenarioResults.innerHTML = '<p class="error">Please fill in all required fields (Product Description, Base Value, Origin Country).</p>';
            return;
        }

        this.showLoading('Creating scenario...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            this.displayScenarioResults(result);
            this.loadScenarios(); // Refresh scenario list
        } catch (error) {
            console.error('Scenario creation error:', error);
            this.scenarioResults.innerHTML = '<p class="error">Error creating scenario. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    async quickAnalysis() {
        const data = {
            product_description: this.scenarioProductDesc.value.trim(),
            hts_code: this.scenarioHtsCode.value.trim(),
            base_value: parseFloat(this.scenarioBaseValue.value),
            quantity: parseInt(this.scenarioQuantity.value),
            origin_country: this.scenarioOriginCountry.value,
            destination_country: this.scenarioDestCountry.value,
            currency: this.scenarioCurrency.value,
            shipping_cost: parseFloat(this.scenarioShippingCost.value) || 0,
            insurance_cost: parseFloat(this.scenarioInsuranceCost.value) || 0,
            additional_costs: parseFloat(this.scenarioAdditionalCosts.value) || 0
        };

        if (!data.product_description || !data.base_value || !data.origin_country) {
            this.scenarioResults.innerHTML = '<p class="error">Please fill in all required fields for quick analysis.</p>';
            return;
        }

        this.showLoading('Performing quick analysis...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/analyze-quick`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            this.displayQuickAnalysisResults(result);
        } catch (error) {
            console.error('Quick analysis error:', error);
            this.scenarioResults.innerHTML = '<p class="error">Error performing quick analysis. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    async loadScenarios() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/list`);
            const data = await response.json();
            
            if (data.success) {
                this.displayScenarioList(data.data.scenarios);
            }
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }

    displayScenarioList(scenarios) {
        const scenarioList = document.getElementById('scenarioList');
        const scenarioSelect = document.getElementById('scenarioSelect1');
        
        if (scenarios.length === 0) {
            scenarioList.innerHTML = '<p>No scenarios created yet.</p>';
            scenarioSelect.innerHTML = '<option value="">No scenarios available</option>';
            return;
        }

        // Update scenario list
        scenarioList.innerHTML = scenarios.map(scenario => `
            <div class="scenario-item">
                <div class="scenario-info">
                    <strong>${scenario.product_description}</strong>
                    <span>HTS: ${scenario.hts_code || 'N/A'}</span>
                    <span>Value: $${scenario.base_value.toFixed(2)}</span>
                    <span>Origin: ${scenario.origin_country}</span>
                </div>
                <div class="scenario-actions">
                    <button class="btn btn-sm" onclick="app.viewScenario('${scenario.scenario_id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm" onclick="app.deleteScenario('${scenario.scenario_id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');

        // Update scenario select for comparison
        scenarioSelect.innerHTML = scenarios.map(scenario => 
            `<option value="${scenario.scenario_id}">${scenario.product_description} - ${scenario.origin_country}</option>`
        ).join('');
    }

    async compareScenarios() {
        const selectedScenarios = Array.from(document.getElementById('scenarioSelect1').selectedOptions)
            .map(option => option.value);

        if (selectedScenarios.length < 2) {
            this.scenarioResults.innerHTML = '<p class="error">Please select at least 2 scenarios to compare.</p>';
            return;
        }

        this.showLoading('Comparing scenarios...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/compare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    scenario_ids: selectedScenarios
                })
            });

            const result = await response.json();
            this.displayComparisonResults(result);
        } catch (error) {
            console.error('Scenario comparison error:', error);
            this.scenarioResults.innerHTML = '<p class="error">Error comparing scenarios. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    displayScenarioResults(data) {
        if (!data.success) {
            this.scenarioResults.innerHTML = '<p class="error">Scenario creation failed.</p>';
            return;
        }

        const scenario = data.data;
        const analysis = data.analysis;
        
        this.scenarioResults.innerHTML = `
            <div class="result-card">
                <h4>Scenario Created Successfully</h4>
                <div class="scenario-details">
                    <h5>Scenario Details</h5>
                    <div class="result-item">
                        <span class="result-label">Product:</span>
                        <span class="result-value">${scenario.product_description}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">HTS Code:</span>
                        <span class="result-value">${scenario.hts_code || 'N/A'}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Origin:</span>
                        <span class="result-value">${scenario.origin_country}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Base Value:</span>
                        <span class="result-value">$${scenario.base_value.toFixed(2)}</span>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <h5>Analysis Results</h5>
                    <div class="result-item">
                        <span class="result-label">Tariff Rate:</span>
                        <span class="result-value">${analysis.tariff_rate.toFixed(2)}%</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Duty Amount:</span>
                        <span class="result-value">$${analysis.duty_amount.toFixed(2)}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Total Cost:</span>
                        <span class="result-value" style="font-weight: bold;">$${analysis.total_cost.toFixed(2)}</span>
                    </div>
                </div>

                ${analysis.recommendations.length > 0 ? `
                <div class="recommendations">
                    <h5>Recommendations</h5>
                    <ul>
                        ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                ${analysis.risks.length > 0 ? `
                <div class="risks">
                    <h5>Risks</h5>
                    <ul>
                        ${analysis.risks.map(risk => `<li>${risk}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                ${analysis.opportunities.length > 0 ? `
                <div class="opportunities">
                    <h5>Opportunities</h5>
                    <ul>
                        ${analysis.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;
    }

    displayQuickAnalysisResults(data) {
        if (!data.success) {
            this.scenarioResults.innerHTML = '<p class="error">Quick analysis failed.</p>';
            return;
        }

        const scenario = data.data.scenario;
        const analysis = data.data.analysis;
        
        this.scenarioResults.innerHTML = `
            <div class="result-card">
                <h4>Quick Analysis Results</h4>
                <div class="result-item">
                    <span class="result-label">Product:</span>
                    <span class="result-value">${scenario.product_description}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Tariff Rate:</span>
                    <span class="result-value">${analysis.tariff_rate.toFixed(2)}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Duty Amount:</span>
                    <span class="result-value">$${analysis.duty_amount.toFixed(2)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Total Cost:</span>
                    <span class="result-value" style="font-weight: bold;">$${analysis.total_cost.toFixed(2)}</span>
                </div>
                
                ${analysis.recommendations.length > 0 ? `
                <div class="result-item">
                    <span class="result-label">Recommendations:</span>
                    <span class="result-value">
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </span>
                </div>
                ` : ''}
            </div>
        `;
    }

    displayComparisonResults(data) {
        if (!data.success) {
            this.scenarioResults.innerHTML = '<p class="error">Scenario comparison failed.</p>';
            return;
        }

        const comparisons = data.data.comparisons;
        const bestOption = data.data.best_option;
        const savings = data.data.cost_savings;
        
        this.scenarioResults.innerHTML = `
            <div class="result-card">
                <h4>Scenario Comparison Results</h4>
                
                <div class="comparison-summary">
                    <h5>Best Option</h5>
                    <div class="result-item">
                        <span class="result-label">Product:</span>
                        <span class="result-value">${bestOption.data.product_description}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Origin:</span>
                        <span class="result-value">${bestOption.data.origin_country}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Total Cost:</span>
                        <span class="result-value" style="color: #48bb78; font-weight: bold;">$${bestOption.analysis.total_cost.toFixed(2)}</span>
                    </div>
                </div>

                <div class="comparison-details">
                    <h5>All Scenarios</h5>
                    ${comparisons.map((comp, index) => `
                        <div class="scenario-comparison-item">
                            <div class="result-item">
                                <span class="result-label">${index + 1}. ${comp.data.product_description}</span>
                                <span class="result-value">$${comp.analysis.total_cost.toFixed(2)}</span>
                            </div>
                            <div class="result-item">
                                <span class="result-label">Origin:</span>
                                <span class="result-value">${comp.data.origin_country}</span>
                            </div>
                            ${savings[comp.scenario_id] ? `
                            <div class="result-item">
                                <span class="result-label">Savings vs Best:</span>
                                <span class="result-value" style="color: #e53e3e;">+$${savings[comp.scenario_id].toFixed(2)}</span>
                            </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async viewScenario(scenarioId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/${scenarioId}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayScenarioResults(data);
            } else {
                this.scenarioResults.innerHTML = '<p class="error">Failed to load scenario.</p>';
            }
        } catch (error) {
            console.error('Error viewing scenario:', error);
            this.scenarioResults.innerHTML = '<p class="error">Error loading scenario.</p>';
        }
    }

    async deleteScenario(scenarioId) {
        if (!confirm('Are you sure you want to delete this scenario?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/scenario/${scenarioId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            
            if (data.success) {
                this.loadScenarios(); // Refresh the list
                this.scenarioResults.innerHTML = '<p class="success">Scenario deleted successfully.</p>';
            } else {
                this.scenarioResults.innerHTML = '<p class="error">Failed to delete scenario.</p>';
            }
        } catch (error) {
            console.error('Error deleting scenario:', error);
            this.scenarioResults.innerHTML = '<p class="error">Error deleting scenario.</p>';
        }
    }

    // Data Ingestion functionality
    async ingestData() {
        const docType = this.docType.value;
        const title = this.docTitle.value.trim();
        const content = this.docContent.value.trim();

        if (!title || !content) {
            this.ingestionStatus.innerHTML = '<p class="error">Please enter document title and content.</p>';
            return;
        }

        this.showLoading('Ingesting data...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/data/ingest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    doc_type: docType,
                    title: title,
                    content: content
                })
            });

            const data = await response.json();
            this.displayIngestionStatus(data);
        } catch (error) {
            console.error('Data ingestion error:', error);
            this.ingestionStatus.innerHTML = '<p class="error">Error ingesting data. Please try again.</p>';
        } finally {
            this.hideLoading();
        }
    }

    displayIngestionStatus(data) {
        if (data.success) {
            this.ingestionStatus.innerHTML = `
                <div class="result-card">
                    <h4>Data Ingestion Successful</h4>
                    <div class="result-item">
                        <span class="result-label">Document:</span>
                        <span class="result-value">${data.title}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Type:</span>
                        <span class="result-value">${data.doc_type}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Status:</span>
                        <span class="result-value" style="color: #48bb78;">Successfully added to knowledge base</span>
                    </div>
                </div>
            `;
            
            // Clear form
            this.docTitle.value = '';
            this.docContent.value = '';
        } else {
            this.ingestionStatus.innerHTML = '<p class="error">Data ingestion failed. Please try again.</p>';
        }
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.docContent.value = e.target.result;
            this.docTitle.value = file.name;
        };
        reader.readAsText(file);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TariffAI();
}); 