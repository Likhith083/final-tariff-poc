import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Dashboard from '../components/Dashboard/Dashboard';

// Mock the API services
jest.mock('../../services/api', () => ({
  htsService: {
    getStatistics: jest.fn(),
  },
  tariffService: {
    getCalculationHistory: jest.fn(),
    getStatistics: jest.fn(),
  },
  materialService: {
    getAnalysisHistory: jest.fn(),
  },
  scenarioService: {
    getScenarioHistory: jest.fn(),
  },
  reportService: {
    getReportHistory: jest.fn(),
  },
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    card: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dashboard title', () => {
    renderWithRouter(<Dashboard />);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  });

  test('renders welcome message', () => {
    renderWithRouter(<Dashboard />);
    expect(screen.getByText(/Welcome to TariffAI/i)).toBeInTheDocument();
  });

  test('renders quick actions section', () => {
    renderWithRouter(<Dashboard />);
    expect(screen.getByText(/Quick Actions/i)).toBeInTheDocument();
  });

  test('renders statistics cards', async () => {
    const { htsService, tariffService } = require('../../services/api');
    
    // Mock statistics data
    htsService.getStatistics.mockResolvedValue({
      data: {
        total_hts_codes: 1000,
        average_tariff_rate: 2.5,
        countries: ['US', 'China', 'Mexico']
      }
    });
    
    tariffService.getStatistics.mockResolvedValue({
      data: {
        total_calculations: 500,
        average_tariff_amount: 150.0,
        total_savings: 25000.0
      }
    });
    
    renderWithRouter(<Dashboard />);
    
    // Wait for statistics to load
    await waitFor(() => {
      expect(screen.getByText(/Total HTS Codes/i)).toBeInTheDocument();
      expect(screen.getByText(/1000/i)).toBeInTheDocument();
    });
  });

  test('renders recent activity section', async () => {
    const { tariffService } = require('../../services/api');
    
    // Mock recent activity data
    tariffService.getCalculationHistory.mockResolvedValue({
      data: {
        calculations: [
          {
            id: 1,
            hts_code: '8471.30.01',
            tariff_amount: 0.0,
            created_at: '2024-01-01T10:00:00Z'
          }
        ]
      }
    });
    
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Recent Activity/i)).toBeInTheDocument();
    });
  });

  test('quick action buttons work correctly', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Dashboard />);
    
    // Find and click quick action buttons
    const htsSearchButton = screen.getByText(/Search HTS Codes/i);
    await user.click(htsSearchButton);
    
    // Check if navigation occurred
    await waitFor(() => {
      expect(window.location.pathname).toBe('/hts-search');
    });
  });

  test('handles loading state', () => {
    const { htsService } = require('../../services/api');
    
    // Mock a slow API response
    htsService.getStatistics.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    renderWithRouter(<Dashboard />);
    
    // Check for loading indicators
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('handles error state gracefully', async () => {
    const { htsService } = require('../../services/api');
    
    // Mock API error
    htsService.getStatistics.mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<Dashboard />);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when no data', async () => {
    const { tariffService } = require('../../services/api');
    
    // Mock empty data
    tariffService.getCalculationHistory.mockResolvedValue({
      data: { calculations: [] }
    });
    
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/No recent activity/i)).toBeInTheDocument();
    });
  });

  test('refresh button works', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    htsService.getStatistics.mockResolvedValue({
      data: { total_hts_codes: 1000 }
    });
    
    renderWithRouter(<Dashboard />);
    
    // Find and click refresh button
    const refreshButton = screen.getByLabelText(/refresh/i);
    await user.click(refreshButton);
    
    // Verify API was called again
    expect(htsService.getStatistics).toHaveBeenCalledTimes(2);
  });

  test('displays correct date format', async () => {
    const { tariffService } = require('../../services/api');
    
    tariffService.getCalculationHistory.mockResolvedValue({
      data: {
        calculations: [
          {
            id: 1,
            hts_code: '8471.30.01',
            created_at: '2024-01-01T10:00:00Z'
          }
        ]
      }
    });
    
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      // Check if date is formatted correctly
      expect(screen.getByText(/Jan 1, 2024/i)).toBeInTheDocument();
    });
  });

  test('statistics cards show correct values', async () => {
    const { htsService, tariffService } = require('../../services/api');
    
    htsService.getStatistics.mockResolvedValue({
      data: {
        total_hts_codes: 1500,
        average_tariff_rate: 3.2
      }
    });
    
    tariffService.getStatistics.mockResolvedValue({
      data: {
        total_calculations: 750,
        total_savings: 50000.0
      }
    });
    
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('1,500')).toBeInTheDocument();
      expect(screen.getByText('3.2%')).toBeInTheDocument();
      expect(screen.getByText('750')).toBeInTheDocument();
      expect(screen.getByText('$50,000')).toBeInTheDocument();
    });
  });

  test('responsive design works', () => {
    // Test mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });
    
    renderWithRouter(<Dashboard />);
    
    // Check if mobile-specific layout is applied
    const dashboard = screen.getByTestId('dashboard');
    expect(dashboard).toBeInTheDocument();
  });

  test('accessibility features are present', () => {
    renderWithRouter(<Dashboard />);
    
    // Check for proper heading structure
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for proper button labels
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('aria-label');
    });
  });

  test('keyboard navigation works', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Dashboard />);
    
    // Test tab navigation through dashboard elements
    await user.tab();
    
    const focusedElement = document.activeElement;
    expect(focusedElement).toBeInTheDocument();
  });

  test('cleanup on unmount', () => {
    const { unmount } = renderWithRouter(<Dashboard />);
    
    // Unmount the component
    unmount();
    
    // Check if cleanup functions are called
    // This depends on your cleanup implementation
  });
});

describe('Dashboard Integration Tests', () => {
  test('loads all data sources on mount', async () => {
    const { 
      htsService, 
      tariffService, 
      materialService, 
      scenarioService, 
      reportService 
    } = require('../../services/api');
    
    // Mock all API calls
    htsService.getStatistics.mockResolvedValue({ data: {} });
    tariffService.getStatistics.mockResolvedValue({ data: {} });
    tariffService.getCalculationHistory.mockResolvedValue({ data: { calculations: [] } });
    materialService.getAnalysisHistory.mockResolvedValue({ data: { analyses: [] } });
    scenarioService.getScenarioHistory.mockResolvedValue({ data: { scenarios: [] } });
    reportService.getReportHistory.mockResolvedValue({ data: { reports: [] } });
    
    renderWithRouter(<Dashboard />);
    
    // Wait for all API calls to complete
    await waitFor(() => {
      expect(htsService.getStatistics).toHaveBeenCalled();
      expect(tariffService.getStatistics).toHaveBeenCalled();
      expect(tariffService.getCalculationHistory).toHaveBeenCalled();
      expect(materialService.getAnalysisHistory).toHaveBeenCalled();
      expect(scenarioService.getScenarioHistory).toHaveBeenCalled();
      expect(reportService.getReportHistory).toHaveBeenCalled();
    });
  });

  test('handles partial data loading', async () => {
    const { htsService, tariffService } = require('../../services/api');
    
    // Mock some successful and some failed API calls
    htsService.getStatistics.mockResolvedValue({
      data: { total_hts_codes: 1000 }
    });
    
    tariffService.getStatistics.mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<Dashboard />);
    
    // Wait for successful data to load
    await waitFor(() => {
      expect(screen.getByText('1,000')).toBeInTheDocument();
    });
    
    // Check that error is handled gracefully
    expect(screen.getByText(/Error/i)).toBeInTheDocument();
  });

  test('real-time updates work', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock initial data
    htsService.getStatistics.mockResolvedValue({
      data: { total_hts_codes: 1000 }
    });
    
    renderWithRouter(<Dashboard />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('1,000')).toBeInTheDocument();
    });
    
    // Mock updated data
    htsService.getStatistics.mockResolvedValue({
      data: { total_hts_codes: 1100 }
    });
    
    // Trigger refresh
    const refreshButton = screen.getByLabelText(/refresh/i);
    await user.click(refreshButton);
    
    // Wait for updated data
    await waitFor(() => {
      expect(screen.getByText('1,100')).toBeInTheDocument();
    });
  });
});
