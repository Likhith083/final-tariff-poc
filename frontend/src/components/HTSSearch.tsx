import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, FileText, Clock, CheckCircle, X, Download, ChevronDown } from 'lucide-react';

interface HTSResult {
  hts_code: string;
  description: string;
  duty_rate: string;
  category: string;
  similarity_score?: number;
}

interface HTSSuggestion {
  hts_code: string;
  description: string;
  display_text: string;
  similarity_score: number;
}

const HTSSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [results, setResults] = useState<HTSResult[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [suggestions, setSuggestions] = useState<HTSSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load recent searches from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem('hts_recent_searches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse recent searches:', e);
      }
    }
  }, []);

  // Debounced search for suggestions
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (searchQuery.trim().length >= 2) {
      searchTimeoutRef.current = setTimeout(() => {
        fetchSuggestions(searchQuery);
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const fetchSuggestions = async (query: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/hts/suggestions?query=${encodeURIComponent(query)}&limit=5`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const performSearch = async (query: string = searchQuery) => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/hts/search?query=${encodeURIComponent(query)}&limit=50`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setResults(data.results || []);
          // Add to recent searches
          addToRecentSearches(query);
        } else {
          setError(data.message || 'Search failed');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch results');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to fetch results. Please check your connection.');
    } finally {
      setIsLoading(false);
      setShowSuggestions(false);
    }
  };

  const addToRecentSearches = (query: string) => {
    const updated = [query, ...recentSearches.filter(q => q !== query)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('hts_recent_searches', JSON.stringify(updated));
  };

  const handleSearch = () => {
    performSearch();
  };

  const handleSuggestionClick = (suggestion: HTSSuggestion) => {
    setSearchQuery(suggestion.display_text);
    setShowSuggestions(false);
    performSearch(suggestion.display_text);
  };

  const handleRecentSearchClick = (query: string) => {
    setSearchQuery(query);
    performSearch(query);
  };

  const handleSelectAll = () => {
    if (selected.size === results.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(results.map(r => r.hts_code)));
    }
  };

  const handleSelect = (htsCode: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(htsCode)) {
      newSelected.delete(htsCode);
    } else {
      newSelected.add(htsCode);
    }
    setSelected(newSelected);
  };

  const exportToCSV = () => {
    if (selected.size === 0) return;

    const selectedResults = results.filter(r => selected.has(r.hts_code));
    const csvContent = [
      'HTS Code,Description,Duty Rate,Category',
      ...selectedResults.map(r => `"${r.hts_code}","${r.description}","${r.duty_rate}","${r.category}"`)
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hts_codes_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportToPDF = () => {
    if (selected.size === 0) return;
    
    // Simple PDF export using browser print
    const selectedResults = results.filter(r => selected.has(r.hts_code));
    const printContent = `
      <html>
        <head><title>HTS Codes Export</title></head>
        <body>
          <h1>HTS Codes Export</h1>
          <table border="1" style="width:100%; border-collapse: collapse;">
            <tr><th>HTS Code</th><th>Description</th><th>Duty Rate</th><th>Category</th></tr>
            ${selectedResults.map(r => `
              <tr>
                <td>${r.hts_code}</td>
                <td>${r.description}</td>
                <td>${r.duty_rate}</td>
                <td>${r.category}</td>
              </tr>
            `).join('')}
          </table>
        </body>
      </html>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow?.document.write(printContent);
    printWindow?.document.close();
    printWindow?.print();
  };

  return (
    <div className="hts-search-container">
      {/* Header */}
      <div className="search-header" style={{ marginBottom: '2.5rem' }}>
        <h1 style={{
          fontFamily: 'Inter, Segoe UI, Roboto, Arial, sans-serif',
          fontWeight: 900,
          fontSize: '2.8rem',
          color: '#22223b',
          letterSpacing: '-1px',
          marginBottom: '0.5rem',
          textShadow: '0 2px 8px rgba(0,0,0,0.04)'
        }}>HTS Code Search</h1>
        <p style={{
          fontFamily: 'Inter, Segoe UI, Roboto, Arial, sans-serif',
          fontWeight: 500,
          fontSize: '1.25rem',
          color: '#444',
          marginBottom: 0
        }}>
          Find Harmonized Tariff Schedule codes with intelligent search and autocomplete
        </p>
      </div>

      {/* Search Input */}
      <div className="search-input-container">
        <div className="search-input-wrapper">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search for products, materials, or HTS codes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            onFocus={() => searchQuery.trim().length >= 2 && setShowSuggestions(true)}
            className="search-input"
          />
          <motion.button
            className="search-button"
            onClick={handleSearch}
            disabled={!searchQuery.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Search size={20} />
              </motion.div>
            ) : (
              'Search'
            )}
          </motion.button>
        </div>

        {/* Autocomplete Suggestions */}
        <AnimatePresence>
          {showSuggestions && suggestions.length > 0 && (
            <motion.div
              className="suggestions-dropdown"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {suggestions.map((suggestion, index) => (
                <motion.div
                  key={suggestion.hts_code}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                  whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <FileText size={16} />
                  <span>{suggestion.display_text}</span>
                  <span className="similarity-score">
                    {Math.round(suggestion.similarity_score * 100)}%
                  </span>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Recent Searches */}
      {recentSearches.length > 0 && !results.length && !isLoading && (
        <div className="recent-searches">
          <h3>Recent Searches</h3>
          <div className="recent-grid">
            {recentSearches.map((search, index) => (
              <motion.div
                key={index}
                className="recent-search-item"
                onClick={() => handleRecentSearchClick(search)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Clock size={16} />
                <span>{search}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="error-message"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <X size={16} />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading State */}
      {isLoading && (
        <div className="loading-container">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <Search size={24} />
          </motion.div>
          <p>Searching...</p>
        </div>
      )}

      {/* Results */}
      {!isLoading && results.length > 0 && (
        <div className="results-container">
          <div className="results-header">
            <div className="results-info">
              <h3>Search Results ({results.length})</h3>
              <p>Found {results.length} HTS codes matching "{searchQuery}"</p>
            </div>
            
            {results.length > 0 && (
              <div className="export-controls">
                <div className="select-controls">
                  <a
                    className="select-all-btn"
                    style={{ color: '#4ecdc4', fontWeight: 700, textDecoration: 'underline', cursor: 'pointer', opacity: 1 }}
                    onMouseOver={e => (e.currentTarget.style.color = '#222')}
                    onMouseOut={e => (e.currentTarget.style.color = '#4ecdc4')}
                    onClick={handleSelectAll}
                  >
                    {selected.size === results.length ? 'Deselect All' : 'Select All'}
                  </a>
                  {selected.size > 0 && (
                    <span className="selected-count">
                      {selected.size} selected
                    </span>
                  )}
                </div>
                
                {selected.size > 0 && (
                  <div className="export-buttons">
                    <button
                      className="export-btn csv"
                      onClick={exportToCSV}
                    >
                      <Download size={16} />
                      Export CSV
                    </button>
                    <button
                      className="export-btn pdf"
                      onClick={exportToPDF}
                    >
                      <FileText size={16} />
                      Export PDF
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="results-table">
            <table>
              <thead>
                <tr>
                  <th className="checkbox-col">
                    <input
                      type="checkbox"
                      checked={selected.size === results.length}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th>HTS Code</th>
                  <th>Description</th>
                  <th>Duty Rate</th>
                  <th>Category</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, index) => (
                  <motion.tr
                    key={result.hts_code}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={selected.has(result.hts_code) ? 'selected' : ''}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={selected.has(result.hts_code)}
                        onChange={() => handleSelect(result.hts_code)}
                      />
                    </td>
                    <td className="hts-code">
                      <FileText size={14} />
                      {result.hts_code}
                    </td>
                    <td className="description">{result.description}</td>
                    <td className="duty-rate">{result.duty_rate}</td>
                    <td className="category">{result.category || '-'}</td>
                    <td className="actions">
                      <button
                        className="action-btn"
                        onClick={() => navigator.clipboard.writeText(result.hts_code)}
                        title="Copy HTS Code"
                      >
                        <FileText size={14} style={{ color: '#4ecdc4', opacity: 0.95, fontSize: '1.2rem', cursor: 'pointer' }} />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* No Results */}
      {!isLoading && !error && searchQuery && results.length === 0 && (
        <div className="no-results">
          <Search size={48} />
          <h3>No results found</h3>
          <p>Try searching with different keywords or check your spelling</p>
        </div>
      )}

      <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center' }}>
        <a
          href="https://www.cartage.ai/tools/hts-code-lookup"
          target="_blank"
          rel="noopener noreferrer"
          className="glass-button primary"
          style={{ fontWeight: 700, fontSize: '1.1rem', padding: '1rem 2.5rem', background: 'linear-gradient(135deg, #4ecdc4 0%, #667eea 100%)', color: '#fff', border: 'none', borderRadius: '16px', boxShadow: '0 4px 24px rgba(76, 205, 196, 0.15)' }}
        >
          Open Cartage AI HTS Lookup
        </a>
      </div>
    </div>
  );
};

export default HTSSearch; 