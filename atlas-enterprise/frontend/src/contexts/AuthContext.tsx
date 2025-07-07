import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '@/services/api'
import toast from 'react-hot-toast'

interface User {
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

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  demoLogin: () => void
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token and validate
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        // For now, skip backend validation to avoid API errors
        // TODO: Re-enable when backend is fixed
        console.log('Skipping auth check due to backend issues')
        
        // If it's a demo token, restore the demo user
        if (token === 'demo-token') {
          const demoUser: User = {
            id: 'demo',
            email: 'demo@atlas.com',
            username: 'demo',
            full_name: 'Demo User',
            role: 'user',
            phone: '123-456-7890',
            company: 'ATLAS Demo',
            job_title: 'Demo Specialist',
            department: 'Demo',
            created_at: new Date().toISOString(),
          }
          setUser(demoUser)
          console.log('Demo user restored from token')
        }
      }
      setIsLoading(false)
    }
    
    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await api.auth.login({ username, password })
      
      if (response.success && response.data) {
        const { access_token, user } = response.data
        localStorage.setItem('auth_token', access_token)
        setUser(user)
        toast.success('Login successful!')
      } else {
        throw new Error(response.message || 'Login failed')
      }
    } catch (error: any) {
      console.error('Login failed:', error)
      const message = error.response?.data?.detail || error.message || 'Login failed'
      toast.error(message)
      throw error
    }
  }

  const register = async (data: any) => {
    try {
      const response = await api.auth.register(data)
      
      if (response.success && response.data) {
        const { access_token, user } = response.data
        localStorage.setItem('auth_token', access_token)
        setUser(user)
        toast.success('Registration successful!')
      } else {
        throw new Error(response.message || 'Registration failed')
      }
    } catch (error: any) {
      console.error('Registration failed:', error)
      const message = error.response?.data?.detail || error.message || 'Registration failed'
      toast.error(message)
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('auth_token')
    toast.success('Logged out successfully')
    window.location.href = '/login'
  }

  const demoLogin = () => {
    console.log('Demo login called - setting demo user without network request')
    const demoUser: User = {
      id: 'demo',
      email: 'demo@atlas.com',
      username: 'demo',
      full_name: 'Demo User',
      role: 'user',
      phone: '123-456-7890',
      company: 'ATLAS Demo',
      job_title: 'Demo Specialist',
      department: 'Demo',
      created_at: new Date().toISOString(),
    }
    localStorage.setItem('auth_token', 'demo-token')
    setUser(demoUser)
    console.log('Demo user set successfully:', demoUser)
  }

  const value = {
    user,
    login,
    register,
    demoLogin,
    logout,
    isLoading,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 