import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User } from 'lucide-react';
import { chatService } from '../services/chatService';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: "Hello! I'm TariffAI, your intelligent HTS & tariff management assistant. I can help you with:\n\n• Tariff calculations and cost analysis\n• HTS code searches and classifications\n• Material composition analysis\n• Alternative sourcing recommendations\n• Scenario simulations\n\nWhat would you like to know?",
        timestamp: new Date(),
        suggestions: [
          "Calculate tariffs for HTS 8471.30.01",
          "Search for smartphone HTS codes",
          "Analyze material composition",
          "Compare sourcing scenarios"
        ]
      }
    ]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(inputMessage, sessionId);
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        suggestions: response.suggestions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
        suggestions: ["Try rephrasing your question", "Check your internet connection"]
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <motion.div
      className="glass-card"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="chat-container">
        <div className="chat-messages">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                className={`message ${message.role}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="message-content">
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                    {message.role === 'assistant' && (
                      <Bot size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
                    )}
                    {message.role === 'user' && (
                      <User size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
                    )}
                    <div style={{ flex: 1 }}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="suggestions">
                          {message.suggestions.map((suggestion, index) => (
                            <motion.button
                              key={index}
                              className="suggestion"
                              onClick={() => handleSuggestionClick(suggestion)}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              {suggestion}
                            </motion.button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <span className="message-time">{formatTime(message.timestamp)}</span>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              className="message assistant"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="message-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Bot size={16} />
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <motion.div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.7)'
                      }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                    <motion.div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.7)'
                      }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.7)'
                      }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about tariffs, HTS codes, materials, or sourcing..."
            disabled={isLoading}
          />
          <motion.button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <Send size={20} />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface; 