import { useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatRequest {
  messages: ChatMessage[]
  model: string
  serp_search?: boolean
  product_query?: string
  temperature?: number
  max_tokens?: number
}

interface ChatResponse {
  content: string
  model: string
  usage?: any
  product_info?: any
  error?: string
}

// Mutation for AI chat
export const useAIChat = () => {
  return useMutation({
    mutationFn: async (data: ChatRequest): Promise<ChatResponse> => {
      try {
        console.log('Sending AI chat request:', data)
        
        // Call the backend API directly
        const response = await api.post('/api/v1/ai/chat', data)
        
        console.log('Received AI chat response:', response)
        
        // Return the response directly - the backend already returns the correct format
        return response
        
      } catch (error) {
        console.error('AI chat API error:', error)
        
        // Throw the error so it can be handled by the component
        throw new Error(`Failed to get AI response: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    },
    onError: (error) => {
      console.error('AI chat mutation error:', error)
      // Don't show toast here - let the component handle it
    },
    onSuccess: (data) => {
      console.log('AI chat mutation success:', data)
      // Don't show toast here - let the component handle it
    }
  })
}

// Remove the mock response generator - we don't need it anymore
// The backend should handle all responses, including errors 