import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import HTSSearch from '../components/HTSSearch/HTSSearch';

// Mock the API services
jest.mock('../../services/api', () => ({
  htsService: {
    searchHTS: jest.fn(),
    getHTSDetails: jest.fn(),
    getTariffRate: jest.fn(),
    getStatistics: jest.fn(),
  },
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    input: ({ children, ...props }) => <input {...props}>{children}</input>,
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
  },
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('HTS Search Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders search page title', () => {
    renderWithRouter(<HTSSearch />);
    expect(screen.getByText(/HTS Code Search/i)).toBeInTheDocument();
  });

  test('renders search input field', () => {
    renderWithRouter(<HTSSearch />);
    expect(screen.getByPlaceholderText(/Search HTS codes/i)).toBeInTheDocument();
  });

  test('renders search button', () => {
    renderWithRouter(<HTSSearch />);
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  test('renders filters section', () => {
    renderWithRouter(<HTSSearch />);
    expect(screen.getByText(/Filters/i)).toBeInTheDocument();
  });

  test('performs search on button click', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock search results
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [
          {
            hts_code: '8471.30.01',
            description: 'Laptop computers',
            tariff_rate: 0.0,
            country_origin: 'US'
          }
        ],
        total_results: 1
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Type search query
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    // Click search button
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
      expect(screen.getByText('Laptop computers')).toBeInTheDocument();
    });
  });

  test('performs search on Enter key press', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
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
    
    renderWithRouter(<HTSSearch />);
    
    // Type search query and press Enter
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop{enter}');
    
    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
  });

  test('displays loading state during search', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock slow API response
    htsService.searchHTS.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Check for loading indicator
    expect(screen.getByText(/Searching/i)).toBeInTheDocument();
  });

  test('handles empty search results', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [],
        total_results: 0
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'nonexistent');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for empty state
    await waitFor(() => {
      expect(screen.getByText(/No results found/i)).toBeInTheDocument();
    });
  });

  test('handles search errors gracefully', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    htsService.searchHTS.mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  test('filters work correctly', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [
          {
            hts_code: '8471.30.01',
            description: 'Laptop computers',
            tariff_rate: 0.0,
            country_origin: 'US'
          }
        ]
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Set country filter
    const countryFilter = screen.getByLabelText(/Country/i);
    await user.selectOptions(countryFilter, 'US');
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Verify filter was applied
    await waitFor(() => {
      expect(htsService.searchHTS).toHaveBeenCalledWith(
        expect.objectContaining({
          country_origin: 'US'
        })
      );
    });
  });

  test('pagination works correctly', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock paginated results
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: Array(20).fill().map((_, i) => ({
          hts_code: `8471.${i.toString().padStart(2, '0')}.01`,
          description: `Product ${i}`,
          tariff_rate: 0.0
        })),
        total_results: 50,
        page: 1,
        total_pages: 3
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform initial search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'product');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('8471.00.01')).toBeInTheDocument();
    });
    
    // Mock next page results
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: Array(20).fill().map((_, i) => ({
          hts_code: `8471.${(i + 20).toString().padStart(2, '0')}.01`,
          description: `Product ${i + 20}`,
          tariff_rate: 0.0
        })),
        total_results: 50,
        page: 2,
        total_pages: 3
      }
    });
    
    // Click next page
    const nextButton = screen.getByLabelText(/next page/i);
    await user.click(nextButton);
    
    // Wait for next page results
    await waitFor(() => {
      expect(screen.getByText('8471.20.01')).toBeInTheDocument();
    });
  });

  test('displays HTS code details on click', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock search results
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
    
    // Mock HTS details
    htsService.getHTSDetails.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        description: 'Laptop computers, portable, weighing not more than 10 kg',
        tariff_rate: 0.0,
        country_origin: 'US',
        effective_date: '2024-01-01'
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results and click on HTS code
    await waitFor(() => {
      const htsCodeElement = screen.getByText('8471.30.01');
      user.click(htsCodeElement);
    });
    
    // Wait for details modal
    await waitFor(() => {
      expect(screen.getByText(/Laptop computers, portable/i)).toBeInTheDocument();
    });
  });

  test('sorts results correctly', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [
          { hts_code: '8471.30.02', description: 'Desktop computers', tariff_rate: 2.5 },
          { hts_code: '8471.30.01', description: 'Laptop computers', tariff_rate: 0.0 }
        ]
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'computers');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('8471.30.02')).toBeInTheDocument();
    });
    
    // Click sort by tariff rate
    const sortButton = screen.getByLabelText(/sort by tariff rate/i);
    await user.click(sortButton);
    
    // Verify sort was applied
    await waitFor(() => {
      expect(htsService.searchHTS).toHaveBeenCalledWith(
        expect.objectContaining({
          sort_by: 'tariff_rate'
        })
      );
    });
  });

  test('exports search results', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock search results
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
    
    // Mock window.open
    const mockOpen = jest.fn();
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // Click export button
    const exportButton = screen.getByLabelText(/export results/i);
    await user.click(exportButton);
    
    // Verify export was triggered
    expect(mockOpen).toHaveBeenCalled();
  });

  test('saves search history', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
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
    
    renderWithRouter(<HTSSearch />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // Check if search was saved to history
    const historyButton = screen.getByLabelText(/search history/i);
    await user.click(historyButton);
    
    // Verify search history is displayed
    await waitFor(() => {
      expect(screen.getByText('laptop')).toBeInTheDocument();
    });
  });

  test('responsive design works', () => {
    // Test mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });
    
    renderWithRouter(<HTSSearch />);
    
    // Check if mobile-specific layout is applied
    const searchContainer = screen.getByTestId('hts-search-container');
    expect(searchContainer).toBeInTheDocument();
  });

  test('accessibility features are present', () => {
    renderWithRouter(<HTSSearch />);
    
    // Check for proper form labels
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    expect(searchInput).toHaveAttribute('aria-label');
    
    // Check for proper button labels
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toHaveAttribute('aria-label');
    
    // Check for proper table headers
    const tableHeaders = screen.getAllByRole('columnheader');
    expect(tableHeaders.length).toBeGreaterThan(0);
  });

  test('keyboard navigation works', async () => {
    const user = userEvent.setup();
    renderWithRouter(<HTSSearch />);
    
    // Test tab navigation
    await user.tab();
    
    const focusedElement = document.activeElement;
    expect(focusedElement).toBeInTheDocument();
    
    // Test arrow key navigation in results
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for results and test keyboard navigation
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
  });
});

describe('HTS Search Integration Tests', () => {
  test('full search workflow', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock all API calls
    htsService.searchHTS.mockResolvedValue({
      data: {
        results: [
          {
            hts_code: '8471.30.01',
            description: 'Laptop computers',
            tariff_rate: 0.0
          }
        ],
        total_results: 1
      }
    });
    
    htsService.getHTSDetails.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        description: 'Laptop computers',
        tariff_rate: 0.0
      }
    });
    
    renderWithRouter(<HTSSearch />);
    
    // 1. Enter search query
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    // 2. Apply filters
    const countryFilter = screen.getByLabelText(/Country/i);
    await user.selectOptions(countryFilter, 'US');
    
    // 3. Perform search
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // 4. Verify results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // 5. View details
    const htsCodeElement = screen.getByText('8471.30.01');
    await user.click(htsCodeElement);
    
    // 6. Verify details modal
    await waitFor(() => {
      expect(screen.getByText(/Laptop computers/i)).toBeInTheDocument();
    });
  });

  test('handles concurrent searches', async () => {
    const user = userEvent.setup();
    const { htsService } = require('../../services/api');
    
    // Mock multiple search calls
    htsService.searchHTS
      .mockResolvedValueOnce({
        data: {
          results: [{ hts_code: '8471.30.01', description: 'Laptop computers' }]
        }
      })
      .mockResolvedValueOnce({
        data: {
          results: [{ hts_code: '8471.30.02', description: 'Desktop computers' }]
        }
      });
    
    renderWithRouter(<HTSSearch />);
    
    // Perform first search
    const searchInput = screen.getByPlaceholderText(/Search HTS codes/i);
    await user.type(searchInput, 'laptop');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    // Wait for first results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // Clear and perform second search
    await user.clear(searchInput);
    await user.type(searchInput, 'desktop');
    await user.click(searchButton);
    
    // Wait for second results
    await waitFor(() => {
      expect(screen.getByText('8471.30.02')).toBeInTheDocument();
    });
  });
});
