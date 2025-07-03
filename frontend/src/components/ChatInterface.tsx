import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hello! I'm your AI tariff assistant. I can help you with HTS code lookups, tariff calculations, material analysis, and more. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };

    setMessages(prev => [...prev, aiMessage]);

    // Simulate streaming response
    const responses = [
      "I found the HTS code for your product. Based on your description, this appears to be **HTS 4015.19.0510** - Disposable gloves of vulcanized rubber other than hard rubber, surgical or medical use, with a tariff rate of **3.0%**.",
      "For **nitrile gloves**, the most common HTS code is **4015.19.0510** with a tariff rate of **3.0%**. This classification applies to disposable gloves used in medical and industrial applications.",
      "Based on your query about **cotton t-shirts**, the appropriate HTS code would be **6109.10.0010** with a tariff rate of **16.5%**. This covers men's or boys' cotton t-shirts."
    ];

    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    let currentText = '';
    
    for (let i = 0; i < randomResponse.length; i++) {
      currentText += randomResponse[i];
      setMessages(prev => 
        prev.map(msg => 
          msg.id === aiMessage.id 
            ? { ...msg, content: currentText }
            : msg
        )
      );
      await new Promise(resolve => setTimeout(resolve, 30));
    }

    // Remove streaming flag
    setMessages(prev => 
      prev.map(msg => 
        msg.id === aiMessage.id 
          ? { ...msg, isStreaming: false }
          : msg
      )
    );

    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="chat-interface">
      <motion.div
        className="chat-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1>
          <Bot size={24} />
          AI Tariff Assistant
        </h1>
        <p>Get instant help with HTS codes, tariff calculations, and trade compliance</p>
      </motion.div>

      {/* Chat Messages */}
      <motion.div
        className="chat-container"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="glass-card chat-card">
          <div className="messages-container">
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.type}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <div className="message-avatar">
                    {message.type === 'ai' ? <Bot size={20} /> : <User size={20} />}
                  </div>
                  
                  <div className="message-content">
                    <div className="message-text">
                      {message.content}
                      {message.isStreaming && (
                        <motion.span
                          className="typing-indicator"
                          animate={{ opacity: [0.5, 1, 0.5] }}
                          transition={{ duration: 1, repeat: Infinity }}
                        >
                          |
                        </motion.span>
                      )}
                    </div>
                    
                    <div className="message-actions">
                      <span className="message-time">
                        {message.timestamp.toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                      
                      {message.type === 'ai' && !message.isStreaming && (
                        <div className="action-buttons">
                          <motion.button
                            className="action-button"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => copyMessage(message.content)}
                          >
                            <Copy size={16} />
                          </motion.button>
                          <motion.button
                            className="action-button"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <ThumbsUp size={16} />
                          </motion.button>
                          <motion.button
                            className="action-button"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <ThumbsDown size={16} />
                          </motion.button>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {isLoading && (
              <motion.div
                className="message ai"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="message-avatar">
                  <Bot size={20} />
                </div>
                <div className="message-content">
                  <div className="message-text">
                    <motion.div
                      className="loading-dots"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <motion.span
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                      >
                        •
                      </motion.span>
                      <motion.span
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                      >
                        •
                      </motion.span>
                      <motion.span
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                      >
                        •
                      </motion.span>
                    </motion.div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Section */}
          <div className="input-section">
            <div className="input-container">
              <textarea
                className="glass-input chat-input"
                placeholder="Ask me about HTS codes, tariff rates, or trade compliance..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                rows={1}
                disabled={isLoading}
              />
              <motion.button
                className="send-button"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Send size={20} />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        className="quick-actions"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="glass-card">
          <h3>
            <Sparkles size={20} />
            Quick Actions
          </h3>
          <div className="quick-buttons">
            {[
              'Find HTS code for nitrile gloves',
              'Calculate tariff for cotton t-shirts',
              'Material composition analysis',
              'Alternative sourcing suggestions'
            ].map((action, index) => (
              <motion.button
                key={action}
                className="quick-button"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setInputMessage(action)}
              >
                {action}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ChatInterface; 