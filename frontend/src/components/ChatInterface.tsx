import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import jsPDF from 'jspdf';

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
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [kbText, setKbText] = useState("");
  const [kbTextUploading, setKbTextUploading] = useState(false);
  const [kbTextMessage, setKbTextMessage] = useState("");

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => { setSelectedFile(e.target.files?.[0] || null); };

  const handleUploadKnowledgeClick = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadMessage("");
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/upload-knowledge', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) setUploadMessage('Knowledge uploaded successfully!');
      else setUploadMessage(data.detail || 'Upload failed.');
    } catch (err) { setUploadMessage('Upload failed.'); }
    setUploading(false);
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    let y = 10;
    doc.setFontSize(16);
    doc.text('Tariff AI Chat Session', 10, y);
    y += 10;
    doc.setFontSize(12);
    messages.forEach((msg, idx) => {
      const prefix = msg.type === 'user' ? 'User: ' : 'AI: ';
      const lines = doc.splitTextToSize(prefix + msg.content, 180) as string[];
      lines.forEach((line: string) => {
        if (y > 270) { doc.addPage(); y = 10; }
        doc.text(line, 10, y);
        y += 7;
      });
      y += 3;
    });
    doc.save('tariff-ai-chat.pdf');
  };

  const handleKbTextUpload = async () => {
    if (!kbText.trim()) return;
    setKbTextUploading(true);
    setKbTextMessage("");
    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/upload-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: kbText })
      });
      const data = await res.json();
      if (res.ok) setKbTextMessage('Text added to knowledge base!');
      else setKbTextMessage(data.detail || 'Upload failed.');
    } catch (err) { setKbTextMessage('Upload failed.'); }
    setKbTextUploading(false);
    setKbText("");
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
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: '1rem' }}>
            <button className="glass-button primary" onClick={handleExportPDF}>
              Export
            </button>
          </div>
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

      <div style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        gap: '2rem',
        marginTop: '2.5rem',
        flexWrap: 'wrap',
      }}>
        {/* Upload File Card */}
        <div className="glass-card" style={{ width: 400, minHeight: 260, flex: 'none', marginBottom: '1.5rem' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1.2rem', color: '#22223b', marginBottom: '1rem' }}>Upload File to Knowledge Base</h3>
          <label className="glass-input" style={{ display: 'block', padding: '0.75rem 1rem', cursor: 'pointer', background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '12px', color: '#fff', fontWeight: 500, marginBottom: '1rem', textAlign: 'center' }}>
            <input type="file" accept=".pdf,.txt,.md,.doc,.docx" onChange={handleFileChange} style={{ display: 'none' }} />
            {selectedFile ? selectedFile.name : 'Choose File'}
          </label>
          <button type="button" className="glass-button primary" onClick={handleUploadKnowledgeClick} disabled={uploading || !selectedFile} style={{ width: '100%', marginBottom: '0.5rem' }}>
            {uploading ? 'Uploading...' : 'Upload to Knowledge Base'}
          </button>
          {uploadMessage && <div style={{ color: '#4ecdc4', fontWeight: 500, marginTop: '0.5rem' }}>{uploadMessage}</div>}
        </div>
        {/* Add Text Card */}
        <div className="glass-card" style={{ width: 400, minHeight: 260, flex: 'none', marginBottom: '1.5rem' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1.2rem', color: '#22223b', marginBottom: '1rem' }}>Add Text to Knowledge Base</h3>
          <textarea
            className="glass-input"
            style={{ minWidth: '100%', minHeight: '64px', background: 'rgba(255,255,255,0.15)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '12px', padding: '0.75rem 1rem', fontSize: '1rem', marginBottom: '1rem' }}
            placeholder="Paste or type text to add to the knowledge base..."
            value={kbText}
            onChange={e => setKbText(e.target.value)}
            disabled={kbTextUploading}
          />
          <button type="button" className="glass-button primary" onClick={handleKbTextUpload} disabled={kbTextUploading || !kbText.trim()} style={{ width: '100%', marginBottom: '0.5rem' }}>
            {kbTextUploading ? 'Uploading...' : 'Add Text to Knowledge Base'}
          </button>
          {kbTextMessage && <div style={{ color: '#4ecdc4', fontWeight: 500, marginTop: '0.5rem' }}>{kbTextMessage}</div>}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 