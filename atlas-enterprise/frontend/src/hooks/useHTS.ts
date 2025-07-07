import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { HTSCode, HTSSearchResponse, ChapterSummary, TariffCalculationRequest, TariffCalculationResult } from '@/services/api'
import toast from 'react-hot-toast'

// Query keys
const QUERY_KEYS = {
  htsSearch: (query: string, chapter?: string, limit?: number) => ['hts', 'search', query, chapter, limit],
  htsCode: (code: string) => ['hts', 'code', code],
  chapters: ['hts', 'chapters'],
  popularCodes: (limit: number) => ['hts', 'popular', limit],
  calculation: ['tariff', 'calculation'],
}

// Mock data for demo purposes
const mockHTSCodes: HTSCode[] = [
  {
    id: 1,
    hts_code: '8471.30.0100',
    description: 'Portable automatic data processing machines, weighing not more than 10 kg, consisting of at least a central processing unit, a keyboard and a display',
    chapter: '84',
    heading: '8471',
    subheading: '8471.30',
    general_rate: 0,
    special_rate: null,
    other_rate: null,
    unit_of_quantity: 'PCE',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    hts_code: '8517.13.0000',
    description: 'Smartphones, cellular or other wireless networks',
    chapter: '85',
    heading: '8517',
    subheading: '8517.13',
    general_rate: 0,
    special_rate: null,
    other_rate: null,
    unit_of_quantity: 'PCE',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 3,
    hts_code: '9503.00.0000',
    description: 'Other toys; reduced-size (scale) models and similar recreational models, working or not; puzzles of all kinds',
    chapter: '95',
    heading: '9503',
    subheading: '9503.00',
    general_rate: 0,
    special_rate: null,
    other_rate: null,
    unit_of_quantity: 'PCE',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 4,
    hts_code: '6104.43.2010',
    description: 'Women\'s or girls\' dresses, of synthetic fibres, knitted or crocheted',
    chapter: '61',
    heading: '6104',
    subheading: '6104.43',
    general_rate: 16,
    special_rate: null,
    other_rate: null,
    unit_of_quantity: 'PCE',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 5,
    hts_code: '4202.12.2020',
    description: 'Trunks, suitcases, vanity cases, executive-cases, briefcases, school satchels and similar containers, with outer surface of leather or of composition leather',
    chapter: '42',
    heading: '4202',
    subheading: '4202.12',
    general_rate: 8.5,
    special_rate: null,
    other_rate: null,
    unit_of_quantity: 'PCE',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
]

const mockChapters: ChapterSummary[] = [
  { chapter_number: '84', description: 'Nuclear reactors, boilers, machinery and mechanical appliances', code_count: 1500 },
  { chapter_number: '85', description: 'Electrical machinery and equipment', code_count: 1200 },
  { chapter_number: '95', description: 'Toys, games and sports requisites', code_count: 800 },
  { chapter_number: '61', description: 'Articles of apparel and clothing accessories, knitted or crocheted', code_count: 600 },
  { chapter_number: '42', description: 'Articles of leather; saddlery and harness', code_count: 400 }
]

// Mock API functions
const mockSearchHTS = async (query: string, chapter?: string, limit: number = 20): Promise<HTSSearchResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const filteredCodes = mockHTSCodes.filter(code => 
    code.description.toLowerCase().includes(query.toLowerCase()) ||
    code.hts_code.includes(query)
  )
  
  return {
    success: true,
    message: `Found ${filteredCodes.length} HTS codes`,
    data: filteredCodes.slice(0, limit),
    total_results: filteredCodes.length,
    search_query: query,
    search_time_ms: 500
  }
}

const mockGetChapters = async (): Promise<{ success: boolean, data: ChapterSummary[] }> => {
  await new Promise(resolve => setTimeout(resolve, 300))
  return {
    success: true,
    data: mockChapters
  }
}

const mockGetPopularCodes = async (limit: number = 10): Promise<{ success: boolean, data: HTSCode[] }> => {
  await new Promise(resolve => setTimeout(resolve, 200))
  return {
    success: true,
    data: mockHTSCodes.slice(0, limit)
  }
}

// Search HTS codes
export const useHTSSearch = (query: string, chapter?: string, limit: number = 20) => {
  return useQuery({
    queryKey: QUERY_KEYS.htsSearch(query, chapter, limit),
    queryFn: () => api.tariff.searchHTS(query, chapter, limit),
    enabled: query.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  })
}

// Get specific HTS code
export const useHTSCode = (htsCode: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.htsCode(htsCode),
    queryFn: () => api.tariff.getHTSCode(htsCode),
    enabled: !!htsCode,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Get all chapters
export const useChapters = () => {
  return useQuery({
    queryKey: QUERY_KEYS.chapters,
    queryFn: () => api.tariff.getChapters(),
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
  })
}

// Get popular HTS codes
export const usePopularCodes = (limit: number = 10) => {
  return useQuery({
    queryKey: QUERY_KEYS.popularCodes(limit),
    queryFn: () => api.tariff.getPopularCodes(limit),
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
  })
}

// Calculate tariff mutation
export const useTariffCalculation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: TariffCalculationRequest) => {
      // Mock calculation
      await new Promise(resolve => setTimeout(resolve, 1000))
      return {
        success: true,
        message: 'Calculation completed successfully',
        data: {
          hts_code: data.hts_code,
          duty_amount: 150.00,
          mpf_amount: 25.00,
          hmf_amount: 0.125,
          total_landed_cost: 1175.13,
          calculation_breakdown: {
            product_value: 1000.00,
            freight_cost: data.freight_cost || 0,
            insurance_cost: data.insurance_cost || 0,
            duty_rate: 15.0,
            mpf_rate: 0.3464,
            hmf_rate: 0.125
          }
        }
      }
    },
    onSuccess: (data) => {
      toast.success('Tariff calculation completed')
      // Cache the calculation result
      queryClient.setQueryData(QUERY_KEYS.calculation, data)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Calculation failed')
    },
  })
}

// Custom hook for debounced search
export const useDebouncedHTSSearch = (delay: number = 300) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedTerm, setDebouncedTerm] = useState('')
  const [chapter, setChapter] = useState<string>()
  const [limit, setLimit] = useState(20)

  // Debounce logic
  useState(() => {
    const timer = setTimeout(() => {
      setDebouncedTerm(searchTerm)
    }, delay)

    return () => clearTimeout(timer)
  })

  const searchQuery = useHTSSearch(debouncedTerm, chapter, limit)

  return {
    searchTerm,
    setSearchTerm,
    chapter,
    setChapter,
    limit,
    setLimit,
    ...searchQuery,
  }
}

// Custom hook for HTS code details with related codes
export const useHTSCodeWithRelated = (htsCode: string) => {
  const codeQuery = useHTSCode(htsCode)
  const chapter = codeQuery.data?.data?.[0]?.chapter
  
  // Get related codes from same chapter
  const relatedQuery = useHTSSearch(chapter || '', chapter, 10)
  
  return {
    code: codeQuery.data?.data?.[0],
    isLoading: codeQuery.isLoading,
    error: codeQuery.error,
    relatedCodes: relatedQuery.data?.data?.filter(code => code.hts_code !== htsCode) || [],
  }
}

// Export all hooks
export default {
  useHTSSearch,
  useHTSCode,
  useChapters,
  usePopularCodes,
  useTariffCalculation,
  useDebouncedHTSSearch,
  useHTSCodeWithRelated,
} 