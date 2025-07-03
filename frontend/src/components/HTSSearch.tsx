import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, FileText, TrendingUp, Clock, CheckCircle, X } from 'lucide-react';

const HTSSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Mock suggestions - in real app, these would come from AI/API
  const mockSuggestions = [
    'Nitrile gloves - HTS 4015.19.0510',
    'Cotton t-shirts - HTS 6109.10.0010',
    'Smartphone - HTS 8517.13.00',
    'Steel pipes - HTS 7306.30.50',
    'Plastic containers - HTS 3923.30.00',
    'Wooden furniture - HTS 9403.60.80',
    'Electronic components - HTS 8542.31.00',
    'Textile fabrics - HTS 5208.52.30'
  ];

  // Mock search history
  useEffect(() => {
    setRecentSearches([
      'Nitrile gloves',
      'Cotton t-shirts',
      'Steel pipes',
      'Plastic containers'
    ]);
  }, []);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Add to search history
    setSearchHistory(prev => [query, ...prev.slice(0, 4)]);
    
    setIsLoading(false);
  };

  const handleInputChange = (value: string) => {
    setSearchQuery(value);
    
    if (value.trim()) {
      // Filter suggestions based on input
      const filtered = mockSuggestions.filter(suggestion => 
        suggestion.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 5));
    } else {
      setSuggestions([]);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    setSuggestions([]);
    handleSearch(suggestion);
  };

  return (
    <div className="hts-search">
      <motion.div
        className="search-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>HTS Code Lookup</h1>
        <p>Search for Harmonized Tariff Schedule codes with AI-powered suggestions</p>
      </motion.div>

      {/* Main Search Section */}
      <motion.div
        className="search-section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="glass-card search-card">
          <div className="search-input-container">
            <div className="search-input-wrapper">
              <Search className="search-icon" />
              <input
                type="text"
                className="glass-input search-input"
                placeholder="Describe your product (e.g., 'nitrile gloves', 'cotton t-shirts')"
                value={searchQuery}
                onChange={(e) => handleInputChange(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
              />
              {isLoading && (
                <motion.div
                  className="loading-spinner"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Sparkles size={20} />
                </motion.div>
              )}
            </div>

            {/* AI Suggestions */}
            <AnimatePresence>
              {suggestions.length > 0 && (
                <motion.div
                  className="suggestions-container"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  {suggestions.map((suggestion, index) => (
                    <motion.div
                      key={index}
                      className="suggestion-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2, delay: index * 0.05 }}
                      whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      <Sparkles size={16} />
                      <span>{suggestion}</span>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <motion.button
            className="glass-button search-button"
            onClick={() => handleSearch(searchQuery)}
            disabled={isLoading || !searchQuery.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? 'Searching...' : 'Search HTS Codes'}
            <Search size={20} />
          </motion.button>
        </div>
      </motion.div>

      {/* Recent Searches */}
      <motion.div
        className="recent-searches"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="glass-card">
          <h3>
            <Clock size={20} />
            Recent Searches
          </h3>
          <div className="recent-items">
            {recentSearches.map((item, index) => (
              <motion.div
                key={index}
                className="recent-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                onClick={() => handleSearch(item)}
              >
                <FileText size={16} />
                <span>{item}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        className="quick-actions"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="glass-card">
          <h3>
            <TrendingUp size={20} />
            Popular Categories
          </h3>
          <div className="category-grid">
            {[
              'Textiles & Apparel',
              'Electronics',
              'Machinery',
              'Chemicals',
              'Food & Beverages',
              'Automotive'
            ].map((category, index) => (
              <motion.button
                key={category}
                className="category-button"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleSearch(category)}
              >
                {category}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Search Results Placeholder */}
      <AnimatePresence>
        {searchHistory.length > 0 && (
          <motion.div
            className="search-results"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.6 }}
          >
            <div className="glass-card">
              <h3>
                <CheckCircle size={20} />
                Search Results
              </h3>
              <div className="results-list">
                {searchHistory.slice(0, 3).map((query, index) => (
                  <motion.div
                    key={index}
                    className="result-item"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <div className="result-content">
                      <h4>{query}</h4>
                      <p>HTS Code: 4015.19.0510 | Tariff Rate: 3.0%</p>
                      <span className="result-tag">Nitrile gloves, disposable</span>
                    </div>
                    <button className="result-action">
                      View Details
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HTSSearch; 