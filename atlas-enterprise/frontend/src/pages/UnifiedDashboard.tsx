import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  Search, 
  Calculator, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  FileText, 
  Globe, 
  DollarSign, 
  Package, 
  Users, 
  BarChart3, 
  PieChart, 
  Activity, 
  Target, 
  Zap, 
  Shield, 
  Briefcase, 
  Brain,
  MessageSquare,
  Loader2
} from 'lucide-react'
import { useHTSSearch, usePopularCodes } from '@/hooks/useHTS'
import { useAIChat } from '@/hooks/useAI'
import api from '@/services/api'
import toast from 'react-hot-toast'

interface DashboardMetrics {
  totalSearches: number
  avgDutyRate: number
  costSavings: number
  complianceScore: number
  activeSourcingProjects: number
  riskAlerts: number
}

interface SourcingOption {
  country: string
  cost: number
  dutyRate: number
  leadTime: string
  risk: 'low' | 'medium' | 'high'
}

interface ComplianceAlert {
  id: string
  type: 'warning' | 'error' | 'info'
  message: string
  htsCode?: string
  action?: string
}

export const UnifiedDashboard: React.FC = () => {
  const [activePersona, setActivePersona] = useState<'procurement' | 'compliance' | 'analyst'>('procurement')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedHTS, setSelectedHTS] = useState<string>('')
  const [calculationValue, setCalculationValue] = useState<number>(1000)
  const [aiQuery, setAiQuery] = useState('')
  const [isCalculating, setIsCalculating] = useState(false)
  const [calculationResult, setCalculationResult] = useState<any>(null)
  const [isAgentAnalyzing, setIsAgentAnalyzing] = useState(false)
  const [agentAnalysisResult, setAgentAnalysisResult] = useState<any>(null)
  
  // Mock data for demonstration
  const [metrics] = useState<DashboardMetrics>({
    totalSearches: 1247,
    avgDutyRate: 8.5,
    costSavings: 125000,
    complianceScore: 94,
    activeSourcingProjects: 8,
    riskAlerts: 3
  })
  
  const [sourcingOptions] = useState<SourcingOption[]>([
    { country: 'China', cost: 1000, dutyRate: 25, leadTime: '4-6 weeks', risk: 'high' },
    { country: 'Vietnam', cost: 1150, dutyRate: 0, leadTime: '3-4 weeks', risk: 'medium' },
    { country: 'Mexico', cost: 1200, dutyRate: 0, leadTime: '1-2 weeks', risk: 'low' },
    { country: 'India', cost: 1100, dutyRate: 5, leadTime: '5-7 weeks', risk: 'medium' }
  ])
  
  const [complianceAlerts] = useState<ComplianceAlert[]>([
    { id: '1', type: 'warning', message: 'Section 301 tariff update affects electronics imports', htsCode: '8517.13.0000', action: 'Review rates' },
    { id: '2', type: 'error', message: 'Missing certificate of origin for textile shipment', htsCode: '6104.43.2010', action: 'Obtain certificate' },
    { id: '3', type: 'info', message: 'New GSP benefits available for Vietnam imports', action: 'Update procedures' }
  ])
  
  // Hooks
  const { data: searchResults, isLoading: isSearching } = useHTSSearch(searchTerm, undefined, 5)
  const { data: popularCodes } = usePopularCodes(5)
  const aiChatMutation = useAIChat()
  
  // Calculate tariff
  const handleCalculateTariff = async () => {
    if (!selectedHTS || !calculationValue) return
    
    setIsCalculating(true)
    try {
      const result = await api.tariff.calculate({
        hts_code: selectedHTS,
        product_value: calculationValue,
        quantity: 1,
        freight_cost: 0,
        insurance_cost: 0,
        other_costs: 0,
        country_code: 'CN',
        currency: 'USD'
      })
      setCalculationResult(result.data)
      toast.success('Tariff calculation completed')
    } catch (error) {
      console.error('Calculation error:', error)
      toast.error('Calculation failed')
    } finally {
      setIsCalculating(false)
    }
  }
  
  // AI Chat
  const handleAIQuery = async () => {
    if (!aiQuery.trim()) return
    
    try {
      const result = await aiChatMutation.mutateAsync({
        messages: [{ role: 'user', content: aiQuery }],
        model: 'llama3.1',
        temperature: 0.1
      })
      toast.success('AI analysis completed')
    } catch (error) {
      console.error('AI query error:', error)
      toast.error('AI query failed')
    }
  }
  
  // Add agent sourcing analysis function
  const handleAgentSourcingAnalysis = async () => {
    if (!searchTerm) {
      toast.error('Please enter a product description first')
      return
    }
    
    setIsAgentAnalyzing(true)
    try {
      const result = await api.post('/api/v1/agents/sourcing/analyze', {
        product_description: searchTerm,
        target_countries: ['CN', 'VN', 'MX', 'IN'],
        product_value: calculationValue,
        quantity: 1
      })
      
      setAgentAnalysisResult(result.data)
      toast.success('AI Agent analysis completed!')
    } catch (error) {
      console.error('Agent analysis error:', error)
      toast.error('Agent analysis failed')
    } finally {
      setIsAgentAnalyzing(false)
    }
  }
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }
  
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'high': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }
  
  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-red-600 bg-red-100 border-red-200'
      case 'warning': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'info': return 'text-blue-600 bg-blue-100 border-blue-200'
      default: return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">ATLAS Enterprise</h1>
        <p className="text-xl text-gray-600">Intelligent Tariff Management & Trade Compliance Platform</p>
      </div>
      
      {/* Persona Selector */}
      <div className="flex justify-center">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActivePersona('procurement')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activePersona === 'procurement' 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Briefcase className="h-4 w-4" />
            Procurement Manager
          </button>
          <button
            onClick={() => setActivePersona('compliance')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activePersona === 'compliance' 
                ? 'bg-green-600 text-white' 
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Shield className="h-4 w-4" />
            Compliance Officer
          </button>
          <button
            onClick={() => setActivePersona('analyst')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activePersona === 'analyst' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Brain className="h-4 w-4" />
            Business Analyst
          </button>
        </div>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Searches</p>
                <p className="text-2xl font-bold">{metrics.totalSearches.toLocaleString()}</p>
              </div>
              <Search className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Duty Rate</p>
                <p className="text-2xl font-bold">{metrics.avgDutyRate}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Cost Savings</p>
                <p className="text-2xl font-bold">{formatCurrency(metrics.costSavings)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Compliance Score</p>
                <p className="text-2xl font-bold">{metrics.complianceScore}%</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Projects</p>
                <p className="text-2xl font-bold">{metrics.activeSourcingProjects}</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Risk Alerts</p>
                <p className="text-2xl font-bold">{metrics.riskAlerts}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Main Content based on Persona */}
      <Tabs value={activePersona} onValueChange={(value: string) => setActivePersona(value as 'procurement' | 'compliance' | 'analyst')}>
        
        {/* Procurement Manager View */}
        <TabsContent value="procurement" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* HTS Search & Calculation */}
            <div className="lg:col-span-2 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Search className="h-5 w-5" />
                    Product Classification & Costing
                  </CardTitle>
                  <CardDescription>
                    Find HTS codes and calculate import costs
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Search for products (e.g., laptop, smartphone, textile)"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {searchResults?.data && searchResults.data.length > 0 && (
                    <div className="space-y-2">
                      {searchResults.data.map((code) => (
                        <div
                          key={code.id}
                          className={`p-3 border rounded-md cursor-pointer transition-colors ${
                            selectedHTS === code.hts_code 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedHTS(code.hts_code)}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-blue-700">{code.hts_code}</p>
                              <p className="text-sm text-gray-600">{code.description}</p>
                            </div>
                            <Badge variant="outline">{code.general_rate}%</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="Product value (USD)"
                      value={calculationValue}
                      onChange={(e) => setCalculationValue(Number(e.target.value))}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                    <Button 
                      onClick={handleCalculateTariff}
                      disabled={!selectedHTS || isCalculating}
                      className="flex items-center gap-2"
                    >
                      {isCalculating ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Calculator className="h-4 w-4" />
                      )}
                      Calculate
                    </Button>
                  </div>
                  
                  {calculationResult && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                      <h4 className="font-medium text-green-800 mb-2">Calculation Results</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>Product Value: {formatCurrency(calculationResult.product_value_usd)}</div>
                        <div>Duty Rate: {calculationResult.duty_rate}%</div>
                        <div>Duty Amount: {formatCurrency(calculationResult.duty_amount)}</div>
                        <div>Total Cost: {formatCurrency(calculationResult.total_landed_cost)}</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
            
            {/* Sourcing Options */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="h-5 w-5" />
                    Sourcing Options
                  </CardTitle>
                  <CardDescription>
                    Compare costs across countries
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 mb-4">
                    <Button 
                      onClick={handleAgentSourcingAnalysis}
                      disabled={!searchTerm || isAgentAnalyzing}
                      className="w-full flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      {isAgentAnalyzing ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Zap className="h-4 w-4" />
                      )}
                      AI Agent Analysis
                    </Button>
                  </div>
                  
                  {agentAnalysisResult?.data?.recommendations && (
                    <div className="space-y-3 mb-4">
                      <h4 className="font-medium text-sm text-purple-800">🤖 AI Recommendations</h4>
                      {agentAnalysisResult.data.recommendations.map((rec: any, index: number) => (
                        <div key={index} className="p-3 border border-purple-200 bg-purple-50 rounded-md">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="font-medium text-purple-900">{rec.country_name}</h5>
                            <Badge className="bg-purple-100 text-purple-800">
                              {rec.type}
                            </Badge>
                          </div>
                          <p className="text-sm text-purple-700 mb-2">{rec.reasoning}</p>
                          <div className="text-xs text-purple-600">
                            Cost: {formatCurrency(rec.total_cost)} | Confidence: {(rec.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="space-y-3">
                    {sourcingOptions.map((option, index) => (
                      <div key={index} className="p-3 border border-gray-200 rounded-md">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium">{option.country}</h4>
                          <Badge className={getRiskColor(option.risk)}>
                            {option.risk} risk
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>Cost: {formatCurrency(option.cost)}</div>
                          <div>Duty: {option.dutyRate}%</div>
                          <div>Lead Time: {option.leadTime}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
        
        {/* Compliance Officer View */}
        <TabsContent value="compliance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Compliance Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Compliance Alerts
                </CardTitle>
                <CardDescription>
                  Active compliance issues and updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {complianceAlerts.map((alert) => (
                    <div key={alert.id} className={`p-3 border rounded-md ${getAlertColor(alert.type)}`}>
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          {alert.type === 'error' && <AlertCircle className="h-4 w-4" />}
                          {alert.type === 'warning' && <AlertCircle className="h-4 w-4" />}
                          {alert.type === 'info' && <FileText className="h-4 w-4" />}
                          <span className="font-medium text-sm">{alert.type.toUpperCase()}</span>
                        </div>
                        {alert.htsCode && (
                          <Badge variant="outline">{alert.htsCode}</Badge>
                        )}
                      </div>
                      <p className="text-sm mb-2">{alert.message}</p>
                      {alert.action && (
                        <Button size="sm" variant="outline" className="text-xs">
                          {alert.action}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            {/* Compliance Score Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Compliance Score Breakdown
                </CardTitle>
                <CardDescription>
                  Current compliance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Classification Accuracy</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div className="w-18 h-2 bg-green-500 rounded-full" style={{ width: '95%' }}></div>
                      </div>
                      <span className="text-sm font-medium">95%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Documentation Complete</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div className="w-16 h-2 bg-yellow-500 rounded-full" style={{ width: '88%' }}></div>
                      </div>
                      <span className="text-sm font-medium">88%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Regulatory Updates</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div className="w-19 h-2 bg-green-500 rounded-full" style={{ width: '98%' }}></div>
                      </div>
                      <span className="text-sm font-medium">98%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Audit Readiness</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div className="w-17 h-2 bg-green-500 rounded-full" style={{ width: '92%' }}></div>
                      </div>
                      <span className="text-sm font-medium">92%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        {/* Business Analyst View */}
        <TabsContent value="analyst" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* AI Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  AI Trade Intelligence
                </CardTitle>
                <CardDescription>
                  Ask questions about trade data and regulations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ask about trade regulations, tariffs, or sourcing strategies..."
                    value={aiQuery}
                    onChange={(e) => setAiQuery(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                  <Button 
                    onClick={handleAIQuery}
                    disabled={!aiQuery.trim() || aiChatMutation.isPending}
                    className="flex items-center gap-2"
                  >
                    {aiChatMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <MessageSquare className="h-4 w-4" />
                    )}
                    Ask AI
                  </Button>
                </div>
                
                <div className="space-y-2">
                  <Button variant="outline" size="sm" onClick={() => setAiQuery('What are the latest Section 301 tariff updates?')}>
                    Section 301 Updates
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setAiQuery('Compare sourcing costs between China and Vietnam')}>
                    Sourcing Analysis
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setAiQuery('What are the compliance requirements for textile imports?')}>
                    Compliance Guide
                  </Button>
                </div>
              </CardContent>
            </Card>
            
            {/* Trade Analytics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Trade Analytics
                </CardTitle>
                <CardDescription>
                  Key insights and trends
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <h4 className="font-medium text-blue-800 mb-1">Top Import Categories</h4>
                    <p className="text-sm text-blue-700">Electronics (45%), Textiles (23%), Machinery (18%)</p>
                  </div>
                  
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <h4 className="font-medium text-green-800 mb-1">Cost Savings Opportunity</h4>
                    <p className="text-sm text-green-700">Switch 15% of electronics sourcing to Vietnam for $50K savings</p>
                  </div>
                  
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <h4 className="font-medium text-yellow-800 mb-1">Risk Assessment</h4>
                    <p className="text-sm text-yellow-700">High tariff exposure on China electronics (65% of imports)</p>
                  </div>
                  
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-md">
                    <h4 className="font-medium text-purple-800 mb-1">Trend Analysis</h4>
                    <p className="text-sm text-purple-700">Increasing demand for GSP-eligible suppliers (+12% this quarter)</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      
      {/* Popular HTS Codes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Popular HTS Codes
          </CardTitle>
          <CardDescription>
            Frequently searched classification codes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {popularCodes?.data?.map((code) => (
              <div key={code.id} className="p-3 border border-gray-200 rounded-md hover:border-blue-300 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-blue-700">{code.hts_code}</h4>
                  <Badge variant="outline">{code.general_rate}%</Badge>
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">{code.description}</p>
                <div className="flex gap-2 mt-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setSelectedHTS(code.hts_code)}
                  >
                    Select
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => setSearchTerm(code.hts_code)}
                  >
                    Search
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 