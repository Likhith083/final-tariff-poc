import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, MessageCircle, BarChart3, Menu, X } from 'lucide-react';
import './App.css';
import QuickLinks from './components/QuickLinks';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

// Components
import Hero from './components/Hero';
import HTSSearch from './components/HTSSearch';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import TariffCalculator from './components/TariffCalculator';
import ScenarioAnalysis from './components/ScenarioAnalysis';
import MaterialAnalyzer from './components/MaterialAnalyzer';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorPage from './components/ErrorPage';
import StatusIndicator from './components/StatusIndicator';

// Navigation component that uses router hooks
function Navigation({ sidebarOpen, setSidebarOpen }: { sidebarOpen: boolean; setSidebarOpen: (open: boolean) => void }) {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    // Remove the Home button
    // { id: 'hero', label: 'Home', icon: <Search />, path: '/' },
    { id: 'hts', label: 'HTS Lookup', icon: <Search />, path: '/hts' },
    { id: 'chat', label: 'AI Chat', icon: <MessageCircle />, path: '/chat' },
    { id: 'calculator', label: 'Calculator', icon: <BarChart3 />, path: '/calculator' },
    { id: 'scenario', label: 'Scenarios', icon: <BarChart3 />, path: '/scenario' },
    { id: 'analyzer', label: 'Materials', icon: <BarChart3 />, path: '/analyzer' },
    { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 />, path: '/dashboard' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname === path;
  };

  return (
    <>
      {/* Glass Navigation */}
      <motion.nav 
        className="glass-nav"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="nav-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <motion.div 
              className="logo"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              style={{ cursor: 'pointer', marginLeft: 8 }}
            >
              🚢 TariffAI
            </motion.div>
            <div style={{ marginLeft: 'auto', marginRight: 16 }}>
              <StatusIndicator />
            </div>
          </div>
          
          <div className="nav-links">
            {navigationItems.map((item) => (
              <motion.button
                key={item.id}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {item.icon}
                <span>{item.label}</span>
              </motion.button>
            ))}
          </div>

          <motion.button
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {sidebarOpen ? <X /> : <Menu />}
          </motion.button>
        </div>
      </motion.nav>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            className="mobile-sidebar"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
          >
            <div className="sidebar-content">
              {navigationItems.map((item) => (
                <motion.button
                  key={item.id}
                  className={`sidebar-link ${isActive(item.path) ? 'active' : ''}`}
                  onClick={() => {
                    navigate(item.path);
                    setSidebarOpen(false);
                  }}
                  whileHover={{ x: 10 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// Navigation wrapper for Hero component
function HeroWrapper() {
  const navigate = useNavigate();
  return <Hero onNavigate={(path: string) => navigate(path)} />;
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [backendError, setBackendError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Check backend connectivity on app start
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          setIsLoading(false);
          setBackendError(false);
        } else {
          throw new Error('Backend not responding properly');
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsLoading(false);
        setBackendError(true);
        setErrorMessage('Unable to connect to backend server');
      }
    };

    checkBackend();
  }, []);

  const handleRetry = () => {
    setIsLoading(true);
    setBackendError(false);
    // Re-check backend connectivity
    setTimeout(() => {
      const checkBackend = async () => {
        try {
          const response = await fetch('http://localhost:8000/health');
          if (response.ok) {
            setIsLoading(false);
            setBackendError(false);
          } else {
            throw new Error('Backend not responding properly');
          }
        } catch (error) {
          setIsLoading(false);
          setBackendError(true);
        }
      };
      checkBackend();
    }, 1000);
  };

  // Show loading spinner while checking backend
  if (isLoading) {
    return (
      <div className="app">
        <div className="background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
        </div>
        <LoadingSpinner message="Connecting to Tariff AI..." size="large" />
      </div>
    );
  }

  // Show error page if backend is not available
  if (backendError) {
    return (
      <ErrorPage 
        error={errorMessage}
        onRetry={handleRetry}
        isBackendError={true}
      />
    );
  }

  return (
    <Router>
      <div className="app">
        {/* Animated Background */}
        <div className="background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
        </div>

        <Navigation sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<><HeroWrapper /> <QuickLinks /></>} />
            <Route path="/hts" element={<HTSSearch />} />
            <Route path="/chat" element={<ChatInterface />} />
            <Route path="/calculator" element={<TariffCalculator />} />
            <Route path="/scenario" element={<ScenarioAnalysis />} />
            <Route path="/analyzer" element={<MaterialAnalyzer />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
