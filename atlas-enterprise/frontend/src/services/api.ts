/**
 * API Service for ATLAS Enterprise Frontend
 * Handles all backend API communications
 */

import axios, { AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Add this generic post method after the existing apiClient setup
const post = async (url: string, data: any): Promise<any> => {
  const response = await apiClient.post(url, data)
  return response.data
}

// Types
export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

export interface HTSCode {
  id: number
  hts_code: string
  description: string
  general_rate: number
  special_rate: number | null
  other_rate: number | null
  unit_of_quantity: string
  chapter: string
  heading: string
  subheading: string
  created_at: string
  updated_at: string
}

export interface HTSSearchResponse {
  success: boolean
  message: string
  data: HTSCode[]
  total_results: number
  search_query: string
  search_time_ms: number
}

export interface ChapterSummary {
  chapter_number: string
  description: string
  code_count: number
}

export interface TariffCalculationRequest {
  hts_code: string
  country_code: string
  product_value: number
  quantity: number
  freight_cost: number
  insurance_cost: number
  other_costs: number
  currency: string
}

export interface TariffCalculationResult {
  success: boolean
  hts_code: string
  product_description: string
  country_code: string
  country_name: string
  currency: string
  exchange_rate: number
  product_value_usd: number
  customs_value: number
  duty_rate: number
  duty_amount: number
  mpf_amount: number
  hmf_amount: number
  total_fees: number
  total_landed_cost: number
  calculation_breakdown: {
    product_value: number
    freight_cost: number
    insurance_cost: number
    other_costs: number
    customs_value: number
    duty_calculation: string
    mpf_calculation: string
    hmf_calculation: string
  }
}

export interface SourcingOption {
  country_code: string
  country_name: string
  duty_rate: number
  duty_amount: number
  total_landed_cost: number
  savings: number
  fta_benefits: string | null
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    username: string
    full_name: string
    role: string
    phone?: string
    company?: string
    job_title?: string
    department?: string
    created_at?: string
  }
}

// API Methods
export const api = {
  // Generic methods
  post,
  
  // Auth
  auth: {
    login: async (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
      const response = await apiClient.post('/api/v1/auth/login-json', data)
      return response.data
    },
    register: async (data: any): Promise<ApiResponse<any>> => {
      const response = await apiClient.post('/api/v1/auth/register', data)
      return response.data
    },
    getProfile: async (): Promise<ApiResponse<any>> => {
      const response = await apiClient.get('/api/v1/auth/me')
      return response.data
    },
    updateProfile: async (data: any): Promise<ApiResponse<any>> => {
      const response = await apiClient.put('/api/v1/auth/me', data)
      return response.data
    },
    changePassword: async (data: any): Promise<ApiResponse<any>> => {
      const response = await apiClient.put('/api/v1/auth/change-password', data)
      return response.data
    },
  },

  // Tariff
  tariff: {
    searchHTS: async (query: string, chapter?: string, limit: number = 20): Promise<HTSSearchResponse> => {
      const params = new URLSearchParams({ query, limit: limit.toString() })
      if (chapter) params.append('chapter', chapter)
      const response = await apiClient.get(`/api/v1/tariff/hts/search?${params}`)
      return response.data
    },
    getHTSCode: async (htsCode: string): Promise<ApiResponse<HTSCode>> => {
      const response = await apiClient.get(`/api/v1/tariff/hts/${htsCode}`)
      return response.data
    },
    getChapters: async (): Promise<ApiResponse<ChapterSummary[]>> => {
      const response = await apiClient.get('/api/v1/tariff/chapters')
      return response.data
    },
    calculate: async (data: TariffCalculationRequest): Promise<ApiResponse<TariffCalculationResult>> => {
      const response = await apiClient.post('/api/v1/tariff/calculate', data)
      return response.data
    },
    compareSourcing: async (data: any): Promise<ApiResponse<SourcingOption[]>> => {
      const response = await apiClient.post('/api/v1/tariff/compare-sourcing', data)
      return response.data
    },
    getPopularCodes: async (limit: number = 10): Promise<ApiResponse<HTSCode[]>> => {
      const response = await apiClient.get(`/api/v1/tariff/popular-codes?limit=${limit}`)
      return response.data
    },
  },

  // Data
  data: {
    searchKnowledge: async (query: string, topK: number = 5): Promise<ApiResponse<any>> => {
      const params = new URLSearchParams({ query, top_k: topK.toString() })
      const response = await apiClient.get(`/api/v1/data/knowledge/search?${params}`)
      return response.data
    },
    ingestKnowledge: async (): Promise<ApiResponse<any>> => {
      const response = await apiClient.post('/api/v1/data/knowledge/ingest')
      return response.data
    },
    getDataSummary: async (): Promise<ApiResponse<any>> => {
      const response = await apiClient.get('/api/v1/data/summary')
      return response.data
    },
  },

  // AI
  ai: {
    chat: async (data: {
      messages: Array<{ role: string; content: string }>;
      model: string;
      serp_search?: boolean;
      product_query?: string;
      temperature?: number;
      max_tokens?: number;
    }): Promise<{
      content: string;
      model: string;
      usage?: any;
      product_info?: any;
      error?: string;
    }> => {
      const response = await apiClient.post('/api/v1/ai/chat', data)
      return response.data
    },
  },

  // Health
  health: {
    check: async (): Promise<ApiResponse<any>> => {
      const response = await apiClient.get('/api/v1/health')
      return response.data
    },
    detailed: async (): Promise<ApiResponse<any>> => {
      const response = await apiClient.get('/api/v1/health/detailed')
      return response.data
    },
  },
}

export default api 