/**
 * __tests__/components/QualitySelector.test.tsx
 * Unit tests for QualitySelector component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QualitySelector from '../../components/VideoUpload/QualitySelector';

describe('QualitySelector Component', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  test('renders all quality options', () => {
    render(<QualitySelector value="medium" onChange={mockOnChange} />);

    expect(screen.getByText('Ultra Low')).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Ultra High')).toBeInTheDocument();
  });

  test('displays resolution for each quality', () => {
    render(<QualitySelector value="medium" onChange={mockOnChange} />);

    expect(screen.getByText('240p')).toBeInTheDocument();
    expect(screen.getByText('480p')).toBeInTheDocument();
    expect(screen.getByText('720p')).toBeInTheDocument();
    expect(screen.getByText('1080p')).toBeInTheDocument();
    expect(screen.getByText('4K')).toBeInTheDocument();
  });

  test('handles quality selection', () => {
    const { container } = render(<QualitySelector value="medium" onChange={mockOnChange} />);

    const lowButton = container.querySelector('[data-testid="quality-low"]') as HTMLElement;

    fireEvent.click(lowButton);

    expect(mockOnChange).toHaveBeenCalledWith('low');
  });

  test('shows selected quality as active', () => {
    const { container, rerender } = render(
      <QualitySelector value="medium" onChange={mockOnChange} />
    );

    let mediumButton = container.querySelector('[data-testid="quality-medium"]');
    expect(mediumButton).toHaveClass('selected');

    rerender(<QualitySelector value="high" onChange={mockOnChange} />);

    const highButton = container.querySelector('[data-testid="quality-high"]');
    expect(highButton).toHaveClass('selected');
  });

  test('displays quality descriptions', () => {
    render(<QualitySelector value="medium" onChange={mockOnChange} />);

    expect(screen.getByText(/Preview only/i)).toBeInTheDocument();
    expect(screen.getByText(/Mobile-friendly/i)).toBeInTheDocument();
    expect(screen.getByText(/Balanced/i)).toBeInTheDocument();
    expect(screen.getByText(/Evidence quality/i)).toBeInTheDocument();
    expect(screen.getByText(/Archival quality/i)).toBeInTheDocument();
  });

  test('shows speed indicators', () => {
    render(<QualitySelector value="medium" onChange={mockOnChange} />);

    expect(screen.getByText(/Very Fast/)).toBeInTheDocument();
    expect(screen.getByText(/Fast ⚡⚡/)).toBeInTheDocument();
    expect(screen.getByText(/Balanced ⚡/)).toBeInTheDocument();
    expect(screen.getByText('Slow')).toBeInTheDocument();
    expect(screen.getByText('Very Slow')).toBeInTheDocument();
  });
});
