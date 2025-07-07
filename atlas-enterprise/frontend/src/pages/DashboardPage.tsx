import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Package, 
  Globe, 
  Users, 
  Clock,
  Search,
  Calculator,
  FileText,
  AlertCircle,
  CheckCircle,
  Activity
} from 'lucide-react'
import { useChapters, usePopularCodes } from '@/hooks/useHTS'
import api from '@/services/api'
import { Link } from 'react-router-dom'

export const DashboardPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')
  
  // Data queries
  const { data: chaptersData } = useChapters()
  const { data: popularCodes } = usePopularCodes()
  
  // Health check
  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.health.check(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })
  
  // Mock data for demonstration - in real app, these would come from API
  const dashboardStats = {
    totalSearches: 1247,
    totalCalculations: 589,
    totalSavings: 125000,
    activeUsers: 23,
    recentActivity: [
      { id: 1, type: 'search', description: 'HTS search for "computers"', time: '2 minutes ago', user: 'John D.' },
      { id: 2, type: 'calculation', description: 'Tariff calculation for 8471.30.0100', time: '5 minutes ago', user: 'Sarah M.' },
      { id: 3, type: 'sourcing', description: 'Sourcing analysis: China vs Vietnam', time: '12 minutes ago', user: 'Mike R.' },
      { id: 4, type: 'search', description: 'HTS search for "textiles"', time: '18 minutes ago', user: 'Lisa K.' },
      { id: 5, type: 'calculation', description: 'Tariff calculation for 6203.42.4010', time: '25 minutes ago', user: 'David L.' },
    ],
    topCountries: [
      { code: 'CN', name: 'China', searches: 456, flag: '🇨🇳' },
      { code: 'MX', name: 'Mexico', searches: 234, flag: '🇲🇽' },
      { code: 'VN', name: 'Vietnam', searches: 189, flag: '🇻🇳' },
      { code: 'CA', name: 'Canada', searches: 167, flag: '🇨🇦' },
      { code: 'JP', name: 'Japan', searches: 145, flag: '🇯🇵' },
    ],
  }
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }
  
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'search':
        return <Search className="h-4 w-4 text-blue-500" />
      case 'calculation':
        return <Calculator className="h-4 w-4 text-green-500" />
      case 'sourcing':
        return <Globe className="h-4 w-4 text-purple-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }
  
  const isHealthy = healthData?.data?.status === 'healthy'
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Overview of your tariff management activities</p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
            <span className="text-sm font-medium">
              System {isHealthy ? 'Healthy' : 'Issues'}
            </span>
          </div>
          
          {/* Time Range Selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Searches</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.totalSearches.toLocaleString()}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Search className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-green-600">+12% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Calculations</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.totalCalculations.toLocaleString()}</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Calculator className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-green-600">+8% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Savings</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(dashboardStats.totalSavings)}</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-green-600">+15% from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardStats.activeUsers}</p>
              </div>
              <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Users className="h-6 w-6 text-orange-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm">
              <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
              <span className="text-red-600">-3% from last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>Latest actions across your organization</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardStats.recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className="mt-1">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">{activity.user}</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{activity.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <Button variant="outline" className="w-full">
                  View All Activity
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Top Countries */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Top Countries
              </CardTitle>
              <CardDescription>Most searched countries this month</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardStats.topCountries.map((country, index) => (
                  <div key={country.code} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-lg">{country.flag}</div>
                      <div>
                        <p className="font-medium text-sm">{country.name}</p>
                        <p className="text-xs text-gray-500">{country.code}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-sm">{country.searches}</p>
                      <p className="text-xs text-gray-500">searches</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Popular HTS Codes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Popular HTS Codes
            </CardTitle>
            <CardDescription>Most frequently searched codes</CardDescription>
          </CardHeader>
          <CardContent>
            {popularCodes?.data ? (
              <div className="space-y-3">
                {popularCodes.data.slice(0, 8).map((code) => (
                  <div key={code.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-blue-700">{code.hts_code}</p>
                      <p className="text-sm text-gray-600 truncate">{code.description}</p>
                    </div>
                    <div className="flex gap-2">
                      <Link to={`/calculator?hts=${code.hts_code}`}>
                        <Button variant="outline" size="sm">
                          <Calculator className="h-4 w-4" />
                        </Button>
                      </Link>
                      <Link to={`/sourcing?hts=${code.hts_code}`}>
                        <Button variant="outline" size="sm">
                          <Globe className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">Loading popular codes...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* HTS Chapters Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              HTS Chapters
            </CardTitle>
            <CardDescription>Overview of available product categories</CardDescription>
          </CardHeader>
          <CardContent>
            {chaptersData?.data ? (
              <div className="space-y-3">
                {chaptersData.data.slice(0, 8).map((chapter) => (
                  <div key={chapter.chapter_number} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium">Chapter {chapter.chapter_number}</p>
                      <p className="text-sm text-gray-600 truncate">{chapter.description}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant="secondary" className="text-xs">
                        {chapter.code_count} codes
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">Loading chapters...</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Link to="/search">
              <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center gap-2">
                <Search className="h-6 w-6" />
                <span>Search HTS Codes</span>
              </Button>
            </Link>
            
            <Link to="/calculator">
              <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center gap-2">
                <Calculator className="h-6 w-6" />
                <span>Calculate Tariff</span>
              </Button>
            </Link>
            
            <Link to="/sourcing">
              <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center gap-2">
                <Globe className="h-6 w-6" />
                <span>Sourcing Analysis</span>
              </Button>
            </Link>
            
            <Link to="/profile">
              <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center gap-2">
                <FileText className="h-6 w-6" />
                <span>View Reports</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 