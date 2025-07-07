import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { AuthProvider } from '@/contexts/AuthContext'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

// Pages
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { UnifiedDashboard } from '@/pages/UnifiedDashboard'
import { HTSSearchPage } from '@/pages/HTSSearchPage'
import { TariffCalculatorPage } from '@/pages/TariffCalculatorPage'
import { SourcingAnalysisPage } from '@/pages/SourcingAnalysisPage'
import { AIChatbotPage } from '@/pages/AIChatbotPage'
import { ProfilePage } from '@/pages/ProfilePage'

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            {/* Main unified dashboard */}
            <Route index element={<UnifiedDashboard />} />
            
            {/* Individual feature pages */}
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="hts-search" element={<HTSSearchPage />} />
            <Route path="calculator" element={<TariffCalculatorPage />} />
            <Route path="sourcing" element={<SourcingAnalysisPage />} />
            <Route path="ai-chatbot" element={<AIChatbotPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          
          {/* Redirect legacy routes */}
          <Route path="/atlas" element={<Navigate to="/" replace />} />
          <Route path="/demo" element={<Navigate to="/" replace />} />
        </Routes>
        
        <Toaster />
      </div>
    </AuthProvider>
  )
}

export default App 