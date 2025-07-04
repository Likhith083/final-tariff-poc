import axios from 'axios';
import logger from '../utils/logger';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    logger.apiRequest('APIService', config.url, config.method, config.data);
    return config;
  },
  (error) => {
    logger.error('APIService', 'Request interceptor error', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
apiClient.interceptors.response.use(
  (response) => {
    logger.apiResponse('APIService', response.config.url, response.status, response.data);
    return response;
  },
  (error) => {
    const status = error.response?.status || 'NETWORK_ERROR';
    const url = error.config?.url || 'UNKNOWN_ENDPOINT';
    logger.apiResponse('APIService', url, status, error.response?.data);
    return Promise.reject(error);
  }
);

// API Service Class
class ApiService {
  constructor() {
    logger.info('APIService', 'API Service initialized', { baseURL: API_BASE_URL });
  }

  // Generic request method with error handling
  async request(method, endpoint, data = null, config = {}) {
    try {
      logger.debug('APIService', `Making ${method} request to ${endpoint}`, { data, config });
      
      const response = await apiClient.request({
        method,
        url: endpoint,
        data,
        ...config,
      });
      
      return response.data;
    } catch (error) {
      logger.error('APIService', `Request failed: ${method} ${endpoint}`, error);
      throw this.handleError(error);
    }
  }

  // Error handler
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      logger.error('APIService', `HTTP Error ${status}`, data);
      
      return {
        type: 'HTTP_ERROR',
        status,
        message: data?.detail || data?.message || `HTTP ${status} error`,
        data,
      };
    } else if (error.request) {
      // Network error
      logger.error('APIService', 'Network error - no response received', error.request);
      
      return {
        type: 'NETWORK_ERROR',
        message: 'Network error - unable to reach server',
        originalError: error,
      };
    } else {
      // Other error
      logger.error('APIService', 'Request setup error', error);
      
      return {
        type: 'REQUEST_ERROR',
        message: error.message || 'Request failed',
        originalError: error,
      };
    }
  }

  // Health check
  async healthCheck() {
    logger.info('APIService', 'Performing health check');
    return this.request('GET', '/health');
  }

  // Chat API
  async sendChatMessage(message, context = {}) {
    logger.info('APIService', 'Sending chat message', { message, context });
    return this.request('POST', '/api/v1/chat', {
      message,
      context,
    });
  }

  // HTS Search API
  async searchHTS(searchData) {
    logger.info('APIService', 'Searching HTS codes', searchData);
    return this.request('POST', '/api/v1/hts/search', searchData);
  }

  async getHTSDetails(htsCode) {
    logger.info('APIService', 'Getting HTS details', { htsCode });
    return this.request('GET', `/api/v1/hts/${htsCode}`);
  }

  // Tariff API
  async calculateTariff(data) {
    logger.info('APIService', 'Calculating tariff', data);
    return this.request('POST', '/api/v1/tariff/calculate', data);
  }

  async getTariffRates(country, htsCode) {
    logger.info('APIService', 'Getting tariff rates', { country, htsCode });
    return this.request('GET', `/api/v1/tariff/rates/${country}/${htsCode}`);
  }

  // Scenario API
  async createScenario(scenarioData) {
    logger.info('APIService', 'Creating scenario', scenarioData);
    return this.request('POST', '/api/v1/scenario', scenarioData);
  }

  async getScenarios(userId = null) {
    logger.info('APIService', 'Getting scenarios', { userId });
    const params = userId ? { user_id: userId } : {};
    return this.request('GET', '/api/v1/scenario', null, { params });
  }

  async runScenario(scenarioId) {
    logger.info('APIService', 'Running scenario', { scenarioId });
    return this.request('POST', `/api/v1/scenario/${scenarioId}/run`);
  }

  // Analytics API
  async getAnalytics(filters = {}) {
    logger.info('APIService', 'Getting analytics', filters);
    return this.request('POST', '/api/v1/analytics', filters);
  }

  async generateReport(reportType, parameters = {}) {
    logger.info('APIService', 'Generating report', { reportType, parameters });
    return this.request('POST', '/api/v1/analytics/report', {
      type: reportType,
      parameters,
    });
  }

  // Risk Assessment API
  async assessRisk(data) {
    logger.info('APIService', 'Assessing risk', data);
    return this.request('POST', '/api/v1/risk/assess', data);
  }

  // Data API
  async uploadData(file, dataType) {
    logger.info('APIService', 'Uploading data', { fileName: file.name, dataType });
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);
    
    return this.request('POST', '/api/v1/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async getDataStatus() {
    logger.info('APIService', 'Getting data status');
    return this.request('GET', '/api/v1/data/status');
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
