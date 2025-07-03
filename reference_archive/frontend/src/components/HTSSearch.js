import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, FileText, Copy, ExternalLink, X } from 'lucide-react';
import apiService from '../services/apiService';
import logger from '../utils/logger';

const HTSSearch = ({ backendStatus }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    logger.componentMount('HTSSearch');
    loadRecentSearches();
  }, []);

  const loadRecentSearches = () => {
    setRecentSearches([
      { id: 1, query: 'electronics', count: 45 },
      { id: 2, query: 'textiles', count: 32 },
      { id: 3, query: 'machinery', count: 28 },
      { id: 4, query: 'chemicals', count: 19 }
    ]);
  };

  const handleSearch = async (query = searchQuery) => {
    if (!query.trim() || backendStatus !== 'connected') return;
    try {
      setIsLoading(true);
      logger.userAction('HTSSearch', `search_query: ${query}`);
      const response = await apiService.searchHTS({
        query: query,
        category: null,
        rate_filter: null
      });
      if (response.success && response.data && response.data.results) {
        setSearchResults(response.data.results);
        logger.info('HTSSearch', `Search completed with ${response.data.results.length} results`);
      } else {
        setSearchResults([]);
        logger.warn('HTSSearch', 'No results found');
      }
    } catch (error) {
      logger.error('HTSSearch', 'Search failed', error);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResultClick = (result) => {
    setSelectedResult(result);
    logger.userAction('HTSSearch', `select_result: ${result.hts_code}`);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    logger.userAction('HTSSearch', 'copy_hts_code');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <motion.div
      className="hts-search"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="search-header">
        <h1>HTS Code Search</h1>
        <p>Find Harmonized Tariff Schedule codes and descriptions</p>
      </div>
      {/* Search Input */}
      <div className="search-container">
        <div className="search-input-wrapper">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search for products, materials, or HTS codes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="search-input"
            disabled={backendStatus !== 'connected'}
          />
          <motion.button
            className="search-button"
            onClick={() => handleSearch()}
            disabled={!searchQuery.trim() || backendStatus !== 'connected' || isLoading}
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
      </div>
      {/* Recent Searches */}
      {recentSearches.length > 0 && !searchResults.length && !isLoading && (
        <div className="recent-searches">
          <h3>Recent Searches</h3>
          <div className="recent-grid">
            {recentSearches.map((search) => (
              <motion.div
                key={search.id}
                className="recent-search-item"
                onClick={() => {
                  setSearchQuery(search.query);
                  handleSearch(search.query);
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Search size={16} />
                <span>{search.query}</span>
                <span className="result-count">{search.count} results</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
      {/* Shimmer Loading */}
      {isLoading && (
        <div className="results-grid">
          {[...Array(6)].map((_, i) => (
            <div className="shimmer" key={i} />
          ))}
        </div>
      )}
      {/* Search Results */}
      {!isLoading && searchResults.length > 0 && (
        <div className="search-results">
          <div className="results-header">
            <h3>Search Results ({searchResults.length})</h3>
            <p>Click on a result to view details</p>
          </div>
          <div className="results-grid">
            <AnimatePresence>
              {searchResults.map((result, idx) => (
                <motion.div
                  key={result.hts_code + idx}
                  className={`result-card${selectedResult?.hts_code === result.hts_code ? ' selected' : ''}`}
                  onClick={() => handleResultClick(result)}
                  whileHover={{ scale: 1.03, y: -4 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ duration: 0.3, delay: idx * 0.03 }}
                >
                  <div className="hts-code">
                    <FileText size={18} />
                    <span>{result.hts_code}</span>
                    <motion.button
                      className="copy-button"
                      onClick={e => { e.stopPropagation(); copyToClipboard(result.hts_code); }}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <Copy size={14} />
                    </motion.button>
                  </div>
                  <div className="duty-rate">{result.rate_display || `${result.general_rate}%`}</div>
                  <div className="result-description">{result.description}</div>
                  <div className="result-meta">
                    <span className="rate-type">{result.rate_type}</span>
                    <span className="confidence">Confidence: {Math.round(result.confidence * 100)}%</span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
      {/* Details Modal */}
      <AnimatePresence>
        {selectedResult && (
          <motion.div
            className="details-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              className="details-modal-content"
              initial={{ scale: 0.98, y: 40 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.98, y: 40 }}
              transition={{ duration: 0.25 }}
            >
              <div className="details-header">
                <h3>HTS Code Details</h3>
                <button className="close-details" onClick={() => setSelectedResult(null)}>
                  <X size={24} />
                </button>
              </div>
              <div className="details-content">
                <div className="detail-row">
                  <label>HTS Code:</label>
                  <span className="hts-code-detail">{selectedResult.hts_code}</span>
                </div>
                <div className="detail-row">
                  <label>Description:</label>
                  <span>{selectedResult.description}</span>
                </div>
                <div className="detail-row">
                  <label>General Rate:</label>
                  <span className="duty-rate-detail">{selectedResult.general_rate}%</span>
                </div>
                <div className="detail-row">
                  <label>Specific Rate:</label>
                  <span>${selectedResult.specific_rate}</span>
                </div>
                <div className="detail-row">
                  <label>Other Rate:</label>
                  <span>${selectedResult.other_rate}</span>
                </div>
                <div className="detail-row">
                  <label>Rate Type:</label>
                  <span>{selectedResult.rate_type}</span>
                </div>
                <div className="detail-row">
                  <label>Confidence:</label>
                  <span>{Math.round(selectedResult.confidence * 100)}%</span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* No Results */}
      {searchQuery && !isLoading && searchResults.length === 0 && (
        <div className="no-results">
          <Search size={48} />
          <h3>No results found</h3>
          <p>Try adjusting your search terms or browse recent searches</p>
        </div>
      )}
    </motion.div>
  );
};

export default HTSSearch; 