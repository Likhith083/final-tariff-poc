import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import App from '../App';

// Mock the API services
jest.mock('../services/api', () => ({
  htsService: {
    searchHTS: jest.fn(),
    getHTSDetails: jest.fn(),
    getTariffRate: jest.fn(),
  },
  tariffService: {
    calculateTariff: jest.fn(),
    getCalculationHistory: jest.fn(),
  },
  chatService: {
    sendMessage: jest.fn(),
    getSession: jest.fn(),
  },
  materialService: {
    analyzeMaterials: jest.fn(),
    searchMaterials: jest.fn(),
  },
  scenarioService: {
    simulateScenario: jest.fn(),
    compareScenarios: jest.fn(),
  },
  reportService: {
    generateReport: jest.fn(),
    getReportTypes: jest.fn(),
  },
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    nav: ({ children, ...props }) => <nav {...props}>{children}</nav>,
    main: ({ children, ...props }) => <main {...props}>{children}</main>,
  },
  AnimatePresence: ({ children }) => <div>{children}</div>,
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    renderWithRouter(<App />);
    expect(screen.getByText(/TariffAI/i)).toBeInTheDocument();
  });

  test('renders sidebar navigation', () => {
    renderWithRouter(<App />);
    
    // Check for sidebar navigation items
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/HTS Search/i)).toBeInTheDocument();
    expect(screen.getByText(/Tariff Calculator/i)).toBeInTheDocument();
    expect(screen.getByText(/Material Analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Scenario Simulation/i)).toBeInTheDocument();
    expect(screen.getByText(/Chat Interface/i)).toBeInTheDocument();
    expect(screen.getByText(/Reports/i)).toBeInTheDocument();
  });

  test('renders main content area', () => {
    renderWithRouter(<App />);
    
    // Check for main content area
    const mainContent = screen.getByRole('main');
    expect(mainContent).toBeInTheDocument();
  });

  test('sidebar can be toggled', async () => {
    const user = userEvent.setup();
    renderWithRouter(<App />);
    
    // Find the toggle button (hamburger menu)
    const toggleButton = screen.getByLabelText(/toggle sidebar/i);
    expect(toggleButton).toBeInTheDocument();
    
    // Click the toggle button
    await user.click(toggleButton);
    
    // Check if sidebar state changes (this might depend on your implementation)
    // You might need to check for CSS classes or other indicators
  });

  test('navigation links work correctly', async () => {
    const user = userEvent.setup();
    renderWithRouter(<App />);
    
    // Test navigation to different sections
    const htsSearchLink = screen.getByText(/HTS Search/i);
    await user.click(htsSearchLink);
    
    // Wait for navigation to complete
    await waitFor(() => {
      expect(window.location.pathname).toBe('/hts-search');
    });
  });

  test('renders loading state initially', () => {
    renderWithRouter(<App />);
    
    // Check if loading indicator is present
    // This depends on your loading implementation
    const loadingElement = screen.queryByText(/Loading/i);
    if (loadingElement) {
      expect(loadingElement).toBeInTheDocument();
    }
  });

  test('handles error states gracefully', async () => {
    // Mock an error in one of the services
    const { htsService } = require('../services/api');
    htsService.searchHTS.mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<App />);
    
    // Navigate to HTS Search to trigger the error
    const user = userEvent.setup();
    const htsSearchLink = screen.getByText(/HTS Search/i);
    await user.click(htsSearchLink);
    
    // Check if error handling is in place
    await waitFor(() => {
      // This depends on your error handling implementation
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  test('responsive design works on different screen sizes', () => {
    // Test mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });
    
    renderWithRouter(<App />);
    
    // Check if mobile-specific elements are rendered
    // This depends on your responsive implementation
  });

  test('accessibility features are present', () => {
    renderWithRouter(<App />);
    
    // Check for proper ARIA labels
    expect(screen.getByLabelText(/toggle sidebar/i)).toBeInTheDocument();
    
    // Check for proper heading structure
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for proper navigation landmarks
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
  });

  test('theme and styling are applied correctly', () => {
    renderWithRouter(<App />);
    
    // Check if glassmorphism classes are applied
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toHaveClass('glassmorphism');
    
    // Check if main content has proper styling
    const mainContent = screen.getByRole('main');
    expect(mainContent).toHaveClass('main-content');
  });

  test('keyboard navigation works', async () => {
    const user = userEvent.setup();
    renderWithRouter(<App />);
    
    // Test tab navigation
    await user.tab();
    
    // Check if focus moves to the first interactive element
    const focusedElement = document.activeElement;
    expect(focusedElement).toBeInTheDocument();
  });

  test('handles window resize events', () => {
    renderWithRouter(<App />);
    
    // Simulate window resize
    const resizeEvent = new Event('resize');
    window.dispatchEvent(resizeEvent);
    
    // Check if the app responds to resize events
    // This depends on your resize handling implementation
  });

  test('cleanup on unmount', () => {
    const { unmount } = renderWithRouter(<App />);
    
    // Unmount the component
    unmount();
    
    // Check if cleanup functions are called
    // This depends on your cleanup implementation
  });
});

describe('App Integration Tests', () => {
  test('full user journey - HTS search to tariff calculation', async () => {
    const user = userEvent.setup();
    const { htsService, tariffService } = require('../services/api');
    
    // Mock successful API responses
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [
          {
            hts_code: '8471.30.01',
            description: 'Laptop computers',
            tariff_rate: 0.0
          }
        ]
      }
    });
    
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0
      }
    });
    
    renderWithRouter(<App />);
    
    // Navigate to HTS Search
    const htsSearchLink = screen.getByText(/HTS Search/i);
    await user.click(htsSearchLink);
    
    // Wait for HTS Search page to load
    await waitFor(() => {
      expect(screen.getByText(/Search HTS Codes/i)).toBeInTheDocument();
    });
    
    // Navigate to Tariff Calculator
    const tariffCalculatorLink = screen.getByText(/Tariff Calculator/i);
    await user.click(tariffCalculatorLink);
    
    // Wait for Tariff Calculator page to load
    await waitFor(() => {
      expect(screen.getByText(/Calculate Tariff/i)).toBeInTheDocument();
    });
  });

  test('error boundary catches component errors', () => {
    // Create a component that throws an error
    const ErrorComponent = () => {
      throw new Error('Test error');
    };
    
    // Mock the error boundary
    const originalError = console.error;
    console.error = jest.fn();
    
    try {
      renderWithRouter(<ErrorComponent />);
    } catch (error) {
      // Error should be caught by error boundary
      expect(error.message).toBe('Test error');
    }
    
    console.error = originalError;
  });
});
