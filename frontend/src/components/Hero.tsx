import React from 'react';
import { motion } from 'framer-motion';
import { Search, MessageCircle, BarChart3, ArrowRight, Sparkles } from 'lucide-react';

interface HeroProps {
  onNavigate: (view: string) => void;
}

const Hero: React.FC<HeroProps> = ({ onNavigate }) => {
  const features = [
    {
      icon: <Search />,
      title: 'HTS Lookup',
      description: 'Intelligent search with AI-powered suggestions',
      action: () => onNavigate('/hts')
    },
    {
      icon: <MessageCircle />,
      title: 'AI Chat',
      description: 'Conversational tariff assistance',
      action: () => onNavigate('/chat')
    },
    {
      icon: <BarChart3 />,
      title: 'Analytics',
      description: 'Comprehensive tariff insights',
      action: () => onNavigate('/dashboard')
    }
  ];

  return (
    <div className="hero">
      {/* Hero Section */}
      <motion.div 
        className="hero-content"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <motion.div
          className="hero-badge"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Sparkles size={16} />
          <span>AI-Powered Tariff Management</span>
        </motion.div>

        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          Intelligent HTS & Tariff
          <span className="gradient-text"> Management</span>
        </motion.h1>

        <motion.p
          className="hero-description"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          Streamline your import/export operations with AI-powered HTS code classification, 
          tariff calculations, and intelligent material analysis. Get instant insights and 
          optimize your global trade strategy.
        </motion.p>

        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <motion.button
            className="glass-button primary"
            onClick={() => onNavigate('/hts')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start HTS Lookup
            <ArrowRight size={20} />
          </motion.button>
          
          <motion.button
            className="glass-button secondary"
            onClick={() => onNavigate('/chat')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Chat with AI
            <MessageCircle size={20} />
          </motion.button>
        </motion.div>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        className="features-grid"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            className="glass-card feature-card"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
            whileHover={{ 
              scale: 1.02,
              y: -5
            }}
            onClick={feature.action}
          >
            <div className="feature-icon">
              {feature.icon}
            </div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            <motion.div
              className="feature-arrow"
              initial={{ x: 0 }}
              whileHover={{ x: 5 }}
              transition={{ duration: 0.2 }}
            >
              <ArrowRight size={16} />
            </motion.div>
          </motion.div>
        ))}
      </motion.div>

      {/* Stats Section */}
      <motion.div
        className="stats-section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 1.0 }}
      >
        <div className="stats-grid">
          <motion.div
            className="stat-item"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 1.1 }}
          >
            <div className="stat-number">99.9%</div>
            <div className="stat-label">Accuracy</div>
          </motion.div>
          
          <motion.div
            className="stat-item"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 1.2 }}
          >
            <div className="stat-number">2s</div>
            <div className="stat-label">Response Time</div>
          </motion.div>
          
          <motion.div
            className="stat-item"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 1.3 }}
          >
            <div className="stat-number">10K+</div>
            <div className="stat-label">HTS Codes</div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Hero; 