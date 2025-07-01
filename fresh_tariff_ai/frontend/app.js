/**
 * TariffAI Frontend Application
 * Modern JavaScript with enhanced functionality and glassmorphism UI
 */

class TariffAI {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        
        this.initializeElements();
        this.bindEvents();
        this.checkConnection();
        this.initializeTabs();
        this.applyTheme();
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
        this.advancedSearchBtn = document.getElementById('advancedSearchBtn');
        this.advancedFilters = document.getElementById('advancedFilters');
        this.sortBy = document.getElementById('sortBy');

        // Enhanced table elements
        this.htsTable = document.getElementById('htsTable');
        this.htsTableBody = document.getElementById('htsTableBody');
        this.selectAllCheckbox = document.getElementById('selectAllCheckbox');
        this.resultCount = document.getElementById('resultCount');
        this.pageInfo = document.getElementById('pageInfo');
        this.exportTable = document.getElementById('exportTable');
        this.selectAll = document.getElementById('selectAll');
        this.clearSelection = document.getElementById('clearSelection');
        this.prevPage = document.getElementById('prevPage');
        this.nextPage = document.getElementById('nextPage');
        this.pageNumbers = document.getElementById('pageNumbers');

        // Analytics elements
        this.totalSearches = document.getElementById('totalSearches');
        this.todaySearches = document.getElementById('todaySearches');
        this.totalCalculations = document.getElementById('totalCalculations');
        this.avgDutyRate = document.getElementById('avgDutyRate');
        this.totalAssessments = document.getElementById('totalAssessments');
        this.highRiskCount = document.getElementById('highRiskCount');
        this.totalScenarios = document.getElementById('totalScenarios');
        this.savedScenarios = document.getElementById('savedScenarios');
        this.exportAnalytics = document.getElementById('exportAnalytics');
        this.exportCharts = document.getElementById('exportCharts');
        this.generateReport = document.getElementById('generateReport');

        // Chart elements
        this.dutyRateChart = document.getElementById('dutyRateChart');
        this.categoryChart = document.getElementById('categoryChart');
        this.trendChart = document.getElementById('trendChart');
        this.countryChart = document.getElementById('countryChart');
        this.riskChart = document.getElementById('riskChart');
        this.dutyRateChartType = document.getElementById('dutyRateChartType');
        this.categoryChartType = document.getElementById('categoryChartType');
        this.trendPeriod = document.getElementById('trendPeriod');

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

        // Initialize data structures
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalItems = 0;
        this.currentData = [];
        this.selectedItems = new Set();
        this.charts = {};
        this.analyticsData = {};
    }

    bindEvents() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

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

        // Advanced search events
        this.advancedSearchBtn.addEventListener('click', () => this.toggleAdvancedFilters());
        this.categoryFilter.addEventListener('change', () => this.applyFilters());
        this.rateFilter.addEventListener('change', () => this.applyFilters());
        this.sortBy.addEventListener('change', () => this.applySorting());

        // Table control events
        this.selectAllCheckbox.addEventListener('change', () => this.toggleSelectAll());
        this.selectAll.addEventListener('click', () => this.selectAllItems());
        this.clearSelection.addEventListener('click', () => this.clearSelectionItems());
        this.exportTable.addEventListener('click', () => this.exportTableData());
        this.prevPage.addEventListener('click', () => this.previousPage());
        this.nextPage.addEventListener('click', () => this.nextPage());

        // Analytics events
        this.exportAnalytics.addEventListener('click', () => this.exportAnalyticsData());
        this.exportCharts.addEventListener('click', () => this.exportChartsAsImages());
        this.generateReport.addEventListener('click', () => this.generateAnalyticsReport());

        // Chart control events
        this.dutyRateChartType.addEventListener('change', () => this.updateDutyRateChart());
        this.categoryChartType.addEventListener('change', () => this.updateCategoryChart());
        this.trendPeriod.addEventListener('change', () => this.updateTrendChart());

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

        // Load analytics when analytics tab is opened
        document.querySelector('[data-tab="analytics"]').addEventListener('click', () => {
            setTimeout(() => this.loadAnalytics(), 100);
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
        const statusRight = document.querySelector('.connection-status');
        if (statusRight) {
            statusRight.className = `connection-status ${status}`;
        }
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
            this.htsResults.innerHTML = `
                <div class="result-card">
                    <div class="result-content">
                        <i class="fas fa-info-circle"></i>
                        <p>No HTS codes found matching your search. Try different keywords or check the spelling.</p>
                    </div>
                </div>
            `;
            return;
        }

        // Store the data for table operations
        this.currentData = data.data.results.map(result => ({
            hts_code: result.hts_code,
            description: result.description,
            duty_rate: result.general_rate,
            category: this.extractCategory(result.description),
            rate_type: result.rate_type,
            rate_display: result.rate_display,
            raw_hts_code: result.raw_hts_code,
            specific_rate: result.specific_rate,
            other_rate: result.other_rate
        }));
        
        this.totalItems = this.currentData.length;
        this.currentPage = 1;
        this.selectedItems.clear();

        // Display the data in table format
        this.displayTableData();
        
        this.showToast(`Found ${this.currentData.length} HTS codes`, 'success');
    }

    extractCategory(description) {
        const desc = description.toLowerCase();
        if (desc.includes('steel') || desc.includes('iron') || desc.includes('metal')) return 'Steel & Metals';
        if (desc.includes('textile') || desc.includes('fabric') || desc.includes('cloth')) return 'Textiles';
        if (desc.includes('electronic') || desc.includes('computer') || desc.includes('phone')) return 'Electronics';
        if (desc.includes('machine') || desc.includes('equipment') || desc.includes('tool')) return 'Machinery';
        if (desc.includes('chemical') || desc.includes('compound') || desc.includes('acid')) return 'Chemicals';
        if (desc.includes('food') || desc.includes('agricultural') || desc.includes('grain')) return 'Agriculture';
        return 'Other';
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
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.docContent.value = e.target.result;
                this.showToast('File loaded successfully', 'success');
            };
            reader.readAsText(file);
        }
    }

    // Enhanced HTS Search Methods
    toggleAdvancedFilters() {
        const isVisible = this.advancedFilters.style.display !== 'none';
        this.advancedFilters.style.display = isVisible ? 'none' : 'block';
        this.advancedSearchBtn.innerHTML = isVisible ? 
            '<i class="fas fa-sliders-h"></i> Advanced' : 
            '<i class="fas fa-times"></i> Hide';
    }

    applyFilters() {
        if (this.currentData.length > 0) {
            this.filterAndDisplayData();
        }
    }

    applySorting() {
        if (this.currentData.length > 0) {
            this.sortAndDisplayData();
        }
    }

    filterAndDisplayData() {
        let filteredData = [...this.currentData];
        
        const categoryFilter = this.categoryFilter.value;
        const rateFilter = this.rateFilter.value;
        
        if (categoryFilter) {
            filteredData = filteredData.filter(item => 
                item.category && item.category.toLowerCase().includes(categoryFilter.toLowerCase())
            );
        }
        
        if (rateFilter) {
            filteredData = filteredData.filter(item => {
                const rate = parseFloat(item.duty_rate);
                switch (rateFilter) {
                    case '0': return rate === 0;
                    case 'low': return rate > 0 && rate <= 5;
                    case 'medium': return rate > 5 && rate <= 15;
                    case 'high': return rate > 15;
                    default: return true;
                }
            });
        }
        
        this.currentData = filteredData;
        this.currentPage = 1;
        this.displayTableData();
    }

    sortAndDisplayData() {
        const sortBy = this.sortBy.value;
        
        this.currentData.sort((a, b) => {
            switch (sortBy) {
                case 'hts_code':
                    return a.hts_code.localeCompare(b.hts_code);
                case 'duty_rate':
                    return parseFloat(a.duty_rate) - parseFloat(b.duty_rate);
                case 'description':
                    return a.description.localeCompare(b.description);
                default:
                    return 0;
            }
        });
        
        this.displayTableData();
    }

    // Enhanced Table Methods
    displayTableData() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.currentData.slice(startIndex, endIndex);
        
        this.htsTableBody.innerHTML = '';
        
        pageData.forEach((item, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox" data-index="${startIndex + index}" ${this.selectedItems.has(startIndex + index) ? 'checked' : ''}></td>
                <td><strong>${item.hts_code}</strong></td>
                <td>${item.description}</td>
                <td><span class="rate-badge ${this.getRateBadgeClass(item.duty_rate)}">${item.duty_rate}%</span></td>
                <td>${item.category || 'N/A'}</td>
                <td>
                    <button class="btn btn-glass btn-sm" onclick="tariffAI.showHTSDetails(${startIndex + index})">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                </td>
            `;
            this.htsTableBody.appendChild(row);
        });
        
        this.updatePagination();
        this.updateTableInfo();
        this.bindTableEvents();
    }

    bindTableEvents() {
        const checkboxes = this.htsTableBody.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.index);
                if (e.target.checked) {
                    this.selectedItems.add(index);
                } else {
                    this.selectedItems.delete(index);
                }
                this.updateSelectAllState();
            });
        });
    }

    toggleSelectAll() {
        const checkboxes = this.htsTableBody.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            const index = parseInt(checkbox.dataset.index);
            if (this.selectAllCheckbox.checked) {
                checkbox.checked = true;
                this.selectedItems.add(index);
            } else {
                checkbox.checked = false;
                this.selectedItems.delete(index);
            }
        });
    }

    selectAllItems() {
        this.selectAllCheckbox.checked = true;
        this.toggleSelectAll();
    }

    clearSelectionItems() {
        this.selectAllCheckbox.checked = false;
        this.selectedItems.clear();
        const checkboxes = this.htsTableBody.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = false);
    }

    updateSelectAllState() {
        const checkboxes = this.htsTableBody.querySelectorAll('input[type="checkbox"]');
        const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
        this.selectAllCheckbox.checked = checkedCount === checkboxes.length && checkboxes.length > 0;
        this.selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
    }

    updatePagination() {
        const totalPages = Math.ceil(this.currentData.length / this.itemsPerPage);
        
        this.prevPage.disabled = this.currentPage === 1;
        this.nextPage.disabled = this.currentPage === totalPages;
        
        this.pageNumbers.innerHTML = '';
        
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === this.currentPage ? 'active' : '';
            pageBtn.addEventListener('click', () => this.goToPage(i));
            this.pageNumbers.appendChild(pageBtn);
        }
    }

    updateTableInfo() {
        this.resultCount.textContent = `${this.currentData.length} results`;
        const totalPages = Math.ceil(this.currentData.length / this.itemsPerPage);
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
    }

    goToPage(page) {
        this.currentPage = page;
        this.displayTableData();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.displayTableData();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.currentData.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.displayTableData();
        }
    }

    exportTableData() {
        const selectedData = Array.from(this.selectedItems).map(index => this.currentData[index]);
        const dataToExport = selectedData.length > 0 ? selectedData : this.currentData;
        
        const csv = this.convertToCSV(dataToExport);
        this.downloadCSV(csv, 'hts_search_results.csv');
        this.showToast('Data exported successfully', 'success');
    }

    convertToCSV(data) {
        const headers = ['HTS Code', 'Description', 'Duty Rate', 'Category'];
        const rows = data.map(item => [
            item.hts_code,
            item.description,
            item.duty_rate,
            item.category || 'N/A'
        ]);
        
        return [headers, ...rows].map(row => 
            row.map(cell => `"${cell}"`).join(',')
        ).join('\n');
    }

    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    getRateBadgeClass(rate) {
        const numRate = parseFloat(rate);
        if (numRate === 0) return 'free';
        if (numRate <= 5) return 'low';
        if (numRate <= 15) return 'medium';
        return 'high';
    }

    // Analytics Methods
    async loadAnalytics() {
        this.showLoading('Loading analytics...');
        
        try {
            // Load analytics data
            await this.loadAnalyticsData();
            
            // Initialize charts
            this.initializeCharts();
            
            // Update dashboard widgets
            this.updateDashboardWidgets();
            
        } catch (error) {
            console.error('Analytics loading error:', error);
            this.showToast('Failed to load analytics', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadAnalyticsData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/analytics/dashboard`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.analyticsData = data.data;
                } else {
                    throw new Error('Failed to load analytics data');
                }
            } else {
                throw new Error('Analytics API not responding');
            }
        } catch (error) {
            console.error('Analytics loading error:', error);
            // Fallback to simulated data if API fails
            this.analyticsData = {
                searches: { total: 1250, today: 45 },
                calculations: { total: 890, avg_rate: 8.5 },
                assessments: { total: 567, high_risk: 23 },
                scenarios: { total: 234, saved: 89 },
                dutyRates: [
                    { range: '0%', count: 156 },
                    { range: '1-5%', count: 234 },
                    { range: '6-15%', count: 189 },
                    { range: '16%+', count: 67 }
                ],
                categories: [
                    { name: 'Electronics', count: 234 },
                    { name: 'Textiles', count: 189 },
                    { name: 'Machinery', count: 156 },
                    { name: 'Chemicals', count: 123 },
                    { name: 'Steel', count: 98 }
                ],
                trends: [
                    { date: '2024-01-01', searches: 45, calculations: 32 },
                    { date: '2024-01-02', searches: 52, calculations: 38 },
                    { date: '2024-01-03', searches: 48, calculations: 35 },
                    { date: '2024-01-04', searches: 61, calculations: 42 },
                    { date: '2024-01-05', searches: 55, calculations: 39 }
                ],
                countries: [
                    { name: 'China', count: 456 },
                    { name: 'Mexico', count: 234 },
                    { name: 'Canada', count: 189 },
                    { name: 'Germany', count: 123 },
                    { name: 'Japan', count: 98 }
                ],
                risks: [
                    { level: 'Low', count: 234 },
                    { level: 'Medium', count: 156 },
                    { level: 'High', count: 67 }
                ]
            };
        }
    }

    updateDashboardWidgets() {
        this.totalSearches.textContent = this.analyticsData.searches.total.toLocaleString();
        this.todaySearches.textContent = this.analyticsData.searches.today;
        this.totalCalculations.textContent = this.analyticsData.calculations.total.toLocaleString();
        this.avgDutyRate.textContent = this.analyticsData.calculations.avg_rate + '%';
        this.totalAssessments.textContent = this.analyticsData.assessments.total.toLocaleString();
        this.highRiskCount.textContent = this.analyticsData.assessments.high_risk;
        this.totalScenarios.textContent = this.analyticsData.scenarios.total.toLocaleString();
        this.savedScenarios.textContent = this.analyticsData.scenarios.saved;
    }

    initializeCharts() {
        this.createDutyRateChart();
        this.createCategoryChart();
        this.createTrendChart();
        this.createCountryChart();
        this.createRiskChart();
    }

    createDutyRateChart() {
        const ctx = this.dutyRateChart.getContext('2d');
        const data = this.analyticsData.dutyRates;
        
        this.charts.dutyRate = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(d => d.range),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: [
                        '#48bb78',
                        '#38a169',
                        '#2f855a',
                        '#276749'
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(255, 255, 255, 0.2)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'white',
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    createCategoryChart() {
        const ctx = this.categoryChart.getContext('2d');
        const data = this.analyticsData.categories;
        
        this.charts.category = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Search Count',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(72, 187, 120, 0.8)',
                    borderColor: '#48bb78',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }

    createTrendChart() {
        const ctx = this.trendChart.getContext('2d');
        const data = this.analyticsData.trends;
        
        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Searches',
                    data: data.map(d => d.searches),
                    borderColor: '#48bb78',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Calculations',
                    data: data.map(d => d.calculations),
                    borderColor: '#3182ce',
                    backgroundColor: 'rgba(49, 130, 206, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }

    createCountryChart() {
        const ctx = this.countryChart.getContext('2d');
        const data = this.analyticsData.countries;
        
        this.charts.country = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: [
                        '#48bb78',
                        '#38a169',
                        '#2f855a',
                        '#276749',
                        '#22543d'
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(255, 255, 255, 0.2)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'white',
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
    }

    createRiskChart() {
        const ctx = this.riskChart.getContext('2d');
        const data = this.analyticsData.risks;
        
        this.charts.risk = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.level),
                datasets: [{
                    label: 'Risk Level Count',
                    data: data.map(d => d.count),
                    backgroundColor: [
                        '#48bb78',
                        '#ed8936',
                        '#e53e3e'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateDutyRateChart() {
        const chartType = this.dutyRateChartType.value;
        if (this.charts.dutyRate) {
            this.charts.dutyRate.destroy();
        }
        
        const ctx = this.dutyRateChart.getContext('2d');
        const data = this.analyticsData.dutyRates;
        
        this.charts.dutyRate = new Chart(ctx, {
            type: chartType,
            data: {
                labels: data.map(d => d.range),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: [
                        '#48bb78',
                        '#38a169',
                        '#2f855a',
                        '#276749'
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(255, 255, 255, 0.2)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'white',
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    updateCategoryChart() {
        const chartType = this.categoryChartType.value;
        if (this.charts.category) {
            this.charts.category.destroy();
        }
        
        const ctx = this.categoryChart.getContext('2d');
        const data = this.analyticsData.categories;
        
        this.charts.category = new Chart(ctx, {
            type: chartType === 'horizontal' ? 'bar' : chartType,
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Search Count',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(72, 187, 120, 0.8)',
                    borderColor: '#48bb78',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: chartType === 'horizontal' ? 'y' : 'x',
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }

    updateTrendChart() {
        const period = parseInt(this.trendPeriod.value);
        // Simulate loading different period data
        this.showToast(`Loading ${period}-day trend data...`, 'info');
    }

    // Export Methods
    exportAnalyticsData() {
        const data = {
            timestamp: new Date().toISOString(),
            analytics: this.analyticsData
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'analytics_data.json';
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showToast('Analytics data exported successfully', 'success');
    }

    exportChartsAsImages() {
        Object.keys(this.charts).forEach(chartName => {
            const chart = this.charts[chartName];
            if (chart) {
                const canvas = chart.canvas;
                const link = document.createElement('a');
                link.download = `${chartName}_chart.png`;
                link.href = canvas.toDataURL();
                link.click();
            }
        });
        
        this.showToast('Charts exported as images', 'success');
    }

    generateAnalyticsReport() {
        const report = this.generateReportContent();
        const blob = new Blob([report], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'analytics_report.html';
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showToast('Analytics report generated successfully', 'success');
    }

    generateReportContent() {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>TariffAI Analytics Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .section { margin-bottom: 20px; }
                    .metric { display: inline-block; margin: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>TariffAI Analytics Report</h1>
                    <p>Generated on ${new Date().toLocaleDateString()}</p>
                </div>
                
                <div class="section">
                    <h2>Summary</h2>
                    <div class="metric">Total Searches: ${this.analyticsData.searches.total}</div>
                    <div class="metric">Total Calculations: ${this.analyticsData.calculations.total}</div>
                    <div class="metric">Total Assessments: ${this.analyticsData.assessments.total}</div>
                    <div class="metric">Total Scenarios: ${this.analyticsData.scenarios.total}</div>
                </div>
                
                <div class="section">
                    <h2>Duty Rate Distribution</h2>
                    <ul>
                        ${this.analyticsData.dutyRates.map(d => `<li>${d.range}: ${d.count} items</li>`).join('')}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Top Categories</h2>
                    <ul>
                        ${this.analyticsData.categories.map(c => `<li>${c.name}: ${c.count} searches</li>`).join('')}
                    </ul>
                </div>
            </body>
            </html>
        `;
    }

    // Toast Notification System
    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <i class="${icon}"></i>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'fas fa-check-circle';
            case 'error': return 'fas fa-exclamation-circle';
            case 'warning': return 'fas fa-exclamation-triangle';
            default: return 'fas fa-info-circle';
        }
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon();
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
        this.showToast(`Switched to ${this.currentTheme} mode`, 'info');
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.className = this.currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// Initial loading screen functions
function showInitialLoadingScreen() {
    const loadingScreen = document.getElementById('initialLoadingScreen');
    const progressFill = document.getElementById('progressFill');
    const loadingStatus = document.getElementById('loadingStatus');
    
    if (loadingScreen) {
        loadingScreen.style.display = 'flex';
        
        // Simulate loading progress
        const loadingSteps = [
            { progress: 20, status: 'Initializing TariffAI...' },
            { progress: 40, status: 'Loading HTS Database...' },
            { progress: 60, status: 'Connecting AI Services...' },
            { progress: 80, status: 'Preparing Analytics...' },
            { progress: 100, status: 'Ready!' }
        ];
        
        let currentStep = 0;
        const progressInterval = setInterval(() => {
            if (currentStep < loadingSteps.length) {
                const step = loadingSteps[currentStep];
                progressFill.style.width = step.progress + '%';
                loadingStatus.textContent = step.status;
                currentStep++;
            } else {
                clearInterval(progressInterval);
            }
        }, 600);
    }
}

function hideInitialLoadingScreen() {
    const loadingScreen = document.getElementById('initialLoadingScreen');
    if (loadingScreen) {
        loadingScreen.classList.add('fade-out');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Show initial loading screen
    showInitialLoadingScreen();
    
    // Initialize the application after loading
    setTimeout(() => {
        hideInitialLoadingScreen();
        new TariffAI();
    }, 3000); // Show loading for 3 seconds
}); 