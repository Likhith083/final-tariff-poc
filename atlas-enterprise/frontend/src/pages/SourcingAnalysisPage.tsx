import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useHTSSearch } from '@/hooks/useHTS'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { 
  Globe, 
  TrendingDown, 
  TrendingUp, 
  MapPin, 
  DollarSign, 
  Percent,
  Award,
  BarChart3,
  Download,
  Filter
} from 'lucide-react'
import api from '@/services/api'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'

// Form validation schema
const sourcingSchema = z.object({
  hts_code: z.string().min(1, 'HTS code is required'),
  product_value: z.number().min(0.01, 'Product value must be greater than 0'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  current_country: z.string().min(2, 'Current country is required'),
  target_countries: z.array(z.string()).min(1, 'Select at least one country to compare'),
})

type SourcingFormData = z.infer<typeof sourcingSchema>

const countries = [
  { code: 'CN', name: 'China', flag: '🇨🇳' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷' },
  { code: 'TW', name: 'Taiwan', flag: '🇹🇼' },
  { code: 'VN', name: 'Vietnam', flag: '🇻🇳' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'TH', name: 'Thailand', flag: '🇹🇭' },
  { code: 'MY', name: 'Malaysia', flag: '🇲🇾' },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬' },
  { code: 'PH', name: 'Philippines', flag: '🇵🇭' },
  { code: 'ID', name: 'Indonesia', flag: '🇮🇩' },
  { code: 'BD', name: 'Bangladesh', flag: '🇧🇩' },
]

export const SourcingAnalysisPage: React.FC = () => {
  const [htsQuery, setHtsQuery] = useState('')
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'savings' | 'duty_rate' | 'total_cost'>('savings')
  
  // Form setup
  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm<SourcingFormData>({
    resolver: zodResolver(sourcingSchema),
    defaultValues: {
      hts_code: '',
      product_value: 1000,
      quantity: 1,
      current_country: 'CN',
      target_countries: ['MX', 'VN', 'TH'],
    }
  })
  
  // Queries and mutations
  const { data: htsSearchResults } = useHTSSearch(htsQuery, undefined, 10)
  
  const sourcingMutation = useMutation({
    mutationFn: (data: any) => api.tariff.compareSourcing(data),
    onSuccess: () => {
      toast.success('Sourcing analysis completed')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    },
  })
  
  const watchedValues = watch()
  
  // Handle form submission
  const onSubmit = (data: SourcingFormData) => {
    const requestData = {
      ...data,
      target_countries: selectedCountries.length > 0 ? selectedCountries : data.target_countries,
    }
    sourcingMutation.mutate(requestData)
  }
  
  // Select HTS code from search
  const selectHTSCode = (htsCode: string) => {
    setValue('hts_code', htsCode)
    setHtsQuery('')
  }
  
  // Toggle country selection
  const toggleCountry = (countryCode: string) => {
    setSelectedCountries(prev => 
      prev.includes(countryCode) 
        ? prev.filter(c => c !== countryCode)
        : [...prev, countryCode]
    )
  }
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }
  
  // Get country info
  const getCountryInfo = (code: string) => {
    return countries.find(c => c.code === code) || { code, name: code, flag: '🌍' }
  }
  
  const sourcingResults = sourcingMutation.data?.data || []
  const sortedResults = [...sourcingResults].sort((a, b) => {
    switch (sortBy) {
      case 'savings':
        return b.savings - a.savings
      case 'duty_rate':
        return a.duty_rate - b.duty_rate
      case 'total_cost':
        return a.total_landed_cost - b.total_landed_cost
      default:
        return 0
    }
  })
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Sourcing Analysis</h1>
        <p className="text-gray-600 mt-2">Compare sourcing options across different countries to optimize costs</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Analysis Setup
              </CardTitle>
              <CardDescription>
                Configure your sourcing comparison parameters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {/* HTS Code Search */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    HTS Code *
                  </label>
                  <div className="space-y-2">
                    <input
                      {...register('hts_code')}
                      placeholder="Enter HTS code"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                    {errors.hts_code && (
                      <p className="text-red-600 text-sm">{errors.hts_code.message}</p>
                    )}
                    
                    {/* HTS Search */}
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Search for HTS codes..."
                        value={htsQuery}
                        onChange={(e) => setHtsQuery(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      />
                      
                      {htsSearchResults?.data && htsQuery && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                          {htsSearchResults.data.map((code) => (
                            <button
                              key={code.id}
                              type="button"
                              onClick={() => selectHTSCode(code.hts_code)}
                              className="w-full text-left px-3 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                            >
                              <div className="font-medium text-blue-700">{code.hts_code}</div>
                              <div className="text-sm text-gray-600 truncate">{code.description}</div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Current Country */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Sourcing Country *
                  </label>
                  <select
                    {...register('current_country')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    {countries.map((country) => (
                      <option key={country.code} value={country.code}>
                        {country.flag} {country.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Product Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Product Value *
                    </label>
                    <input
                      {...register('product_value', { valueAsNumber: true })}
                      type="number"
                      step="0.01"
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                    {errors.product_value && (
                      <p className="text-red-600 text-sm">{errors.product_value.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity *
                    </label>
                    <input
                      {...register('quantity', { valueAsNumber: true })}
                      type="number"
                      min="1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                    {errors.quantity && (
                      <p className="text-red-600 text-sm">{errors.quantity.message}</p>
                    )}
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={sourcingMutation.isPending}
                >
                  {sourcingMutation.isPending ? 'Analyzing...' : 'Analyze Sourcing Options'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Country Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Compare Countries
              </CardTitle>
              <CardDescription>
                Select countries to compare against your current source
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {countries.map((country) => (
                  <button
                    key={country.code}
                    type="button"
                    onClick={() => toggleCountry(country.code)}
                    className={`p-2 text-left rounded-md border transition-colors ${
                      selectedCountries.includes(country.code)
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <div className="font-medium text-sm">
                      {country.flag} {country.code}
                    </div>
                    <div className="text-xs text-gray-600">{country.name}</div>
                  </button>
                ))}
              </div>
              
              {selectedCountries.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <div className="text-sm text-gray-600 mb-2">Selected countries:</div>
                  <div className="flex flex-wrap gap-1">
                    {selectedCountries.map((code) => {
                      const country = getCountryInfo(code)
                      return (
                        <Badge key={code} variant="secondary" className="text-xs">
                          {country.flag} {country.name}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-6">
          {sortedResults.length > 0 ? (
            <>
              {/* Controls */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Filter className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium">Sort by:</span>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as any)}
                        className="px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="savings">Highest Savings</option>
                        <option value="duty_rate">Lowest Duty Rate</option>
                        <option value="total_cost">Lowest Total Cost</option>
                      </select>
                    </div>
                    
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export Results
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Results List */}
              <div className="space-y-4">
                {sortedResults.map((result, index) => {
                  const country = getCountryInfo(result.country_code)
                  const isPositiveSavings = result.savings > 0
                  
                  return (
                    <Card key={result.country_code} className="relative">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-4">
                            <div className="text-2xl">{country.flag}</div>
                            <div className="space-y-2">
                              <div>
                                <h3 className="text-lg font-semibold">{country.name}</h3>
                                <p className="text-sm text-gray-600">{result.country_code}</p>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                  <Percent className="h-4 w-4 text-gray-400" />
                                  <span>Duty Rate: <span className="font-medium">{result.duty_rate}%</span></span>
                                </div>
                                
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-4 w-4 text-gray-400" />
                                  <span>Duty: <span className="font-medium">{formatCurrency(result.duty_amount)}</span></span>
                                </div>
                                
                                <div className="flex items-center gap-2">
                                  <BarChart3 className="h-4 w-4 text-gray-400" />
                                  <span>Total Cost: <span className="font-medium">{formatCurrency(result.total_landed_cost)}</span></span>
                                </div>
                                
                                {result.fta_benefits && (
                                  <div className="flex items-center gap-2">
                                    <Award className="h-4 w-4 text-green-500" />
                                    <span className="text-green-700 font-medium">FTA Benefits</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {/* Savings Badge */}
                          <div className="text-right">
                            <div className={`flex items-center gap-1 ${
                              isPositiveSavings ? 'text-green-700' : 'text-red-700'
                            }`}>
                              {isPositiveSavings ? (
                                <TrendingDown className="h-4 w-4" />
                              ) : (
                                <TrendingUp className="h-4 w-4" />
                              )}
                              <span className="font-semibold">
                                {isPositiveSavings ? 'Save' : 'Cost'} {formatCurrency(Math.abs(result.savings))}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              vs current source
                            </div>
                          </div>
                        </div>
                        
                        {result.fta_benefits && (
                          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-center gap-2 text-green-700 text-sm">
                              <Award className="h-4 w-4" />
                              <span className="font-medium">Free Trade Agreement Benefits:</span>
                            </div>
                            <p className="text-sm text-green-600 mt-1">{result.fta_benefits}</p>
                          </div>
                        )}
                      </CardContent>
                      
                      {index === 0 && isPositiveSavings && (
                        <div className="absolute -top-2 -right-2">
                          <Badge className="bg-green-600 text-white">Best Option</Badge>
                        </div>
                      )}
                    </Card>
                  )
                })}
              </div>
            </>
          ) : sourcingMutation.isError ? (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 text-red-700">
                  <TrendingUp className="h-5 w-5" />
                  <span>Analysis failed. Please check your inputs and try again.</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Globe className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg text-gray-500">Configure your analysis parameters</p>
                <p className="text-sm text-gray-400 mt-2">Fill out the form to compare sourcing options</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
} 