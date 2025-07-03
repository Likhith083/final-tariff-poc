import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Database, Server, Brain } from 'lucide-react';
import { chatService } from '../services/chatService';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState({ backend: 'checking', chroma: 'checking', ollama: 'checking' });
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
    checkAllStatus();
  }, []);

  const checkAllStatus = async () => {
    // Backend health
    let backend = 'checking', chroma = 'checking', ollama = 'checking';
    try {
      const health = await chatService.checkHealth();
      backend = health.status === 'ok' ? 'connected' : 'disconnected';
    } catch {
      backend = 'disconnected';
    }
    try {
      const chatHealth = await chatService.checkChatHealth();
      chroma = chatHealth.chroma === 'ok' ? 'connected' : 'disconnected';
      ollama = chatHealth.ollama === 'ok' ? 'connected' : 'disconnected';
    } catch {
      chroma = 'disconnected';
      ollama = 'disconnected';
    }
    setStatus({ backend, chroma, ollama });
  };

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
        content: response.message || response.response || "(No response)",
        timestamp: new Date(),
        suggestions: response.suggestions || []
      };
      setMessages(prev => [...prev, assistantMessage]);
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }
    } catch (error) {
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

  // Status bar rendering
  const statusColor = (s) => s === 'connected' ? '#10b981' : (s === 'checking' ? '#f59e0b' : '#ef4444');
  const statusText = (s) => s === 'connected' ? 'Connected' : (s === 'checking' ? 'Checking...' : 'Disconnected');

  return (
    <div className="chat-outer">
      <div className="chat-status-bar" style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginBottom: '1rem', padding: '0.75rem 1rem', borderRadius: '0.75rem', background: 'rgba(30,41,59,0.7)', color: '#fff', fontSize: '0.95rem' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Server size={16} color={statusColor(status.backend)} /> Backend: <b style={{ color: statusColor(status.backend) }}>{statusText(status.backend)}</b>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={16} color={statusColor(status.chroma)} /> Knowledge Base: <b style={{ color: statusColor(status.chroma) }}>{statusText(status.chroma)}</b>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Brain size={16} color={statusColor(status.ollama)} /> LLM: <b style={{ color: statusColor(status.ollama) }}>{statusText(status.ollama)}</b>
        </span>
        <button onClick={checkAllStatus} style={{ marginLeft: 'auto', background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '0.95rem', textDecoration: 'underline' }}>Refresh</button>
      </div>
      <motion.div
        className="glass-card chat-main"
        initial={{ scale: 0.98, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ boxShadow: '0 2px 16px rgba(0,0,0,0.08)', background: 'rgba(30,41,59,0.95)', color: '#f1f5f9', borderRadius: '1rem', padding: '2rem', maxWidth: 700, margin: '0 auto' }}
      >
        <div className="chat-container" style={{ minHeight: 400 }}>
          <div className="chat-messages" style={{ marginBottom: '1rem' }}>
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.role}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  style={{ background: message.role === 'assistant' ? 'rgba(99,102,241,0.08)' : 'rgba(16,185,129,0.08)', color: '#f1f5f9', borderRadius: '0.75rem', padding: '1rem', marginBottom: '0.5rem', fontSize: '1rem', lineHeight: 1.6 }}
                >
                  <div className="message-content" style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                    {message.role === 'assistant' && (
                      <Bot size={18} style={{ marginTop: '2px', flexShrink: 0, color: '#6366f1' }} />
                    )}
                    {message.role === 'user' && (
                      <User size={18} style={{ marginTop: '2px', flexShrink: 0, color: '#10b981' }} />
                    )}
                    <div style={{ flex: 1 }}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="suggestions" style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                          {message.suggestions.map((suggestion, index) => (
                            <motion.button
                              key={index}
                              className="suggestion"
                              onClick={() => handleSuggestionClick(suggestion)}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              style={{ background: '#334155', color: '#fff', border: 'none', borderRadius: '0.5rem', padding: '0.5rem 1rem', cursor: 'pointer', fontSize: '0.95rem' }}
                            >
                              {suggestion}
                            </motion.button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className="message-time" style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.5rem', display: 'block' }}>{formatTime(message.timestamp)}</span>
                </motion.div>
              ))}
            </AnimatePresence>
            {isLoading && (
              <motion.div
                className="message assistant"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ background: 'rgba(99,102,241,0.08)', color: '#f1f5f9', borderRadius: '0.75rem', padding: '1rem', marginBottom: '0.5rem', fontSize: '1rem', lineHeight: 1.6 }}
              >
                <div className="message-content" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Bot size={18} style={{ color: '#6366f1' }} />
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <motion.div
                      style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'rgba(255,255,255,0.7)' }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                    <motion.div
                      style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'rgba(255,255,255,0.7)' }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'rgba(255,255,255,0.7)' }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                    />
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <form className="chat-input-form" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }} onSubmit={e => { e.preventDefault(); handleSendMessage(); }}>
            <input
              type="text"
              className="chat-input"
              placeholder="Type your message..."
              value={inputMessage}
              onChange={e => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              style={{ flex: 1, padding: '1rem', borderRadius: '0.5rem', border: '1px solid #334155', background: '#1e293b', color: '#f1f5f9', fontSize: '1rem' }}
            />
            <button
              type="submit"
              className="send-button"
              disabled={!inputMessage.trim() || isLoading}
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: '#fff', border: 'none', borderRadius: '0.5rem', padding: '0.75rem 1.5rem', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', transition: 'all 0.3s' }}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default ChatInterface; 