import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wifi, Database, Bot, AlertCircle } from 'lucide-react';

interface StatusIndicatorProps {
  className?: string;
}

interface ServiceStatus {
  backend: boolean;
  ai: boolean;
  knowledgeBase: boolean;
  backendError?: string;
  aiError?: string;
  kbError?: string;
  kbStats?: {
    total_documents: number;
    collection_name: string;
  };
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ className }) => {
  const [status, setStatus] = useState<ServiceStatus>({
    backend: false,
    ai: false,
    knowledgeBase: false
  });
  const [isExpanded, setIsExpanded] = useState(false);

  const checkServiceStatus = async () => {
    const newStatus: ServiceStatus = {
      backend: false,
      ai: false,
      knowledgeBase: false
    };

    try {
      // Check backend health
      const healthResponse = await fetch('http://localhost:8000/health', {
        method: 'GET'
      });
      
      if (healthResponse.ok) {
        newStatus.backend = true;
        
        // Check AI service by sending a test message
        try {
          const aiResponse = await fetch('http://localhost:8000/api/v1/chat/send', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: 'What is the tariff for importing drill from China?',
              session_id: null,
              session_title: 'Tariff AI Status Check'
            })
          });
          
          if (aiResponse.ok) {
            const aiData = await aiResponse.json();
            // Check if we get a proper Tariff Management AI response
            if (aiData.message && 
                !aiData.message.includes('unavailable') && 
                !aiData.message.includes('experiencing technical difficulties') &&
                !aiData.message.includes('currently unable') &&
                !aiData.message.includes('AI service is currently') &&
                !aiData.message.includes('currently experiencing technical difficulties') &&
                !aiData.message.includes('currently unable to access my AI capabilities') &&
                !aiData.message.includes('try again later')) {
              newStatus.ai = true;
            } else {
              newStatus.aiError = 'Tariff AI responding with fallback messages';
            }
          } else {
            newStatus.aiError = 'AI service error';
          }
        } catch (aiError) {
          newStatus.aiError = 'AI service connection failed';
        }
        
        // Check knowledge base
        try {
          const kbResponse = await fetch('http://localhost:8000/api/v1/chat/knowledge-stats', {
            method: 'GET'
          });
          
          if (kbResponse.ok) {
            const kbData = await kbResponse.json();
            if (kbData.total_documents > 0) {
              newStatus.knowledgeBase = true;
              newStatus.kbStats = kbData;
            } else {
              newStatus.kbError = 'Knowledge base empty';
            }
          } else {
            newStatus.kbError = 'Knowledge base unavailable';
          }
        } catch (kbError) {
          newStatus.kbError = 'Knowledge base connection failed';
        }
        
      } else {
        newStatus.backendError = 'Backend service unavailable';
      }
    } catch (error) {
      newStatus.backendError = 'Backend connection failed';
    }

    setStatus(newStatus);
  };

  useEffect(() => {
    checkServiceStatus();
    const interval = setInterval(checkServiceStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (status.backend && status.ai && status.knowledgeBase) {
      return '#10b981'; // Green - all good
    } else if (status.backend) {
      return '#f59e0b'; // Yellow - partial
    } else {
      return '#ef4444'; // Red - backend down
    }
  };

  const getStatusText = () => {
    if (status.backend && status.ai && status.knowledgeBase) {
      return 'All Systems Operational';
    } else if (status.backend) {
      return 'Partial Service';
    } else {
      return 'Service Unavailable';
    }
  };

  return (
    <div className={`status-indicator ${className}`}>
      <motion.div
        className="status-button"
        onClick={() => setIsExpanded(!isExpanded)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem 0.75rem',
          background: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          cursor: 'pointer',
          backdropFilter: 'blur(10px)',
          color: '#fff'
        }}
      >
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: getStatusColor(),
            boxShadow: `0 0 6px ${getStatusColor()}`
          }}
        />
        <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>
          {getStatusText()}
        </span>
      </motion.div>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="status-details"
          style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: '0.5rem',
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: '12px',
            backdropFilter: 'blur(20px)',
            color: '#333',
            minWidth: '280px',
            zIndex: 1000,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}
        >
          <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', fontWeight: 600 }}>
            Service Status
          </h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Wifi size={16} color={status.backend ? '#10b981' : '#ef4444'} />
              <span style={{ fontSize: '0.8rem' }}>
                Backend: {status.backend ? 'Connected' : (status.backendError || 'Disconnected')}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Bot size={16} color={status.ai ? '#10b981' : '#ef4444'} />
              <span style={{ fontSize: '0.8rem' }}>
                AI (Ollama llama3.2:3b): {status.ai ? 'Available' : (status.aiError || 'Unavailable')}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Database size={16} color={status.knowledgeBase ? '#10b981' : '#ef4444'} />
              <span style={{ fontSize: '0.8rem' }}>
                Knowledge Base: {status.knowledgeBase ? 
                  `${status.kbStats?.total_documents || 0} documents` : 
                  (status.kbError || 'Unavailable')
                }
              </span>
            </div>
          </div>
          
          <div style={{ 
            marginTop: '0.75rem', 
            padding: '0.5rem', 
            background: 'rgba(59, 130, 246, 0.1)', 
            borderRadius: '6px',
            fontSize: '0.75rem',
            color: '#1e40af'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <AlertCircle size={12} />
              <span>Status updates every 30 seconds</span>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default StatusIndicator;
