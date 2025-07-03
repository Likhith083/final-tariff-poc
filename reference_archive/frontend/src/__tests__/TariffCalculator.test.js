import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import TariffCalculator from '../components/TariffCalculator/TariffCalculator';

// Mock the API services
jest.mock('../../services/api', () => ({
  tariffService: {
    calculateTariff: jest.fn(),
    getCalculationHistory: jest.fn(),
    getStatistics: jest.fn(),
  },
  htsService: {
    searchHTS: jest.fn(),
    getHTSDetails: jest.fn(),
  },
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    form: ({ children, ...props }) => <form {...props}>{children}</form>,
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

describe('Tariff Calculator Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders calculator page title', () => {
    renderWithRouter(<TariffCalculator />);
    expect(screen.getByText(/Tariff Calculator/i)).toBeInTheDocument();
  });

  test('renders calculation form', () => {
    renderWithRouter(<TariffCalculator />);
    expect(screen.getByText(/Calculate Tariff/i)).toBeInTheDocument();
  });

  test('renders input fields', () => {
    renderWithRouter(<TariffCalculator />);
    expect(screen.getByLabelText(/HTS Code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Material Cost/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Country of Origin/i)).toBeInTheDocument();
  });

  test('performs tariff calculation', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock calculation result
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0,
        currency: 'USD'
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Fill in form fields
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const countrySelect = screen.getByLabelText(/Country of Origin/i);
    await user.selectOptions(countrySelect, 'US');
    
    // Submit form
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for calculation result
    await waitFor(() => {
      expect(screen.getByText(/Tariff Rate: 0.0%/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Landed Cost: \$500.00/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    const user = userEvent.setup();
    renderWithRouter(<TariffCalculator />);
    
    // Try to submit without filling required fields
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Check for validation errors
    expect(screen.getByText(/HTS Code is required/i)).toBeInTheDocument();
    expect(screen.getByText(/Material Cost is required/i)).toBeInTheDocument();
  });

  test('validates numeric input', async () => {
    const user = userEvent.setup();
    renderWithRouter(<TariffCalculator />);
    
    // Enter invalid numeric value
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, 'invalid');
    
    // Check for validation error
    expect(screen.getByText(/Material Cost must be a valid number/i)).toBeInTheDocument();
  });

  test('handles calculation errors gracefully', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock API error
    tariffService.calculateTariff.mockRejectedValue(new Error('Calculation failed'));
    
    renderWithRouter(<TariffCalculator />);
    
    // Fill in form and submit
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  test('displays loading state during calculation', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock slow API response
    tariffService.calculateTariff.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    renderWithRouter(<TariffCalculator />);
    
    // Fill in form and submit
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Check for loading indicator
    expect(screen.getByText(/Calculating/i)).toBeInTheDocument();
  });

  test('saves calculation to history', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Perform calculation
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for calculation to complete
    await waitFor(() => {
      expect(screen.getByText(/Tariff Rate: 0.0%/i)).toBeInTheDocument();
    });
    
    // Check if calculation was saved
    const saveButton = screen.getByLabelText(/save calculation/i);
    await user.click(saveButton);
    
    // Verify save confirmation
    expect(screen.getByText(/Calculation saved/i)).toBeInTheDocument();
  });

  test('displays calculation history', async () => {
    const { tariffService } = require('../../services/api');
    
    // Mock calculation history
    tariffService.getCalculationHistory.mockResolvedValue({
      data: {
        calculations: [
          {
            id: 1,
            hts_code: '8471.30.01',
            tariff_amount: 0.0,
            total_landed_cost: 500.0,
            created_at: '2024-01-01T10:00:00Z'
          }
        ]
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Wait for history to load
    await waitFor(() => {
      expect(screen.getByText(/Calculation History/i)).toBeInTheDocument();
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
  });

  test('allows editing previous calculations', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock calculation history
    tariffService.getCalculationHistory.mockResolvedValue({
      data: {
        calculations: [
          {
            id: 1,
            hts_code: '8471.30.01',
            material_cost: 500.0,
            tariff_amount: 0.0,
            total_landed_cost: 500.0
          }
        ]
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Wait for history to load
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // Click on history item to load into form
    const historyItem = screen.getByText('8471.30.01');
    await user.click(historyItem);
    
    // Verify form is populated
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    expect(htsCodeInput.value).toBe('8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    expect(materialCostInput.value).toBe('500');
  });

  test('supports different currencies', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0,
        currency: 'EUR'
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Select different currency
    const currencySelect = screen.getByLabelText(/Currency/i);
    await user.selectOptions(currencySelect, 'EUR');
    
    // Fill in form and calculate
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for result with correct currency
    await waitFor(() => {
      expect(screen.getByText(/Total Landed Cost: €500.00/i)).toBeInTheDocument();
    });
  });

  test('supports bulk calculations', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock bulk calculation results
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        calculations: [
          {
            hts_code: '8471.30.01',
            tariff_rate: 0.0,
            tariff_amount: 0.0,
            total_landed_cost: 500.0
          },
          {
            hts_code: '8471.30.02',
            tariff_rate: 2.5,
            tariff_amount: 12.5,
            total_landed_cost: 512.5
          }
        ]
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Switch to bulk mode
    const bulkModeToggle = screen.getByLabelText(/bulk calculation mode/i);
    await user.click(bulkModeToggle);
    
    // Upload CSV file
    const fileInput = screen.getByLabelText(/upload csv file/i);
    const file = new File(['hts_code,material_cost\n8471.30.01,500\n8471.30.02,500'], 'test.csv', { type: 'text/csv' });
    await user.upload(fileInput, file);
    
    // Start bulk calculation
    const calculateButton = screen.getByRole('button', { name: /calculate bulk/i });
    await user.click(calculateButton);
    
    // Wait for bulk results
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
      expect(screen.getByText('8471.30.02')).toBeInTheDocument();
    });
  });

  test('exports calculation results', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0
      }
    });
    
    // Mock window.open
    const mockOpen = jest.fn();
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Perform calculation
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText(/Tariff Rate: 0.0%/i)).toBeInTheDocument();
    });
    
    // Export results
    const exportButton = screen.getByLabelText(/export results/i);
    await user.click(exportButton);
    
    // Verify export was triggered
    expect(mockOpen).toHaveBeenCalled();
  });

  test('shows calculation breakdown', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 2.5,
        tariff_amount: 12.5,
        total_landed_cost: 512.5,
        breakdown: {
          material_cost: 500.0,
          tariff_amount: 12.5,
          additional_fees: 0.0
        }
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Perform calculation
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Wait for breakdown
    await waitFor(() => {
      expect(screen.getByText(/Material Cost: \$500.00/i)).toBeInTheDocument();
      expect(screen.getByText(/Tariff Amount: \$12.50/i)).toBeInTheDocument();
      expect(screen.getByText(/Additional Fees: \$0.00/i)).toBeInTheDocument();
    });
  });

  test('responsive design works', () => {
    // Test mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Check if mobile-specific layout is applied
    const calculatorContainer = screen.getByTestId('tariff-calculator-container');
    expect(calculatorContainer).toBeInTheDocument();
  });

  test('accessibility features are present', () => {
    renderWithRouter(<TariffCalculator />);
    
    // Check for proper form labels
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    expect(htsCodeInput).toHaveAttribute('aria-label');
    
    // Check for proper button labels
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    expect(calculateButton).toHaveAttribute('aria-label');
    
    // Check for proper fieldset structure
    const fieldset = screen.getByRole('group');
    expect(fieldset).toBeInTheDocument();
  });

  test('keyboard navigation works', async () => {
    const user = userEvent.setup();
    renderWithRouter(<TariffCalculator />);
    
    // Test tab navigation through form fields
    await user.tab();
    
    const focusedElement = document.activeElement;
    expect(focusedElement).toBeInTheDocument();
    
    // Test form submission with Enter key
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01{enter}');
    
    // Verify form validation is triggered
    expect(screen.getByText(/Material Cost is required/i)).toBeInTheDocument();
  });
});

describe('Tariff Calculator Integration Tests', () => {
  test('full calculation workflow', async () => {
    const user = userEvent.setup();
    const { tariffService, htsService } = require('../../services/api');
    
    // Mock HTS search for autocomplete
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
    
    // Mock calculation result
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 0.0,
        tariff_amount: 0.0,
        total_landed_cost: 500.0
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // 1. Enter HTS code (with autocomplete)
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471');
    
    // Wait for autocomplete suggestions
    await waitFor(() => {
      expect(screen.getByText('8471.30.01')).toBeInTheDocument();
    });
    
    // Select suggestion
    const suggestion = screen.getByText('8471.30.01');
    await user.click(suggestion);
    
    // 2. Enter material cost
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    // 3. Select country
    const countrySelect = screen.getByLabelText(/Country of Origin/i);
    await user.selectOptions(countrySelect, 'US');
    
    // 4. Calculate
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // 5. Verify results
    await waitFor(() => {
      expect(screen.getByText(/Tariff Rate: 0.0%/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Landed Cost: \$500.00/i)).toBeInTheDocument();
    });
    
    // 6. Save calculation
    const saveButton = screen.getByLabelText(/save calculation/i);
    await user.click(saveButton);
    
    // 7. Verify save confirmation
    expect(screen.getByText(/Calculation saved/i)).toBeInTheDocument();
  });

  test('handles complex scenarios', async () => {
    const user = userEvent.setup();
    const { tariffService } = require('../../services/api');
    
    // Mock calculation with additional fees
    tariffService.calculateTariff.mockResolvedValue({
      data: {
        hts_code: '8471.30.01',
        tariff_rate: 2.5,
        tariff_amount: 12.5,
        total_landed_cost: 562.5,
        breakdown: {
          material_cost: 500.0,
          tariff_amount: 12.5,
          additional_fees: 50.0
        }
      }
    });
    
    renderWithRouter(<TariffCalculator />);
    
    // Fill in form with additional fees
    const htsCodeInput = screen.getByLabelText(/HTS Code/i);
    await user.type(htsCodeInput, '8471.30.01');
    
    const materialCostInput = screen.getByLabelText(/Material Cost/i);
    await user.type(materialCostInput, '500');
    
    const additionalFeesInput = screen.getByLabelText(/Additional Fees/i);
    await user.type(additionalFeesInput, '50');
    
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    await user.click(calculateButton);
    
    // Verify complex calculation
    await waitFor(() => {
      expect(screen.getByText(/Total Landed Cost: \$562.50/i)).toBeInTheDocument();
      expect(screen.getByText(/Additional Fees: \$50.00/i)).toBeInTheDocument();
    });
  });
});
