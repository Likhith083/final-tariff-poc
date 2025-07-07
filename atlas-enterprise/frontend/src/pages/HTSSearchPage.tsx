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
  Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'

export const HTSSearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedChapter, setSelectedChapter] = useState<string>('')
  const [limit, setLimit] = useState(20)
  const [showFilters, setShowFilters] = useState(false)
  const [recentSearches, setRecentSearches] = useState<string[]>([])
  
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
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">HTS Code Search</h1>
        <p className="text-gray-600 mt-2">Search for Harmonized Tariff Schedule codes and descriptions</p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search by HTS code or product description..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {isSearching && (
                <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 animate-spin text-gray-400" />
              )}
            </div>
            
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
          
          {searchResults?.data && searchResults.data.length > 0 ? (
            <div className="space-y-3">
              {searchResults.data.map((code) => (
                <Card key={code.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
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