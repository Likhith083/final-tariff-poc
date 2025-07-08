import React, { useState, useEffect, useCallback } from 'react'
import { useDebounce } from 'use-debounce'
import { useHTSSearch, useChapters, usePopularCodes } from '@/hooks/useHTS'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { HTSCode } from '@/services/api'
import { 
  Search, 
  Filter, 
  Copy, 
  ChevronRight, 
  TrendingUp,
  Clock,
  Package,
  FileText,
  AlertCircle,
  Loader2,
  ExternalLink,
  ArrowRight,
  Download,
  FileSpreadsheet,
  CheckSquare,
  Square,
  X
} from 'lucide-react'
import toast from 'react-hot-toast'

export const HTSSearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedChapter, setSelectedChapter] = useState<string>('')
  const [limit, setLimit] = useState(20)
  const [showFilters, setShowFilters] = useState(false)
  const [recentSearches, setRecentSearches] = useState<string[]>([])
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set())
  const [isExporting, setIsExporting] = useState(false)
  
  // Debounce search term
  const [debouncedSearchTerm] = useDebounce(searchTerm, 300)
  
  // Load recent searches from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem('atlas-recent-searches')
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved))
      } catch (e) {
        console.error('Error loading recent searches:', e)
      }
    }
  }, [])
  
  // Save recent searches to localStorage
  const saveRecentSearch = useCallback((search: string) => {
    if (!search.trim() || search.length < 2) return
    
    setRecentSearches(prev => {
      const updated = [search, ...prev.filter(s => s !== search)].slice(0, 10) // Keep last 10 searches
      localStorage.setItem('atlas-recent-searches', JSON.stringify(updated))
      return updated
    })
  }, [])
  
  // Handle search term change and save to recent searches
  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value)
    if (value.trim() && value.length >= 2) {
      // Debounced save to recent searches
      const timeoutId = setTimeout(() => {
        saveRecentSearch(value.trim())
      }, 1000) // Save after 1 second of no typing
      
      return () => clearTimeout(timeoutId)
    }
  }, [saveRecentSearch])
  
  // Queries
  const { data: searchResults, isLoading: isSearching, error: searchError } = useHTSSearch(
    debouncedSearchTerm, 
    selectedChapter || undefined, 
    limit
  )
  const { data: chapters } = useChapters()
  const { data: popularCodes } = usePopularCodes(5)
  
  // Copy HTS code to clipboard
  const copyToClipboard = useCallback((code: string) => {
    navigator.clipboard.writeText(code)
    toast.success(`Copied ${code} to clipboard`)
  }, [])
  
  // Highlight search term in text
  const highlightText = (text: string, highlight: string) => {
    if (!highlight.trim()) return text
    
    const regex = new RegExp(`(${highlight})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, i) => 
      regex.test(part) ? <mark key={i} className="bg-yellow-200 px-0.5">{part}</mark> : part
    )
  }
  
  // Format duty rate
  const formatDutyRate = (rate: number | null) => {
    if (rate === null || rate === 0) return 'Free'
    return `${rate}%`
  }
  
  // Check if search is by HTS code
  const isHTSCodeSearch = (query: string) => {
    const cleanQuery = query.replace(/\./g, '')
    return /^\d+$/.test(cleanQuery) || (cleanQuery.length <= 10 && /\d/.test(cleanQuery))
  }

  // Selection functions
  const toggleSelection = (htsCode: string) => {
    const newSelected = new Set(selectedCodes)
    if (newSelected.has(htsCode)) {
      newSelected.delete(htsCode)
    } else {
      newSelected.add(htsCode)
    }
    setSelectedCodes(newSelected)
  }

  const selectAll = () => {
    if (searchResults?.data) {
      const allCodes = new Set(searchResults.data.map(code => code.hts_code))
      setSelectedCodes(allCodes)
    }
  }

  const clearSelection = () => {
    setSelectedCodes(new Set())
  }

  // Export functions
  const exportToCSV = () => {
    if (!searchResults?.data || selectedCodes.size === 0) return
    
    const selectedData = searchResults.data.filter(code => selectedCodes.has(code.hts_code))
    
    const headers = ['HTS Code', 'Description', 'Chapter', 'General Rate', 'Special Rate', 'Unit of Quantity']
    const csvContent = [
      headers.join(','),
      ...selectedData.map(code => [
        code.hts_code,
        `"${code.description.replace(/"/g, '""')}"`,
        code.chapter,
        code.general_rate || 0,
        code.special_rate || 0,
        code.unit_of_quantity
      ].join(','))
    ].join('\n')
    
    downloadFile(csvContent, 'hts-codes.csv', 'text/csv')
  }

  const exportToExcel = async () => {
    if (!searchResults?.data || selectedCodes.size === 0) return
    
    setIsExporting(true)
    try {
      const selectedData = searchResults.data.filter(code => selectedCodes.has(code.hts_code))
      
      // Create a simple tab-separated values format that Excel can open
      const headers = ['HTS Code', 'Description', 'Chapter', 'General Rate', 'Special Rate', 'Unit of Quantity']
      const tsvContent = [
        headers.join('\t'),
        ...selectedData.map(code => [
          code.hts_code,
          code.description.replace(/\t/g, ' '),
          code.chapter,
          code.general_rate || 0,
          code.special_rate || 0,
          code.unit_of_quantity
        ].join('\t'))
      ].join('\n')
      
      downloadFile(tsvContent, 'hts-codes.xlsx', 'application/vnd.ms-excel')
      toast.success(`Exported ${selectedData.length} HTS codes to Excel`)
    } catch (error) {
      toast.error('Failed to export to Excel')
    } finally {
      setIsExporting(false)
    }
  }

  const exportToPDF = async () => {
    if (!searchResults?.data || selectedCodes.size === 0) return
    
    setIsExporting(true)
    try {
      const selectedData = searchResults.data.filter(code => selectedCodes.has(code.hts_code))
      
      // Create HTML content for PDF
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>HTS Codes Export</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .hts-code { font-weight: bold; color: #2563eb; }
          </style>
        </head>
        <body>
          <h1>HTS Codes Export</h1>
          <p>Generated on: ${new Date().toLocaleDateString()}</p>
          <p>Total codes: ${selectedData.length}</p>
          <table>
            <thead>
              <tr>
                <th>HTS Code</th>
                <th>Description</th>
                <th>Chapter</th>
                <th>General Rate</th>
                <th>Special Rate</th>
                <th>Unit</th>
              </tr>
            </thead>
            <tbody>
              ${selectedData.map(code => `
                <tr>
                  <td class="hts-code">${code.hts_code}</td>
                  <td>${code.description}</td>
                  <td>${code.chapter}</td>
                  <td>${formatDutyRate(code.general_rate)}</td>
                  <td>${formatDutyRate(code.special_rate)}</td>
                  <td>${code.unit_of_quantity}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </body>
        </html>
      `
      
      downloadFile(htmlContent, 'hts-codes.html', 'text/html')
      toast.success(`Exported ${selectedData.length} HTS codes to PDF (HTML format)`)
    } catch (error) {
      toast.error('Failed to export to PDF')
    } finally {
      setIsExporting(false)
    }
  }

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // Document and image upload handlers
  const handleDocumentUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      toast.loading('Analyzing document for HTS codes...')
      const response = await fetch('/api/v1/hts/classify-document', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        toast.dismiss()
        
        if (result.success && result.data.suggested_codes?.length > 0) {
          const suggestions = result.data.suggested_codes
          toast.success(`Found ${suggestions.length} potential HTS codes`)
          
          // Set search term to first suggestion
          setSearchTerm(suggestions[0].hts_code)
          
          // Show all suggestions in a toast
          const suggestionText = suggestions.map((s: any) => 
            `${s.hts_code}: ${s.description} (${s.confidence}% confidence)`
          ).join('\n')
          
          console.log('HTS Code Suggestions:', suggestionText)
        } else {
          toast.error('No HTS codes found in document')
        }
      } else {
        throw new Error('Classification failed')
      }
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to analyze document')
      console.error('Document upload error:', error)
    }
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      toast.loading('Analyzing image for product classification...')
      const response = await fetch('/api/v1/hts/classify-image', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        toast.dismiss()
        
        if (result.success && result.data.suggested_codes?.length > 0) {
          const suggestions = result.data.suggested_codes
          toast.success(`Identified product! Found ${suggestions.length} potential HTS codes`)
          
          // Set search term to first suggestion
          setSearchTerm(suggestions[0].hts_code)
          
          // Show product description
          if (result.data.product_description) {
            toast.success(`Product identified as: ${result.data.product_description}`)
          }
        } else {
          toast.error('Could not classify product from image')
        }
      } else {
        throw new Error('Image classification failed')
      }
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to analyze image')
      console.error('Image upload error:', error)
    }
  }
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">HTS Code Search</h1>
        <p className="text-gray-600 mt-2">Search for Harmonized Tariff Schedule codes and descriptions</p>
      </div>

      {/* External Cartage AI Link */}
      <Card className="border-2 border-blue-300 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                  <ExternalLink className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-blue-900">Need More HTS Code Help?</h3>
                <p className="text-sm text-blue-700 mt-1">Try our partner's free HTS code lookup tool from Cartage AI</p>
                <p className="text-xs text-blue-600 mt-1">✓ Instant HS & HTS Code Lookup ✓ AI-Powered Accuracy ✓ Supports U.S. & Canada</p>
              </div>
            </div>
            <Button 
              onClick={() => window.open('https://www.cartage.ai/tools/hts-code-lookup?utm_source=chatgpt.com', '_blank')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 text-base font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
              size="lg"
            >
              <span>Visit Cartage AI</span>
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Document Upload for HTS Classification */}
      <Card className="border-2 border-green-300 bg-gradient-to-r from-green-50 to-emerald-50">
        <CardContent className="p-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-emerald-600 rounded-lg flex items-center justify-center">
                <FileText className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-green-900">Document Classification</h3>
                <p className="text-sm text-green-700">Upload product images or documents for automatic HTS code classification</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div 
                className="border-2 border-dashed border-green-300 rounded-lg p-4 text-center hover:border-green-400 transition-colors cursor-pointer"
                onClick={() => document.getElementById('document-upload')?.click()}
              >
                <FileText className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-sm text-green-700 font-medium">Upload Document</p>
                <p className="text-xs text-green-600 mt-1">PDF, DOC, DOCX, TXT</p>
              </div>
              
              <div 
                className="border-2 border-dashed border-green-300 rounded-lg p-4 text-center hover:border-green-400 transition-colors cursor-pointer"
                onClick={() => document.getElementById('image-upload')?.click()}
              >
                <Package className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-sm text-green-700 font-medium">Upload Image</p>
                <p className="text-xs text-green-600 mt-1">JPG, PNG, WEBP</p>
              </div>
            </div>
            
            <input
              id="document-upload"
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleDocumentUpload}
              className="hidden"
            />
            
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </div>
        </CardContent>
      </Card>

      {/* Search Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search by HTS code (e.g., 8471.30.01) or product description (e.g., laptop computer)..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {isSearching && (
                <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 animate-spin text-gray-400" />
              )}
            </div>
            
            {/* Search Tips */}
            <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              <p className="font-medium mb-1">💡 Search Tips:</p>
              <ul className="space-y-1 text-xs">
                <li>• <strong>By HTS Code:</strong> Enter codes like "8471.30.01" or "84713001" (periods are optional)</li>
                <li>• <strong>By Product:</strong> Describe your product like "smartphone" or "cotton t-shirt"</li>
                <li>• <strong>By Keywords:</strong> Use terms like "electronics" or "textiles" for broader results</li>
              </ul>
            </div>
            
            {/* Search Type Indicator */}
            {debouncedSearchTerm && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-600">Search type:</span>
                <Badge variant={isHTSCodeSearch(debouncedSearchTerm) ? "default" : "secondary"}>
                  {isHTSCodeSearch(debouncedSearchTerm) ? "HTS Code Search" : "Product Description Search"}
                </Badge>
              </div>
            )}
            
            {/* Filters */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2"
              >
                <Filter className="h-4 w-4" />
                Filters
                {selectedChapter && <Badge variant="secondary">{selectedChapter}</Badge>}
              </Button>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                {searchResults && (
                  <>
                    <span>{searchResults.total_results} results</span>
                    <span>•</span>
                    <span>{searchResults.search_time_ms}ms</span>
                  </>
                )}
              </div>
            </div>
            
            {/* Filter Panel */}
            {showFilters && (
              <div className="border-t pt-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chapter Filter
                  </label>
                  <select
                    value={selectedChapter}
                    onChange={(e) => setSelectedChapter(e.target.value)}
                    className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Chapters</option>
                    {chapters?.data?.map((chapter) => (
                      <option key={chapter.chapter_number} value={chapter.chapter_number}>
                        Chapter {chapter.chapter_number}: {chapter.description} ({chapter.code_count} codes)
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Results per page
                  </label>
                  <select
                    value={limit}
                    onChange={(e) => setLimit(Number(e.target.value))}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Results */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search Results */}
          {searchError && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 text-red-700">
                  <AlertCircle className="h-5 w-5" />
                  <span>Error loading results. Please try again.</span>
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Selection and Export Controls */}
          {searchResults?.data && searchResults.data.length > 0 && (
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={selectedCodes.size === searchResults.data.length ? clearSelection : selectAll}
                        className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800"
                      >
                        {selectedCodes.size === searchResults.data.length ? (
                          <>
                            <CheckSquare className="h-4 w-4" />
                            Clear All
                          </>
                        ) : (
                          <>
                            <Square className="h-4 w-4" />
                            Select All
                          </>
                        )}
                      </button>
                      {selectedCodes.size > 0 && (
                        <span className="text-sm text-gray-600">
                          {selectedCodes.size} of {searchResults.data.length} selected
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {selectedCodes.size > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600 mr-2">Export:</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={exportToCSV}
                        className="flex items-center gap-1"
                      >
                        <FileSpreadsheet className="h-4 w-4" />
                        CSV
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={exportToExcel}
                        disabled={isExporting}
                        className="flex items-center gap-1"
                      >
                        <FileSpreadsheet className="h-4 w-4" />
                        Excel
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={exportToPDF}
                        disabled={isExporting}
                        className="flex items-center gap-1"
                      >
                        <Download className="h-4 w-4" />
                        PDF
                      </Button>
                      {isExporting && (
                        <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
          
          {searchResults?.data && searchResults.data.length > 0 ? (
            <div className="space-y-3">
              {searchResults.data.map((code) => (
                <Card key={code.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {/* Selection Checkbox */}
                      <button
                        onClick={() => toggleSelection(code.hts_code)}
                        className="mt-1 flex-shrink-0"
                      >
                        {selectedCodes.has(code.hts_code) ? (
                          <CheckSquare className="h-5 w-5 text-blue-600" />
                        ) : (
                          <Square className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                        )}
                      </button>
                      
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-blue-700">
                            {code.hts_code}
                          </h3>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(code.hts_code)}
                            className="h-7 w-7 p-0"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Badge variant="outline">
                            Chapter {code.chapter}
                          </Badge>
                        </div>
                        
                        <p className="text-gray-700">
                          {highlightText(code.description, debouncedSearchTerm)}
                        </p>
                        
                        <div className="flex flex-wrap gap-4 text-sm">
                          <div className="flex items-center gap-1">
                            <Package className="h-4 w-4 text-gray-400" />
                            <span className="text-gray-600">Unit: {code.unit_of_quantity}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <FileText className="h-4 w-4 text-gray-400" />
                            <span className="text-gray-600">
                              General Rate: <span className="font-medium">{formatDutyRate(code.general_rate)}</span>
                            </span>
                          </div>
                          {code.special_rate !== null && (
                            <div className="flex items-center gap-1">
                              <TrendingUp className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-600">
                                Special Rate: <span className="font-medium">{formatDutyRate(code.special_rate)}</span>
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => window.location.href = `/hts/${code.hts_code}`}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : debouncedSearchTerm && !isSearching ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-gray-500">
                  <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg">No results found for "{debouncedSearchTerm}"</p>
                  <p className="text-sm mt-2">Try adjusting your search terms or filters</p>
                </div>
              </CardContent>
            </Card>
          ) : !debouncedSearchTerm ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-gray-500">
                  <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg">Enter a search term to find HTS codes</p>
                  <p className="text-sm mt-2">Search by code, product description, or keywords</p>
                </div>
              </CardContent>
            </Card>
          ) : null}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Popular Codes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Popular HTS Codes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {popularCodes?.data?.map((code) => (
                  <button
                    key={code.id}
                    onClick={() => setSearchTerm(code.hts_code)}
                    className="w-full text-left p-2 rounded hover:bg-gray-50 transition-colors"
                  >
                    <div className="font-medium text-sm text-blue-700">{code.hts_code}</div>
                    <div className="text-xs text-gray-600 line-clamp-2">{code.description}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/calculator'}
                >
                  Calculate Tariff
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/sourcing'}
                >
                  Compare Sourcing
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => window.open('https://hts.usitc.gov/', '_blank')}
                >
                  USITC Reference
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Searches */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Recent Searches
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentSearches.length > 0 ? (
                <div className="space-y-2">
                  {recentSearches.map((search, index) => (
                    <button
                      key={index}
                      onClick={() => setSearchTerm(search)}
                      className="w-full text-left p-2 rounded hover:bg-gray-50 transition-colors text-sm text-gray-700 border border-gray-200"
                    >
                      <div className="flex items-center gap-2">
                        <Clock className="h-3 w-3 text-gray-400" />
                        {search}
                      </div>
                    </button>
                  ))}
                  <button
                    onClick={() => {
                      setRecentSearches([])
                      localStorage.removeItem('atlas-recent-searches')
                    }}
                    className="w-full text-center p-2 text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    Clear Recent Searches
                  </button>
                </div>
              ) : (
                <p className="text-sm text-gray-500">Your recent searches will appear here</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
} 