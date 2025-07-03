import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const chatService = {
  /**
   * Send a message to the chat API
   * @param {string} message - The message to send
   * @param {string} sessionId - Optional session ID
   * @returns {Promise<Object>} The response from the API
   */
  async sendMessage(message, sessionId = null) {
    try {
      const response = await api.post('/api/v1/chat/', {
        message,
        session_id: sessionId,
      });

      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        throw new Error(error.response.data?.message || 'Server error');
      } else if (error.request) {
        // Network error
        throw new Error('Network error - please check your connection');
      } else {
        // Other error
        throw new Error(error.message || 'Unknown error');
      }
    }
  },

  /**
   * Get session information
   * @param {string} sessionId - The session ID
   * @returns {Promise<Object>} Session information
   */
  async getSessionInfo(sessionId) {
    try {
      const response = await api.get(`/api/v1/chat/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting session info:', error);
      throw error;
    }
  },

  /**
   * Clear a chat session
   * @param {string} sessionId - The session ID
   * @returns {Promise<Object>} Confirmation
   */
  async clearSession(sessionId) {
    try {
      const response = await api.delete(`/api/v1/chat/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error clearing session:', error);
      throw error;
    }
  },

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },

  /**
   * Check chat service health (ChromaDB and Ollama)
   * @returns {Promise<Object>} Chat service health
   */
  async checkChatHealth() {
    try {
      const response = await api.get('/api/v1/chat/health');
      return response.data;
    } catch (error) {
      console.error('Error checking chat health:', error);
      throw error;
    }
  },
};

export default chatService; 