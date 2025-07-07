import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTariffCalculation, useHTSSearch } from '@/hooks/useHTS'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { 
  Calculator, 
  DollarSign, 
  Truck, 
  Package, 
  FileText, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Download,
  Copy
} from 'lucide-react'
import toast from 'react-hot-toast'

// Form validation schema
const calculationSchema = z.object({
  hts_code: z.string().min(1, 'HTS code is required'),
  country_code: z.string().min(2, 'Country code is required'),
  product_value: z.number().min(0.01, 'Product value must be greater than 0'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  freight_cost: z.number().min(0, 'Freight cost cannot be negative'),
  insurance_cost: z.number().min(0, 'Insurance cost cannot be negative'),
  other_costs: z.number().min(0, 'Other costs cannot be negative'),
  currency: z.string().min(3, 'Currency is required'),
})

type CalculationFormData = z.infer<typeof calculationSchema>

const countries = [
  { code: 'CN', name: 'China' },
  { code: 'MX', name: 'Mexico' },
  { code: 'CA', name: 'Canada' },
  { code: 'JP', name: 'Japan' },
  { code: 'DE', name: 'Germany' },
  { code: 'KR', name: 'South Korea' },
  { code: 'TW', name: 'Taiwan' },
  { code: 'VN', name: 'Vietnam' },
  { code: 'IN', name: 'India' },
  { code: 'TH', name: 'Thailand' },
]

const currencies = [
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'CNY', name: 'Chinese Yuan' },
  { code: 'JPY', name: 'Japanese Yen' },
  { code: 'CAD', name: 'Canadian Dollar' },
  { code: 'MXN', name: 'Mexican Peso' },
]

export const TariffCalculatorPage: React.FC = () => {
  const [htsQuery, setHtsQuery] = useState('')
  const [selectedHTS, setSelectedHTS] = useState<string>('')
  
  // Form setup
  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm<CalculationFormData>({
    resolver: zodResolver(calculationSchema),
    defaultValues: {
      hts_code: '',
      country_code: 'CN',
      product_value: 1000,
      quantity: 1,
      freight_cost: 100,
      insurance_cost: 50,
      other_costs: 0,
      currency: 'USD',
    }
  })
  
  // Queries and mutations
  const { data: htsSearchResults } = useHTSSearch(htsQuery, undefined, 10)
  const calculationMutation = useTariffCalculation()
  
  const watchedValues = watch()
  
  // Handle form submission
  const onSubmit = (data: CalculationFormData) => {
    calculationMutation.mutate(data)
  }
  
  // Select HTS code from search
  const selectHTSCode = (htsCode: string) => {
    setValue('hts_code', htsCode)
    setSelectedHTS(htsCode)
    setHtsQuery('')
  }
  
  // Copy calculation results
  const copyResults = () => {
    if (calculationMutation.data?.data) {
      const result = calculationMutation.data.data
      const text = `
HTS Code: ${result.hts_code}
Product: ${result.product_description}
Country: ${result.country_name}
Total Landed Cost: $${result.total_landed_cost.toFixed(2)}
Duty Amount: $${result.duty_amount.toFixed(2)}
Duty Rate: ${result.duty_rate}%
      `.trim()
      navigator.clipboard.writeText(text)
      toast.success('Results copied to clipboard')
    }
  }
  
  // Format currency
  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }
  
  const calculationResult = calculationMutation.data?.data
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tariff Calculator</h1>
        <p className="text-gray-600 mt-2">Calculate landed costs including duties, taxes, and fees</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Calculation Details
              </CardTitle>
              <CardDescription>
                Enter product and shipping information for tariff calculation
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
                      placeholder="Enter HTS code (e.g., 8471.30.0100)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                    {errors.hts_code && (
                      <p className="text-red-600 text-sm">{errors.hts_code.message}</p>
                    )}
                    
                    {/* HTS Search */}
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Or search for HTS codes..."
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

                {/* Country */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Country of Origin *
                  </label>
                  <select
                    {...register('country_code')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    {countries.map((country) => (
                      <option key={country.code} value={country.code}>
                        {country.name} ({country.code})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Product Value and Currency */}
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
                      Currency *
                    </label>
                    <select
                      {...register('currency')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    >
                      {currencies.map((currency) => (
                        <option key={currency.code} value={currency.code}>
                          {currency.code} - {currency.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Quantity */}
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

                {/* Shipping Costs */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Shipping & Additional Costs</h4>
                  
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Freight Cost
                      </label>
                      <input
                        {...register('freight_cost', { valueAsNumber: true })}
                        type="number"
                        step="0.01"
                        min="0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Insurance Cost
                      </label>
                      <input
                        {...register('insurance_cost', { valueAsNumber: true })}
                        type="number"
                        step="0.01"
                        min="0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Other Costs
                      </label>
                      <input
                        {...register('other_costs', { valueAsNumber: true })}
                        type="number"
                        step="0.01"
                        min="0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={calculationMutation.isPending}
                >
                  {calculationMutation.isPending ? 'Calculating...' : 'Calculate Tariff'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="space-y-6">
          {calculationResult ? (
            <>
              {/* Summary Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      Calculation Results
                    </CardTitle>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={copyResults}>
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                      <span className="text-lg font-medium">Total Landed Cost</span>
                      <span className="text-2xl font-bold text-blue-700">
                        {formatCurrency(calculationResult.total_landed_cost)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-600">Product Value</div>
                        <div className="font-semibold">{formatCurrency(calculationResult.product_value_usd)}</div>
                      </div>
                      
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-600">Duty Amount</div>
                        <div className="font-semibold">{formatCurrency(calculationResult.duty_amount)}</div>
                      </div>
                      
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-600">MPF Amount</div>
                        <div className="font-semibold">{formatCurrency(calculationResult.mpf_amount)}</div>
                      </div>
                      
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-600">HMF Amount</div>
                        <div className="font-semibold">{formatCurrency(calculationResult.hmf_amount)}</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Product Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    Product Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">HTS Code:</span>
                      <span className="font-medium">{calculationResult.hts_code}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Description:</span>
                      <span className="font-medium text-right max-w-xs">{calculationResult.product_description}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Country:</span>
                      <span className="font-medium">{calculationResult.country_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Duty Rate:</span>
                      <Badge variant="outline">{calculationResult.duty_rate}%</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Calculation Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Calculation Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span>Product Value ({calculationResult.currency}):</span>
                      <span>{formatCurrency(calculationResult.calculation_breakdown.product_value, calculationResult.currency)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Freight Cost:</span>
                      <span>{formatCurrency(calculationResult.calculation_breakdown.freight_cost)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Insurance Cost:</span>
                      <span>{formatCurrency(calculationResult.calculation_breakdown.insurance_cost)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Other Costs:</span>
                      <span>{formatCurrency(calculationResult.calculation_breakdown.other_costs)}</span>
                    </div>
                    <Separator />
                    <div className="flex justify-between font-medium">
                      <span>Customs Value:</span>
                      <span>{formatCurrency(calculationResult.customs_value)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Duty ({calculationResult.duty_rate}%):</span>
                      <span>{formatCurrency(calculationResult.duty_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MPF:</span>
                      <span>{formatCurrency(calculationResult.mpf_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>HMF:</span>
                      <span>{formatCurrency(calculationResult.hmf_amount)}</span>
                    </div>
                    <Separator />
                    <div className="flex justify-between font-bold text-lg">
                      <span>Total Landed Cost:</span>
                      <span>{formatCurrency(calculationResult.total_landed_cost)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : calculationMutation.isError ? (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 text-red-700">
                  <AlertCircle className="h-5 w-5" />
                  <span>Calculation failed. Please check your inputs and try again.</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Calculator className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg text-gray-500">Enter product details to calculate tariff</p>
                <p className="text-sm text-gray-400 mt-2">Fill out the form on the left to get started</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
} 